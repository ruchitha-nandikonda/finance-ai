from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["auth"])


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    username: str
    email: str


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(req: SignupRequest, request: Request) -> AuthResponse:
    result = request.app.state.auth_service.signup(req.username, req.email, req.password)
    if isinstance(result, str):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result)
    return AuthResponse(user_id=result.id, username=result.username, email=result.email)


@router.post("/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest, request: Request) -> AuthResponse:
    result = request.app.state.auth_service.login(req.username, req.password)
    if isinstance(result, str):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail=result)
    return AuthResponse(user_id=result.id, username=result.username, email=result.email)
