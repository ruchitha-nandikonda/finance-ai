from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request

from app.models.schemas import SavingsGoal, SavingsGoalCreate, SavingsGoalUpdate

router = APIRouter(tags=["savings"])


def _uid(x_user_id: Optional[str]) -> str:
    return x_user_id or "default"


@router.post("/savings", response_model=SavingsGoal)
async def create_goal(
    req: SavingsGoalCreate, request: Request, x_user_id: Optional[str] = Header(default=None)
) -> SavingsGoal:
    return request.app.state.savings_service.create_goal(
        name=req.name, target_amount=req.target_amount,
        current_amount=req.current_amount, deadline=req.deadline, user_id=_uid(x_user_id),
    )


@router.get("/savings", response_model=list[SavingsGoal])
async def get_goals(request: Request, x_user_id: Optional[str] = Header(default=None)) -> list[SavingsGoal]:
    return request.app.state.savings_service.get_goals(user_id=_uid(x_user_id))


@router.patch("/savings/{goal_id}", response_model=SavingsGoal)
async def update_goal(
    goal_id: str, req: SavingsGoalUpdate, request: Request, x_user_id: Optional[str] = Header(default=None)
) -> SavingsGoal:
    goal = request.app.state.savings_service.update_goal(goal_id, req.current_amount, user_id=_uid(x_user_id))
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/savings/{goal_id}")
async def delete_goal(
    goal_id: str, request: Request, x_user_id: Optional[str] = Header(default=None)
) -> dict:
    deleted = request.app.state.savings_service.delete_goal(goal_id, user_id=_uid(x_user_id))
    return {"deleted": deleted}
