from __future__ import annotations

import sqlite3
import uuid
from datetime import date

from app.models.schemas import Budget, BudgetStatus


class BudgetService:
    """CRUD for monthly budgets per category, isolated per user."""

    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    monthly_limit REAL NOT NULL,
                    user_id TEXT NOT NULL DEFAULT 'default',
                    UNIQUE(category, user_id)
                )
            """)
            try:
                conn.execute("ALTER TABLE budgets ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default'")
            except sqlite3.OperationalError:
                pass

    def set_budget(self, category: str, monthly_limit: float, user_id: str = "default") -> Budget:
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM budgets WHERE category = ? AND user_id = ?", (category, user_id)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE budgets SET monthly_limit = ? WHERE category = ? AND user_id = ?",
                    (monthly_limit, category, user_id),
                )
                return Budget(id=existing[0], category=category, monthly_limit=monthly_limit)
            else:
                bid = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO budgets VALUES (?, ?, ?, ?)",
                    (bid, category, monthly_limit, user_id),
                )
                return Budget(id=bid, category=category, monthly_limit=monthly_limit)

    def get_budgets(self, user_id: str = "default") -> list[Budget]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, category, monthly_limit FROM budgets WHERE user_id = ?", (user_id,)
            ).fetchall()
        return [Budget(id=r[0], category=r[1], monthly_limit=r[2]) for r in rows]

    def delete_budget(self, category: str, user_id: str = "default") -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM budgets WHERE category = ? AND user_id = ?", (category, user_id)
            )
            return cursor.rowcount > 0

    def get_budget_status(self, user_id: str = "default") -> list[BudgetStatus]:
        budgets = self.get_budgets(user_id=user_id)
        if not budgets:
            return []
        start_of_month = date.today().replace(day=1).isoformat()
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT category, SUM(amount)
                FROM transactions
                WHERE date >= ? AND user_id = ?
                GROUP BY category
            """, (start_of_month, user_id)).fetchall()
        spent_by_cat = {r[0]: r[1] for r in rows}
        statuses: list[BudgetStatus] = []
        for budget in budgets:
            spent = spent_by_cat.get(budget.category, 0.0)
            remaining = budget.monthly_limit - spent
            pct = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
            status = "over" if pct >= 100 else "warning" if pct >= 80 else "ok"
            statuses.append(BudgetStatus(
                category=budget.category,
                monthly_limit=budget.monthly_limit,
                spent=round(spent, 2),
                remaining=round(remaining, 2),
                percentage=round(pct, 1),
                status=status,
            ))
        return statuses
