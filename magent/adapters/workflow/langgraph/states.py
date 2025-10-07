from typing import Any

from langchain_core.messages import BaseMessage
from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic
from pydantic import Field


class AgentState(AgentStatePydantic):
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_messages(self, messages: list[BaseMessage]):
        self.messages.extend(messages)
        return self
