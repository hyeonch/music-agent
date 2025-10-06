from magent.domain.meta import RecommendationCriteria
from magent.domain.repository import (
    RecommendationRepository,
    ArtistRepository,
    TrackRepository,
)
from magent.service.trace.tracer import trace
from magent.service.usecases.recommend.dto import (
    RecommendByArtistRequest,
    RecommendResponse,
    TrackDto,
    RecommendByTrackRequest,
)


class RecommendationService:
    def __init__(
        self,
        artist_repo: ArtistRepository,
        track_repo: TrackRepository,
        rec_repo: RecommendationRepository,
    ):
        self.artist_repo = artist_repo
        self.track_repo = track_repo
        self.rec_repo = rec_repo

    @trace(name="tool.recommend_by_artist", as_type="tool")
    async def recommend_by_artist_name(
        self, req: RecommendByArtistRequest
    ) -> RecommendResponse:
        artist = await self.artist_repo.search_artist(req.artist_name)
        artist_top_tracks = await self.artist_repo.get_artist_top_tracks(artist)
        tracks = await self.rec_repo.recommend(
            RecommendationCriteria(
                size=req.limit, seeds=[t.id.id for t in artist_top_tracks[:5]]
            )
        )
        return RecommendResponse(tracks=[TrackDto.from_domain(t) for t in tracks])

    @trace(name="tool.recommend_by_track", as_type="tool")
    async def recommend_by_track(
        self, req: RecommendByTrackRequest
    ) -> RecommendResponse:
        seed_track = await self.track_repo.search_track(
            title=req.track_title, artist=req.artist_name
        )
        tracks = await self.track_repo.get_similar_tracks(seed_track, limit=req.limit)
        return RecommendResponse(tracks=[TrackDto.from_domain(t) for t in tracks])
