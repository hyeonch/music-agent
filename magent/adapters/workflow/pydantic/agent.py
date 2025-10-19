from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from magent.adapters.workflow.pydantic.prompts import RECOMMENDATION_AGENT_SYSTEM_PROMPT
from magent.service.usecases.recommend.dto import (
    RecommendByArtistRequest,
    RecommendResponse,
    RecommendByTrackRequest,
)
from magent.service.usecases.recommend.recommend import RecommendationService


@dataclass
class RecommendationDeps:
    service: RecommendationService


def create_recommendation_agent(
    model: Model,
) -> Agent[RecommendationDeps, RecommendResponse]:
    Agent.instrument_all()
    recommendation_agent = Agent[RecommendationDeps, RecommendResponse](
        model=model,
        system_prompt=RECOMMENDATION_AGENT_SYSTEM_PROMPT,
        instrument=True,
    )

    @recommendation_agent.tool(name="recommend_by_artist")
    async def recommend_by_artist(
        ctx: RunContext[RecommendationDeps], req: RecommendByArtistRequest
    ) -> RecommendResponse:
        result = await ctx.deps.service.recommend_by_artist_name(req)
        return result

    @recommendation_agent.tool(name="recommend_by_track")
    async def recommend_by_track(
        ctx: RunContext[RecommendationDeps], req: RecommendByTrackRequest
    ) -> RecommendResponse:
        result = await ctx.deps.service.recommend_by_track(req)
        return result

    return recommendation_agent
