from typing import Callable

from langgraph.graph.state import CompiledStateGraph
from opik import Opik, track
from opik.integrations.langchain import OpikTracer as OpikCallbackHandler

from magent.service.trace.tracer import Tracer


class OpikTracer(Tracer):
    def __init__(self, client: Opik):
        self.client = client

    def trace(self, name: str, as_type: str = "general") -> Callable:
        def decorator(func):
            return track(
                name=name,
                type=as_type,
                project_name="magent",
            )(func)

        return decorator

    def callbacks(self, *args, **kwargs) -> list[OpikCallbackHandler]:
        graph: CompiledStateGraph = kwargs.get("graph")
        handler = OpikCallbackHandler(
            graph=graph.get_graph(xray=True),
            project_name="magent",
        )
        return [handler]
