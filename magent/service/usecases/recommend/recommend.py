from magent.domain.meta import RecommendationCriteria
from magent.domain.repository import RecommendationRepository, ArtistRepository
from magent.logger import logger
from magent.service.usecases.recommend.dto import (
    RecommendRequest,
    RecommendResponse,
    TrackDto,
)


class RecommendationService:
    def __init__(
        self, artist_repo: ArtistRepository, rec_repo: RecommendationRepository
    ):
        self.artist_repo = artist_repo
        self.rec_repo = rec_repo

    async def recommend_by_artist_name(self, req: RecommendRequest) -> RecommendResponse:
        artist = await self.artist_repo.search_artist(req.artist_name)
        logger.info("usecase.recommend.artist_found", artist=artist)
        artist_top_tracks = await self.artist_repo.get_artist_top_tracks(artist)
        logger.info(
            "usecase.recommend.artist_top_tracks_found", top_tracks=[t.title for t in artist_top_tracks[:5]]
        )
        tracks = await self.rec_repo.recommend(
            RecommendationCriteria(size=req.limit, seeds=[t.id.id for t in artist_top_tracks[:5]])
        )
        return RecommendResponse(tracks=[TrackDto.from_domain(t) for t in tracks])
