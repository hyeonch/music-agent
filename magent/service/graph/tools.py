from langchain_core.tools import tool

from magent.logger import logger
from magent.service.usecases.recommend.dto import RecommendRequest, RecommendResponse
from magent.service.usecases.recommend.recommend import RecommendationService


def make_tools(service: RecommendationService) -> list:
    @tool(
        "recommend_by_artist",
        args_schema=RecommendRequest,
        description="Recommend tracks by artist name",
    )
    async def recommend_by_artist(artist_name: str, limit: int) -> RecommendResponse:
        req = RecommendRequest(artist_name=artist_name, limit=limit)
        logger.info("tool.recommend.start", req=req)
        result = await service.recommend_by_artist_name(req)
        logger.info("tool.recommend.end", result=result)
        return result
    
    return [recommend_by_artist]
