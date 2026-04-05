from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    return request.app.state.agent.chat(req.message)


@router.delete("/memory")
async def clear_memory(request: Request) -> dict:
    request.app.state.agent.clear_memory()
    return {"message": "Memory cleared successfully."}
