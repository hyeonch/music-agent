from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from magent.container import AppContainer

router = APIRouter()
class ChatIn(BaseModel):
    text: str


class ChatOut(BaseModel):
    answer: str


@router.post("/", response_model=ChatOut)
@inject
async def chat(body: ChatIn, orchestrator=Depends(Provide[AppContainer.workflow.orchestrator])):
    result = await orchestrator.arun(body.text)
    return ChatOut(answer=result)