from dependency_injector import containers, providers
from langchain_core.language_models import BaseChatModel

from magent.service.graph.graph import graph_factory
from magent.service.graph.prompts import react_agent_prompt
from magent.service.graph.settings import GraphSettings
from magent.service.graph.tools import make_tools
from magent.service.usecases.recommend.recommend import RecommendationService


class GraphContainer(containers.DeclarativeContainer):
    settings: GraphSettings = providers.Configuration()
    
    llm = providers.Dependency(BaseChatModel)
    
    recommendation = providers.Dependency(RecommendationService)

    tools = providers.Factory(
        make_tools,
        service=recommendation,
    )
    
    prompt = providers.Object(react_agent_prompt)

    graph = providers.Factory(
        graph_factory,
        llm=llm,
        tools=tools,
        prompt=prompt,
        graph_type=settings.GRAPH_TYPE,
    )