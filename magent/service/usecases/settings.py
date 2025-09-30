from pydantic_settings import BaseSettings


class UseCaseSettings(BaseSettings):
    LASTFM_API_KEY: str

    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
