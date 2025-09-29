from dependency_injector import providers, containers

from magent.infra.container import InfraContainer
from magent.service.graph.container import LangGraphContainer
from magent.service.usecases.recommend.container import RecommendationContainer
from magent.settings import Settings


class AppContainer(containers.DeclarativeContainer):
    settings: Settings = providers.Configuration()
    infra: InfraContainer = providers.Container(
        InfraContainer,
        settings=settings.infra,
    )

    recommendation: RecommendationContainer = providers.Container(
        RecommendationContainer,
        spotify_auth=infra.spotify_auth,
    )
    
    workflow: LangGraphContainer = providers.Container(
        LangGraphContainer,
        settings=settings.graph,
        recommendation=recommendation.recommendation,
    )
