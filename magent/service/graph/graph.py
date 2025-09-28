from __future__ import annotations

from typing import Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic as AgentState

from magent.service.graph.nodes import make_agent_node, make_should_continue

GRAPH_BUILDERS: dict[
    str, Callable[[BaseChatModel, list[BaseTool], ChatPromptTemplate], CompiledStateGraph]
] = {}


def register_graph(name: str):
    def decorator(
        func: Callable[
            [BaseChatModel, list[BaseTool], ChatPromptTemplate], CompiledStateGraph
        ],
    ):
        GRAPH_BUILDERS[name] = func
        return func

    return decorator


def graph_factory(
    llm: BaseChatModel,
    tools: list[BaseTool],
    prompt: ChatPromptTemplate,
    graph_type: str,
):
    if graph_type not in GRAPH_BUILDERS:
        raise ValueError(
            f"Unknown graph_type: {graph_type}. Available: {list(GRAPH_BUILDERS.keys())}"
        )
    return GRAPH_BUILDERS[graph_type](llm, tools, prompt)


@register_graph("custom_react")
def custom_react(llm: BaseChatModel, tools: list[BaseTool], prompt: ChatPromptTemplate):
    llm = prompt | llm.bind_tools(tools)
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)

    agent_node = make_agent_node(llm)
    should_continue = make_should_continue(tool_node)

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


@register_graph("prebuilt_react")
def prebuilt_react(
    llm: BaseChatModel, tools: list[BaseTool], prompt: ChatPromptTemplate
):
    return create_react_agent(llm, tools, prompt=prompt)
