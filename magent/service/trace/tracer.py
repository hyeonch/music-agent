import inspect
from abc import ABC, abstractmethod
from functools import wraps

from typing import Callable, TypeVar, Any


F = TypeVar("F", bound=Callable[..., Any])


class Tracer(ABC):
    @abstractmethod
    def trace(self, name: str, as_type: str) -> Callable[[F], F]:
        raise NotImplementedError

    @abstractmethod
    def callback(self, *args, **kwargs) -> Any:
        raise NotImplementedError


def set_tracer(tracer: Tracer):
    global _tracer_instance
    _tracer_instance = tracer


def get_tracer() -> Tracer:
    if _tracer_instance is None:
        raise RuntimeError("Tracer has not been initialized. Call set_tracer() first.")
    return _tracer_instance


def trace(name: str, as_type: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                tracer = get_tracer()
                wrapped = tracer.trace(name, as_type)(func)
                return await wrapped(*args, **kwargs)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                tracer = get_tracer()
                wrapped = tracer.trace(name, as_type)(func)
                return wrapped(*args, **kwargs)

            return sync_wrapper

    return decorator
