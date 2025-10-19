from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.constants import END
from langgraph.types import Send

from magent.adapters.workflow.langgraph.states import AgentState


def make_agent_node(llm: Runnable):
    def _are_more_steps_needed(state: AgentState, response: BaseMessage) -> bool:
        has_tool_calls = isinstance(response, AIMessage) and response.tool_calls
        if state.remaining_steps < 2 and has_tool_calls:
            return True
        return False

    async def agent_node(state: AgentState) -> AgentState:
        response = await llm.ainvoke(state.messages)
        if _are_more_steps_needed(state, response):
            response = AIMessage(
                id=response.id,
                content="Sorry, need more steps to process this request.",
            )
        return state.add_messages([response])

    return agent_node


def make_conditional_router():
    def should_continue(state: AgentState):
        last_msg = state.messages[-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return Send("tools", state)
        return END

    return should_continue


def make_tool_node(tools: list[BaseTool]):
    tool_map = {tool.name: tool for tool in tools}

    async def tool_node(state: AgentState) -> AgentState:
        last_msg = state.messages[-1]
        results = []

        for call in last_msg.tool_calls:
            tool_name = call.get("name")
            args = call.get("args", {})
            tool_id = call.get("id")

            tool = tool_map.get(tool_name)
            if tool is None:
                results.append(
                    ToolMessage(
                        content=f"Tool `{tool_name}` not found.",
                        tool_call_id=tool_id,
                    )
                )
                continue

            try:
                if hasattr(tool, "arun"):
                    result = await tool.arun(args)
                elif hasattr(tool, "ainvoke"):
                    result = await tool.ainvoke(args)
                elif hasattr(tool, "invoke"):
                    result = tool.invoke(args)
                else:
                    result = tool.run(args)

                results.append(
                    ToolMessage(
                        content=str(result.model_dump_json()),
                        tool_call_id=tool_id,
                    )
                )

            except Exception as e:
                results.append(
                    ToolMessage(
                        content=f"Error in `{tool_name}`: {e}",
                        tool_call_id=tool_id,
                    )
                )
        return state.add_messages(results)

    return tool_node
