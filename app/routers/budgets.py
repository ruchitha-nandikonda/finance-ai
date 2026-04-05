from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, Request

from app.models.schemas import Budget, BudgetStatus

router = APIRouter(tags=["budgets"])


def _uid(x_user_id: Optional[str]) -> str:
    return x_user_id or "default"


@router.post("/budgets", response_model=Budget)
async def set_budget(
    request: Request, category: str, monthly_limit: float,
    x_user_id: Optional[str] = Header(default=None),
) -> Budget:
    return request.app.state.budget_service.set_budget(category, monthly_limit, user_id=_uid(x_user_id))


@router.get("/budgets", response_model=list[Budget])
async def get_budgets(request: Request, x_user_id: Optional[str] = Header(default=None)) -> list[Budget]:
    return request.app.state.budget_service.get_budgets(user_id=_uid(x_user_id))


@router.delete("/budgets/{category}")
async def delete_budget(
    category: str, request: Request, x_user_id: Optional[str] = Header(default=None)
) -> dict:
    deleted = request.app.state.budget_service.delete_budget(category, user_id=_uid(x_user_id))
    return {"deleted": deleted}


@router.get("/budgets/status", response_model=list[BudgetStatus])
async def budget_status(request: Request, x_user_id: Optional[str] = Header(default=None)) -> list[BudgetStatus]:
    statuses = request.app.state.budget_service.get_budget_status(user_id=_uid(x_user_id))
    request.app.state.alert_service.check_and_alert(statuses)
    return statuses
