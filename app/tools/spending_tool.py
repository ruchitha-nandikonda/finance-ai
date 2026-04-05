from __future__ import annotations

from collections import defaultdict

from app.services.plaid_client import BaseTransactionSource


class SpendingTool:
    """Queries and aggregates transaction data (SRP)."""

    def __init__(self, transaction_source: BaseTransactionSource) -> None:
        self._source = transaction_source

    def run(self, days: int = 30, category: str | None = None, keyword: str | None = None) -> str:
        transactions = self._source.fetch(days=days)
        if category:
            transactions = [t for t in transactions if t.category.lower() == category.lower()]
        if keyword:
            transactions = [t for t in transactions if keyword.lower() in t.description.lower()]
        if not transactions:
            filter_desc = f"category '{category}'" if category else (f"keyword '{keyword}'" if keyword else f"last {days} days")
            return f"No transactions found for {filter_desc}."

        total = sum(t.amount for t in transactions)
        by_category: dict[str, float] = defaultdict(float)
        for t in transactions:
            by_category[t.category] += t.amount

        lines = [f"Spending summary (last {days} days):"]
        lines.append(f"  Total: ${total:,.2f}")
        lines.append(f"  Transactions: {len(transactions)}")
        lines.append("  By category:")
        for cat, amt in sorted(by_category.items(), key=lambda x: -x[1]):
            lines.append(f"    {cat}: ${amt:,.2f}")

        # Always include individual transaction details so the agent can answer date/description questions
        lines.append("  Individual transactions:")
        for t in sorted(transactions, key=lambda x: x.date, reverse=True):
            lines.append(f"    [{t.date}] {t.description} — ${t.amount:,.2f} ({t.category})")
        return "\n".join(lines)
