from dependency_injector import providers, containers

from magent.service.graph.container import LangGraphContainer
from magent.service.usecases.container import UseCaseContainer
from magent.settings import Settings


class AppContainer(containers.DeclarativeContainer):
    settings: Settings = providers.Configuration()

    use_case: UseCaseContainer = providers.Container(
        UseCaseContainer,
        settings=settings.use_case,
    )

    workflow: LangGraphContainer = providers.Container(
        LangGraphContainer,
        settings=settings.graph,
        recommendation=use_case.recommendation,
    )
