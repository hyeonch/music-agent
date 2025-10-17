from pydantic_settings import BaseSettings


class GraphSettings(BaseSettings):
    API_KEY: str
    MODEL_NAME: str
