from __future__ import annotations

import sqlite3
import uuid
from datetime import date

from app.models.schemas import SavingsGoal


class SavingsService:
    """CRUD for savings goals, isolated per user."""

    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    deadline TEXT,
                    created_at TEXT NOT NULL,
                    user_id TEXT NOT NULL DEFAULT 'default'
                )
            """)
            try:
                conn.execute("ALTER TABLE savings_goals ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default'")
            except sqlite3.OperationalError:
                pass

    def create_goal(self, name: str, target_amount: float, current_amount: float = 0.0,
                    deadline: str | None = None, user_id: str = "default") -> SavingsGoal:
        gid = str(uuid.uuid4())
        pct = (current_amount / target_amount * 100) if target_amount > 0 else 0
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO savings_goals VALUES (?, ?, ?, ?, ?, ?, ?)",
                (gid, name, target_amount, current_amount, deadline, date.today().isoformat(), user_id),
            )
        return SavingsGoal(id=gid, name=name, target_amount=target_amount,
                           current_amount=current_amount, deadline=deadline, percentage=round(pct, 1))

    def get_goals(self, user_id: str = "default") -> list[SavingsGoal]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, target_amount, current_amount, deadline FROM savings_goals WHERE user_id = ?",
                (user_id,)
            ).fetchall()
        goals = []
        for r in rows:
            pct = (r[3] / r[2] * 100) if r[2] > 0 else 0
            goals.append(SavingsGoal(id=r[0], name=r[1], target_amount=r[2],
                                     current_amount=r[3], deadline=r[4], percentage=round(pct, 1)))
        return goals

    def update_goal(self, goal_id: str, current_amount: float, user_id: str = "default") -> SavingsGoal | None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE savings_goals SET current_amount = ? WHERE id = ? AND user_id = ?",
                (current_amount, goal_id, user_id),
            )
            row = conn.execute(
                "SELECT id, name, target_amount, current_amount, deadline FROM savings_goals WHERE id = ?",
                (goal_id,)
            ).fetchone()
        if not row:
            return None
        pct = (row[3] / row[2] * 100) if row[2] > 0 else 0
        return SavingsGoal(id=row[0], name=row[1], target_amount=row[2],
                           current_amount=row[3], deadline=row[4], percentage=round(pct, 1))

    def delete_goal(self, goal_id: str, user_id: str = "default") -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM savings_goals WHERE id = ? AND user_id = ?", (goal_id, user_id)
            )
            return cursor.rowcount > 0
