from dependency_injector import containers, providers
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from magent.infra.settings import InfraSettings
from magent.infra.spotify import SpotifyAuth


class InfraContainer(containers.DeclarativeContainer):
    settings: InfraSettings = providers.Configuration()

    spotify_auth: SpotifyAuth = providers.Singleton(
        SpotifyAuth,
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
    )

    llm: BaseChatModel = providers.Singleton(
        ChatGoogleGenerativeAI,
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
    )
