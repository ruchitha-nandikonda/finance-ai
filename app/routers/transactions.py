from __future__ import annotations

import csv
import io
from typing import Optional

from fastapi import APIRouter, File, Header, Query, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.models.schemas import ReceiptScanResult, SyncResponse, Transaction

router = APIRouter(tags=["transactions"])


def _uid(x_user_id: Optional[str]) -> str:
    return x_user_id or "default"


@router.post("/sync", response_model=SyncResponse)
async def sync_transactions(
    request: Request,
    file: UploadFile = File(...),
    x_user_id: Optional[str] = Header(default=None),
) -> SyncResponse:
    user_id = _uid(x_user_id)
    importer = request.app.state.csv_importer
    categorizer = request.app.state.categorizer
    content = (await file.read()).decode("utf-8")
    transactions, meta = importer.import_csv(content)
    for txn in transactions:
        try:
            txn.category = categorizer.categorize(txn.description)
        except Exception:
            pass
    importer.save_transactions(transactions, user_id=user_id)
    return SyncResponse(
        imported_count=len(transactions),
        message=f"Detected: {meta.bank} format. Imported {len(transactions)} transactions. Skipped {meta.skipped} rows.",
    )


@router.post("/transactions/add", response_model=Transaction)
async def add_transaction(
    request: Request,
    amount: float = Query(...),
    description: str = Query(...),
    category: str = Query(default="other"),
    x_user_id: Optional[str] = Header(default=None),
) -> Transaction:
    user_id = _uid(x_user_id)
    categorizer = request.app.state.categorizer
    if category == "other":
        try:
            category = categorizer.categorize(description)
        except Exception:
            pass
    return request.app.state.csv_importer.add_transaction(
        amount=amount, description=description, category=category, user_id=user_id
    )


@router.get("/transactions", response_model=list[Transaction])
async def get_transactions(
    request: Request,
    days: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(default=None),
) -> list[Transaction]:
    return request.app.state.csv_importer.get_transactions(
        days=days, category=category, min_amount=min_amount,
        date_from=date_from, date_to=date_to, user_id=_uid(x_user_id),
    )


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    request: Request,
    x_user_id: Optional[str] = Header(default=None),
) -> dict:
    deleted = request.app.state.csv_importer.delete_transaction(transaction_id, user_id=_uid(x_user_id))
    return {"deleted": deleted}


@router.get("/transactions/export")
async def export_transactions(
    request: Request,
    days: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(default=None),
) -> StreamingResponse:
    transactions = request.app.state.csv_importer.get_transactions(
        days=days, category=category, user_id=_uid(x_user_id)
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "description", "amount", "category", "source"])
    for t in transactions:
        writer.writerow([t.id, t.date, t.description, t.amount, t.category, t.source])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.post("/transactions/scan-receipt", response_model=ReceiptScanResult)
async def scan_receipt(request: Request, file: UploadFile = File(...)) -> ReceiptScanResult:
    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"
    return request.app.state.receipt_scanner.scan(image_bytes, mime_type)
