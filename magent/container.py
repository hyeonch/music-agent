from dependency_injector import providers, containers

from magent.infra.container import InfraContainer
from magent.service.graph.container import GraphContainer
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
    graph: GraphContainer = providers.Container(
        GraphContainer,
        settings=settings.graph,
        llm=infra.llm,
        recommendation=recommendation.recommendation,
    )
