from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import date, timedelta

from app.models.schemas import Transaction
from app.services.csv_normalizer import BankCSVNormalizer, NormalizeResult
from app.services.plaid_client import BaseTransactionSource


class CsvImporter(BaseTransactionSource):
    """CSV-based transaction source backed by SQLite, isolated per user."""

    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path) or ".", exist_ok=True)
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT DEFAULT 'other',
                    source TEXT DEFAULT 'csv',
                    user_id TEXT DEFAULT 'default'
                )
            """)
            # Add user_id column to existing DBs that don't have it
            try:
                conn.execute("ALTER TABLE transactions ADD COLUMN user_id TEXT DEFAULT 'default'")
            except sqlite3.OperationalError:
                pass

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def import_csv(self, file_content: str) -> tuple[list[Transaction], NormalizeResult]:
        result = BankCSVNormalizer().normalize(file_content)
        transactions: list[Transaction] = [
            Transaction(
                id=str(uuid.uuid4()),
                date=row["date"],
                description=row["description"],
                amount=row["amount"],
                category="other",
                source="csv",
            )
            for row in result.rows
        ]
        return transactions, result

    def add_transaction(self, amount: float, description: str, category: str = "other", user_id: str = "default") -> Transaction:
        txn = Transaction(
            id=str(uuid.uuid4()),
            date=date.today(),
            description=description,
            amount=amount,
            category=category,
            source="manual",
        )
        self.save_transactions([txn], user_id=user_id)
        return txn

    def save_transactions(self, transactions: list[Transaction], user_id: str = "default") -> None:
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO transactions VALUES (?,?,?,?,?,?,?)",
                [(t.id, t.date.isoformat(), t.description, t.amount, t.category, t.source, user_id)
                 for t in transactions],
            )

    def fetch(self, days: int = 30, user_id: str = "default") -> list[Transaction]:
        return self.get_transactions(days=days, user_id=user_id)

    def get_transactions(
        self,
        days: int | None = None,
        category: str | None = None,
        min_amount: float | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        user_id: str = "default",
    ) -> list[Transaction]:
        query = "SELECT id, date, description, amount, category, source FROM transactions WHERE user_id = ?"
        params: list = [user_id]
        if days:
            cutoff = (date.today() - timedelta(days=days)).isoformat()
            query += " AND date >= ?"
            params.append(cutoff)
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        if category:
            query += " AND category = ?"
            params.append(category)
        if min_amount is not None:
            query += " AND amount >= ?"
            params.append(min_amount)
        query += " ORDER BY date DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            Transaction(id=r[0], date=date.fromisoformat(r[1]),
                        description=r[2], amount=r[3], category=r[4], source=r[5])
            for r in rows
        ]

    def delete_transaction(self, transaction_id: str, user_id: str = "default") -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)
            )
            return cursor.rowcount > 0
