"""
Smart bank CSV normalizer.

Detects column layout from any major bank export and maps it to the
standard (date, description, amount) format our app expects.

Supported banks / formats:
  - Chase
  - Bank of America
  - Wells Fargo
  - Capital One   (separate Debit / Credit columns)
  - Citi          (separate Debit / Credit columns)
  - American Express
  - Generic / custom CSV
"""
from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime


# ── Column name dictionaries (lowercase) ─────────────────────────────────────

_DATE_NAMES = {
    "transaction date", "date", "posted date", "post date",
    "trans date", "value date", "settlement date", "posting date",
    "transaction_date",
}

_DESC_NAMES = {
    "description", "payee", "memo", "name", "merchant",
    "transaction description", "details", "narrative",
    "original description", "transaction detail", "reference",
}

_AMOUNT_NAMES = {
    "amount", "transaction amount", "trans amount",
    "net amount", "transaction amount (usd)",
}

_DEBIT_NAMES = {
    "debit", "withdrawal", "debit amount", "withdrawals",
    "money out", "charges",
}

_CREDIT_NAMES = {
    "credit", "deposit", "credit amount", "deposits",
    "money in", "payments",
}

# ── Date format patterns to try in order ─────────────────────────────────────

_DATE_FORMATS = [
    "%Y-%m-%d",   # 2024-01-15   (ISO — our native format)
    "%m/%d/%Y",   # 01/15/2024   (US common)
    "%m/%d/%y",   # 01/15/24     (US short)
    "%d/%m/%Y",   # 15/01/2024   (EU)
    "%d-%m-%Y",   # 15-01-2024
    "%m-%d-%Y",   # 01-15-2024
    "%b %d, %Y",  # Jan 15, 2024
    "%B %d, %Y",  # January 15, 2024
    "%d %b %Y",   # 15 Jan 2024
]


def _match_col(headers: list[str], names: set[str]) -> str | None:
    """Return the first header that matches one of the target names (case-insensitive)."""
    for h in headers:
        if h.strip().lower() in names:
            return h
    # Partial match fallback
    for h in headers:
        hl = h.strip().lower()
        if any(n in hl or hl in n for n in names):
            return h
    return None


def _parse_date(value: str) -> date:
    """Try multiple date formats and return a date object."""
    value = value.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {value!r}")


def _parse_amount(value: str) -> float:
    """Parse an amount string, stripping currency symbols and commas."""
    cleaned = re.sub(r"[,$£€\s]", "", value.strip())
    if not cleaned or cleaned in ("-", ""):
        return 0.0
    return float(cleaned)


class NormalizeResult:
    """Result returned by BankCSVNormalizer.normalize()."""

    def __init__(self, rows: list[dict], bank: str, skipped: int) -> None:
        self.rows = rows          # list of {"date": date, "description": str, "amount": float}
        self.bank = bank          # detected bank / format label
        self.skipped = skipped    # rows that couldn't be parsed


class BankCSVNormalizer:
    """
    Detects any major bank CSV layout and converts it to a uniform
    list of {"date", "description", "amount"} dicts.

    Usage:
        result = BankCSVNormalizer().normalize(raw_csv_text)
        result.rows   # normalized rows
        result.bank   # e.g. "Chase", "Capital One", "Generic"
    """

    def normalize(self, content: str) -> NormalizeResult:
        # Strip BOM that some banks add
        content = content.lstrip("\ufeff")

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            raise ValueError("CSV has no headers.")

        headers: list[str] = list(reader.fieldnames)
        rows_raw = list(reader)

        date_col = _match_col(headers, _DATE_NAMES)
        desc_col = _match_col(headers, _DESC_NAMES)
        amount_col = _match_col(headers, _AMOUNT_NAMES)
        debit_col = _match_col(headers, _DEBIT_NAMES)
        credit_col = _match_col(headers, _CREDIT_NAMES)

        if not date_col:
            raise ValueError(
                f"Could not find a date column. Headers found: {headers}. "
                "Rename your date column to 'date' or 'transaction date'."
            )
        if not desc_col:
            raise ValueError(
                f"Could not find a description column. Headers found: {headers}. "
                "Rename your description column to 'description' or 'payee'."
            )
        if not amount_col and not (debit_col or credit_col):
            raise ValueError(
                f"Could not find an amount column. Headers found: {headers}. "
                "Rename your amount column to 'amount', 'debit', or 'credit'."
            )

        # Detect bank label
        bank = self._detect_bank(headers)

        rows: list[dict] = []
        skipped = 0

        for raw in rows_raw:
            try:
                txn_date = _parse_date(raw[date_col])
                description = raw[desc_col].strip()
                if not description:
                    skipped += 1
                    continue

                # --- Amount resolution ---
                if amount_col:
                    amount = _parse_amount(raw[amount_col])
                    # Many banks use negative for expenses; take absolute value.
                    amount = abs(amount)
                else:
                    # Separate debit / credit columns (Capital One, Citi style)
                    debit_val = _parse_amount(raw.get(debit_col, "") or "") if debit_col else 0.0
                    credit_val = _parse_amount(raw.get(credit_col, "") or "") if credit_col else 0.0
                    # Treat debits as expenses; credits (payments/deposits) get 0 amount
                    amount = debit_val if debit_val else credit_val

                if amount == 0.0:
                    skipped += 1
                    continue

                rows.append({
                    "date": txn_date,
                    "description": description,
                    "amount": round(amount, 2),
                })

            except Exception:
                skipped += 1
                continue

        return NormalizeResult(rows=rows, bank=bank, skipped=skipped)

    @staticmethod
    def _detect_bank(headers: list[str]) -> str:
        hl = {h.lower() for h in headers}
        if "transaction date" in hl and "post date" in hl and "memo" in hl:
            return "Chase"
        if "posted date" in hl and "reference number" in hl:
            return "Bank of America"
        if "card no." in hl or "card no" in hl:
            return "Capital One"
        if "status" in hl and "debit" in hl and "credit" in hl:
            return "Citi"
        if any("extended details" in h for h in hl):
            return "American Express"
        if len(headers) >= 5 and headers[2] == "*":
            return "Wells Fargo"
        return "Generic"
