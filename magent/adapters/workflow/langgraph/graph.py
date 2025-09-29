from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic as AgentState

from magent.adapters.workflow.langgraph.nodes import make_agent_node, make_should_continue
from magent.service.graph.workflow import WorkflowOrchestrator


class LangGraphOrchestrator(WorkflowOrchestrator):
    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph
    
    def run(self, query: str):
        results = self.graph.invoke(AgentState(messages=[HumanMessage(content=query)]))
        return results["messages"][-1].content
    
    async def arun(self, query: str):
        results = await self.graph.ainvoke(AgentState(messages=[HumanMessage(content=query)]))
        return results["messages"][-1].content


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


def prebuilt_react(
        llm: BaseChatModel, tools: list[BaseTool], prompt: ChatPromptTemplate
):
    return create_react_agent(llm, tools, prompt=prompt)
