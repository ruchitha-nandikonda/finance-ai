from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import date

from app.models.schemas import ForecastResult


class Forecaster:
    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def forecast(self, user_id: str = "default") -> ForecastResult:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT date, amount, category FROM transactions WHERE user_id = ? ORDER BY date",
                (user_id,)
            ).fetchall()

        if not rows:
            return ForecastResult(next_month_total=0.0, by_category={}, basis="No data available.")

        by_month: dict[str, float] = defaultdict(float)
        by_month_category: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for txn_date, amount, category in rows:
            month = txn_date[:7]
            by_month[month] += amount
            by_month_category[month][category] += amount

        months = sorted(by_month.keys())
        current_month = date.today().strftime("%Y-%m")
        complete_months = [m for m in months if m != current_month]

        if not complete_months:
            return ForecastResult(next_month_total=0.0, by_category={}, basis="Not enough historical data.")

        lookback = complete_months[-3:]
        avg_total = sum(by_month[m] for m in lookback) / len(lookback)

        all_categories: set[str] = set()
        for m in lookback:
            all_categories.update(by_month_category[m].keys())

        by_cat = {
            cat: round(sum(by_month_category[m].get(cat, 0.0) for m in lookback) / len(lookback), 2)
            for cat in all_categories
        }
        by_cat = {k: v for k, v in by_cat.items() if v > 0}

        return ForecastResult(
            next_month_total=round(avg_total, 2),
            by_category=by_cat,
            basis=f"Based on last {len(lookback)} month(s) ({', '.join(lookback)})",
        )

    def get_trends(self, user_id: str = "default") -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT date, amount, category FROM transactions WHERE user_id = ? ORDER BY date",
                (user_id,)
            ).fetchall()

        by_month: dict[str, dict] = {}
        for txn_date, amount, category in rows:
            month = txn_date[:7]
            if month not in by_month:
                by_month[month] = {"period": month, "total": 0.0, "by_category": defaultdict(float)}
            by_month[month]["total"] += amount
            by_month[month]["by_category"][category] += amount

        return [
            {"period": m, "total": round(by_month[m]["total"], 2),
             "by_category": {k: round(v, 2) for k, v in by_month[m]["by_category"].items()}}
            for m in sorted(by_month.keys())
        ]
