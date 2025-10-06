from langchain_core.tools import tool, BaseTool

from magent.service.usecases.recommend.dto import (
    RecommendByArtistRequest,
    RecommendResponse,
    RecommendByTrackRequest,
)
from magent.service.usecases.recommend.recommend import RecommendationService


def make_tools(service: RecommendationService) -> list[BaseTool]:
    @tool(
        "recommend_by_artist",
        args_schema=RecommendByArtistRequest,
        description="Recommend tracks by artist name",
    )
    async def recommend_by_artist(artist_name: str, limit: int) -> RecommendResponse:
        req = RecommendByArtistRequest(artist_name=artist_name, limit=limit)
        result = await service.recommend_by_artist_name(req)
        return result

    @tool(
        "recommend_by_track",
        args_schema=RecommendByTrackRequest,
        description="Recommend tracks by track title and artist name",
    )
    async def recommend_by_track(
        artist_name: str, track_title: str, limit: int
    ) -> RecommendResponse:
        req = RecommendByTrackRequest(
            artist_name=artist_name, track_title=track_title, limit=limit
        )
        result = await service.recommend_by_track(req)
        return result

    return [recommend_by_artist, recommend_by_track]
