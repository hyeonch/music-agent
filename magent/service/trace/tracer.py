import inspect
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, TypeVar, Any

from magent.settings import settings

F = TypeVar("F", bound=Callable[..., Any])


class Tracer(ABC):
    @abstractmethod
    def trace(self, name: str, as_type: str = "") -> Callable[[F], F]:
        raise NotImplementedError

    @abstractmethod
    def callbacks(self, *args, **kwargs) -> Any:
        raise NotImplementedError


def set_tracer():
    if settings.TRACER == "opik":
        from opik import Opik
        from magent.adapters.trace.opik import OpikTracer

        tracer = OpikTracer(
            Opik(
                project_name="magent",
                host=settings.OPIK_HOST,
            )
        )
    elif settings.TRACER == "langfuse":
        from langfuse import Langfuse
        from magent.adapters.trace.langfuse import LangfuseTracer

        tracer = LangfuseTracer(
            Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
            )
        )
    else:
        tracer = None

    global _tracer_instance
    _tracer_instance = tracer


def get_tracer() -> Tracer:
    if _tracer_instance is None:
        raise RuntimeError("Tracer has not been initialized. Call set_tracer() first.")
    return _tracer_instance


def trace(name: str, as_type: str | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        trace_kwargs = {} if as_type is None else {"as_type": as_type}
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                tracer = get_tracer()
                wrapped = tracer.trace(name, **trace_kwargs)(func)
                return await wrapped(*args, **kwargs)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                tracer = get_tracer()
                wrapped = tracer.trace(name, **trace_kwargs)(func)
                return wrapped(*args, **kwargs)

            return sync_wrapper

    return decorator
