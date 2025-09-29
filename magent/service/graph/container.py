from dependency_injector import containers, providers
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from magent.adapters.workflow.langgraph.graph import LangGraphOrchestrator, custom_react
from magent.adapters.workflow.langgraph.prompts import react_agent_prompt
from magent.adapters.workflow.langgraph import make_tools
from magent.service.graph.settings import GraphSettings
from magent.service.usecases.recommend.recommend import RecommendationService


class LangGraphContainer(containers.DeclarativeContainer):
    settings: GraphSettings = providers.Configuration()
    
    llm: BaseChatModel = providers.Singleton(
        ChatGoogleGenerativeAI,
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    
    recommendation = providers.Dependency(RecommendationService)

    tools = providers.Factory(
        make_tools,
        service=recommendation,
    )
    
    prompt = providers.Object(react_agent_prompt)

    graph = providers.Factory(custom_react, llm=llm, tools=tools, prompt=prompt)
    
    orchestrator = providers.Factory(
        LangGraphOrchestrator,
        graph=graph,
    )