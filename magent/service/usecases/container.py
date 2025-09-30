from dependency_injector import containers, providers

from magent.adapters.repository.lastfm import LastFmTrackRepository
from magent.adapters.repository.reccobeats import ReccobeatsRecommendationRepository
from magent.adapters.repository.spotify import SpotifyArtistRepository
from magent.service.usecases.recommend.recommend import RecommendationService
from magent.service.usecases.settings import UseCaseSettings


class UseCaseContainer(containers.DeclarativeContainer):
    settings: UseCaseSettings = providers.Configuration()

    artist_repo: SpotifyArtistRepository = providers.Factory(
        SpotifyArtistRepository,
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
    )
    track_repo: LastFmTrackRepository = providers.Factory(
        LastFmTrackRepository,
        api_key=settings.LASTFM_API_KEY,
    )
    rec_repo: ReccobeatsRecommendationRepository = providers.Factory(
        ReccobeatsRecommendationRepository,
    )

    recommendation: RecommendationService = providers.Factory(
        RecommendationService,
        artist_repo=artist_repo,
        track_repo=track_repo,
        rec_repo=rec_repo,
    )
