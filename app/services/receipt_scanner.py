from __future__ import annotations

import base64
from datetime import date

from openai import OpenAI

from app.core.config import Settings
from app.models.schemas import ReceiptScanResult


class ReceiptScanner:
    """Extracts transaction data from receipt images using GPT Vision."""

    def __init__(self, config: Settings) -> None:
        self._client = OpenAI(api_key=config.openai_api_key)
        self._model = config.chat_model

    def scan(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> ReceiptScanResult:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        prompt = (
            "Extract the following from this receipt image and respond ONLY in this exact format:\n"
            "AMOUNT: <number only, e.g. 45.50>\n"
            "DESCRIPTION: <merchant or store name>\n"
            "CATEGORY: <one of: food, transport, entertainment, bills, shopping, health, other>\n"
            "DATE: <YYYY-MM-DD, or today if not visible>\n\n"
            "If you cannot read the receipt clearly, make your best guess."
        )

        response = self._client.chat.completions.create(
            model="gpt-4o",  # Vision requires gpt-4o
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    ],
                }
            ],
            max_tokens=100,
        )

        text = response.choices[0].message.content or ""
        return self._parse_response(text)

    def _parse_response(self, text: str) -> ReceiptScanResult:
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                 for line in text.strip().splitlines() if ":" in line}

        try:
            amount = float(lines.get("AMOUNT", "0").replace("$", "").replace(",", ""))
        except ValueError:
            amount = 0.0

        description = lines.get("DESCRIPTION", "Receipt scan")
        category = lines.get("CATEGORY", "other").lower()
        valid = {"food", "transport", "entertainment", "bills", "shopping", "health", "other"}
        if category not in valid:
            category = "other"

        raw_date = lines.get("DATE", "").strip()
        try:
            date.fromisoformat(raw_date)
            txn_date = raw_date
        except ValueError:
            txn_date = date.today().isoformat()

        return ReceiptScanResult(amount=amount, description=description, category=category, date=txn_date)
