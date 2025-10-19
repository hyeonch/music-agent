from langfuse import Langfuse
from langfuse import observe
from langfuse.langchain import CallbackHandler

from magent.service.trace.tracer import Tracer


class LangfuseTracer(Tracer):
    def __init__(self, client: Langfuse):
        self.client = client

    def trace(self, name: str, as_type: str = "span"):
        def decorator(func):
            return observe(
                name=name,
                as_type=as_type,
            )(func)

        return decorator

    def callback(self, *args, **kwargs):
        return CallbackHandler(*args, **kwargs)
