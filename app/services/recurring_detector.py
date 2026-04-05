from __future__ import annotations

import re
import sqlite3
from collections import defaultdict

from app.models.schemas import RecurringTransaction


class RecurringDetector:
    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _normalize(self, description: str) -> str:
        text = re.sub(r"\d+", "", description.lower())
        text = re.sub(r"[^a-z\s]", "", text)
        return " ".join(text.split())

    def detect(self, user_id: str = "default") -> list[RecurringTransaction]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT description, amount, category FROM transactions WHERE user_id = ? ORDER BY date",
                (user_id,)
            ).fetchall()

        groups: dict[str, list[dict]] = defaultdict(list)
        for desc, amount, category in rows:
            key = self._normalize(desc)
            if key:
                groups[key].append({"description": desc, "amount": amount, "category": category})

        recurring: list[RecurringTransaction] = []
        for key, entries in groups.items():
            if len(entries) < 2:
                continue
            amounts = [e["amount"] for e in entries]
            avg_amount = sum(amounts) / len(amounts)
            if avg_amount > 0:
                variance = max(abs(a - avg_amount) / avg_amount for a in amounts)
                if variance > 0.20:
                    continue
            desc = max(set(e["description"] for e in entries), key=lambda d: sum(1 for e in entries if e["description"] == d))
            category = max(set(e["category"] for e in entries), key=lambda c: sum(1 for e in entries if e["category"] == c))
            recurring.append(RecurringTransaction(
                description=desc, average_amount=round(avg_amount, 2),
                occurrences=len(entries), category=category, likely_monthly=2 <= len(entries) <= 13,
            ))

        return sorted(recurring, key=lambda r: r.average_amount, reverse=True)
