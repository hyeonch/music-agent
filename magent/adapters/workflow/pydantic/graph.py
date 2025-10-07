from typing import Any
from pydantic_ai import Agent

from magent.adapters.workflow.pydantic.agent import RecommendationDeps
from magent.service.graph.workflow import WorkflowOrchestrator
from magent.service.trace.tracer import trace
from magent.service.usecases.recommend.recommend import RecommendationService


class PydanticGraphOrchestrator(WorkflowOrchestrator):
    def __init__(self, agent: Agent, recommendation: RecommendationService):
        self.agent = agent
        self.recommendation = recommendation

    def run(
        self, user_id: str, session_id: str, query: str, meta: dict[str, Any]
    ) -> str:
        import asyncio

        return asyncio.run(self.arun(user_id, session_id, query, meta))

    @trace(name="orchestrator", as_type="agent")
    async def arun(
        self, user_id: str, session_id: str, query: str, meta: dict[str, Any]
    ) -> str:
        deps = RecommendationDeps(service=self.recommendation)

        response = await self.agent.run(query, deps=deps)
        return response.output
