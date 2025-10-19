from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from magent.adapters.workflow.langgraph.nodes import (
    make_agent_node,
    make_tool_node,
    make_conditional_router,
)
from magent.adapters.workflow.langgraph.states import AgentState
from magent.service.graph.workflow import WorkflowOrchestrator
from magent.service.trace.tracer import get_tracer, trace


class LangGraphOrchestrator(WorkflowOrchestrator):
    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph

    def run(self, user_id: str, session_id: str, query: str, meta: dict[str, Any]):
        callbacks = get_tracer().callbacks(graph=self.graph)
        results = self.graph.invoke(
            AgentState(messages=[HumanMessage(content=query)], metadata=meta),
            config={"callbacks": callbacks},
        )
        return results["messages"][-1].content

    @trace(name="orchestrator")
    async def arun(
        self, user_id: str, session_id: str, query: str, meta: dict[str, Any]
    ):
        callbacks = get_tracer().callbacks(graph=self.graph)
        results = await self.graph.ainvoke(
            AgentState(messages=[HumanMessage(content=query)], metadata=meta),
            config={"callbacks": callbacks, "configurable": {"thread_id": session_id}},
        )
        answer = results["messages"][-1].content
        return answer


def custom_react(
    llm: BaseChatModel,
    tools: list[BaseTool],
    prompt: ChatPromptTemplate,
):
    llm = prompt | llm.bind_tools(tools)
    graph = StateGraph(AgentState)

    agent_node = make_agent_node(llm)
    tool_node = make_tool_node(tools)
    should_continue = make_conditional_router()

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges(
        "agent",
        should_continue,
        path_map=["tools", END],
    )
    graph.add_edge("tools", "agent")
    graph.set_entry_point("agent")

    return graph.compile()


def prebuilt_react(
    llm: BaseChatModel,
    tools: list[BaseTool],
    prompt: ChatPromptTemplate,
):
    return create_react_agent(llm, tools, prompt=prompt)
