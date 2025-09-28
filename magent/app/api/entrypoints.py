from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from magent.container import AppContainer

router = APIRouter()
class ChatIn(BaseModel):
    text: str


class ChatOut(BaseModel):
    answer: str


@router.post("/", response_model=ChatOut)
@inject
async def chat(body: ChatIn, graph=Depends(Provide[AppContainer.graph.graph])):
    result = await graph.ainvoke({"messages": [HumanMessage(content=body.text)]})
    return ChatOut(answer=result["messages"][-1].content)