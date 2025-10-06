from typing import Any

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from magent.container import AppContainer

router = APIRouter()


class ChatIn(BaseModel):
    user_id: str
    session_id: str
    text: str
    meta: dict[str, Any] = Field(default_factory=dict)


class ChatOut(BaseModel):
    text: str


@router.post("/", response_model=ChatOut)
@inject
async def chat(
    body: ChatIn, orchestrator=Depends(Provide[AppContainer.workflow.orchestrator])
):
    result = await orchestrator.arun(
        user_id=body.user_id,
        session_id=body.session_id,
        query=body.text,
        meta=body.meta,
    )
    return ChatOut(text=result)
