import logging

from pydantic_settings import BaseSettings

from magent.infra.settings import InfraSettings
from magent.service.graph.settings import GraphSettings


class Settings(BaseSettings):
    LOG_DIR: str = "logs"
    LOG_LEVEL: int = logging.INFO
    
    infra: InfraSettings = InfraSettings()
    graph: GraphSettings = GraphSettings()
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings(_env_file=".env")
