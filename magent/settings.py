import logging

from pydantic_settings import BaseSettings

from magent.service.graph.settings import GraphSettings
from magent.service.usecases.settings import UseCaseSettings


class Settings(BaseSettings):
    LOG_DIR: str = "logs"
    LOG_LEVEL: int = logging.INFO
    
    graph: GraphSettings = GraphSettings()
    use_case: UseCaseSettings = UseCaseSettings()
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings(_env_file=".env")
