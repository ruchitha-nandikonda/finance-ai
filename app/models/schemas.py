from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    id: str
    date: date
    description: str
    amount: float
    category: str = "other"
    source: str = "csv"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    memory_context: Optional[list[str]] = Field(default=None)


class WeeklyInsight(BaseModel):
    summary: str
    top_categories: list[dict]
    total_spent: float
    period: str


class SyncResponse(BaseModel):
    imported_count: int
    message: str


class HealthResponse(BaseModel):
    status: str


# --- Budget ---

class Budget(BaseModel):
    id: str
    category: str
    monthly_limit: float


class BudgetStatus(BaseModel):
    category: str
    monthly_limit: float
    spent: float
    remaining: float
    percentage: float
    status: str  # "ok", "warning" (>80%), "over" (>100%)


# --- Savings Goals ---

class SavingsGoal(BaseModel):
    id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[str] = None
    percentage: float = 0.0


class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[str] = None


class SavingsGoalUpdate(BaseModel):
    current_amount: float


# --- Analytics ---

class TrendPoint(BaseModel):
    period: str  # "2026-01"
    total: float
    by_category: dict[str, float]


class ForecastResult(BaseModel):
    next_month_total: float
    by_category: dict[str, float]
    basis: str


class RecurringTransaction(BaseModel):
    description: str
    average_amount: float
    occurrences: int
    category: str
    likely_monthly: bool


# --- Receipt ---

class ReceiptScanResult(BaseModel):
    amount: float
    description: str
    category: str
    date: str
