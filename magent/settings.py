import logging

from pydantic_settings import BaseSettings

from magent.service.graph.settings import GraphSettings
from magent.service.usecases.settings import UseCaseSettings


class Settings(BaseSettings):
    LOG_DIR: str = "logs"
    LOG_LEVEL: int = logging.INFO

    TRACER: str = ""

    # Langfuse settings
    LANGFUSE_HOST: str = ""
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""

    # Opik settings
    OPIK_HOST: str = ""
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    graph: GraphSettings = GraphSettings()
    use_case: UseCaseSettings = UseCaseSettings()

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings(_env_file=".env")
