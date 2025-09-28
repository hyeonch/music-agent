from dependency_injector import containers, providers
from spotipy import Spotify

from magent.adapters.repository.reccobeats import ReccobeatsRecommendationRepository
from magent.adapters.repository.spotify import SpotifyArtistRepository
from magent.infra.spotify import SpotifyAuth
from magent.service.usecases.recommend.recommend import RecommendationService


class RecommendationContainer(containers.DeclarativeContainer):
    spotify_auth: SpotifyAuth = providers.Dependency(SpotifyAuth)

    artist_repo: SpotifyArtistRepository = providers.Factory(
        SpotifyArtistRepository,
        auth=spotify_auth,
    )
    rec_repo: ReccobeatsRecommendationRepository = providers.Factory(
        ReccobeatsRecommendationRepository,
    )

    recommendation: RecommendationService = providers.Factory(
        RecommendationService,
        artist_repo=artist_repo,
        rec_repo=rec_repo,
    )
