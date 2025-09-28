from pydantic_settings import BaseSettings


class InfraSettings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    GOOGLE_API_KEY: str
    MODEL_NAME: str