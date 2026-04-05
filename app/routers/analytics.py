from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, Request

from app.models.schemas import ForecastResult, RecurringTransaction

router = APIRouter(tags=["analytics"])


def _uid(x_user_id: Optional[str]) -> str:
    return x_user_id or "default"


@router.get("/analytics/trends")
async def get_trends(request: Request, x_user_id: Optional[str] = Header(default=None)) -> list[dict]:
    return request.app.state.forecaster.get_trends(user_id=_uid(x_user_id))


@router.get("/analytics/forecast", response_model=ForecastResult)
async def get_forecast(request: Request, x_user_id: Optional[str] = Header(default=None)) -> ForecastResult:
    return request.app.state.forecaster.forecast(user_id=_uid(x_user_id))


@router.get("/analytics/recurring", response_model=list[RecurringTransaction])
async def get_recurring(request: Request, x_user_id: Optional[str] = Header(default=None)) -> list[RecurringTransaction]:
    return request.app.state.recurring_detector.detect(user_id=_uid(x_user_id))
