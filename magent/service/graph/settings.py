from pydantic_settings import BaseSettings

class GraphSettings(BaseSettings):
    GOOGLE_API_KEY: str
    MODEL_NAME: str