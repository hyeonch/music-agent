from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.stores import BaseStore
from langgraph.constants import END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic as AgentState
from langgraph.types import Send

from magent.logger import logger


def make_agent_node(llm: Runnable):
    def _are_more_steps_needed(state: AgentState, response: BaseMessage) -> bool:
        has_tool_calls = isinstance(response, AIMessage) and response.tool_calls
        if state.remaining_steps < 2 and has_tool_calls:
            return True
        return False
    
    async def agent_node(state: AgentState):
        logger.info("llm_node.start", messages=state.messages[-1])
        response = await llm.ainvoke(state.messages)
        logger.info("llm_node.end", response=str(response))
        if _are_more_steps_needed(state, response):
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="Sorry, need more steps to process this request.",
                    )
                ]
            }
        return {"messages": [response]}

    return agent_node


def make_should_continue(tool_node: ToolNode, store: BaseStore | None = None):
    def should_continue(state: AgentState):
        last_msg = state.messages[-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            tool_calls = [
                tool_node.inject_tool_args(call, state, store)
                for call in last_msg.tool_calls
            ]
            return [Send("tools", [tool_call]) for tool_call in tool_calls]
        return END

    return should_continue
