import sys

from fastapi import FastAPI
from langfuse import Langfuse
from opik import Opik

from magent.adapters.trace.langfuse import LangfuseTracer
from magent.adapters.trace.opik import OpikTracer
from magent.app.api.entrypoints import router as chat_router
from magent.container import AppContainer
from magent.service.trace.tracer import set_tracer
from magent.settings import settings

API_PREFIX = "/api"


def _add_routers(app_: FastAPI):
    app_.include_router(chat_router, prefix=f"{API_PREFIX}/chat", tags=["chat"])


def create_app(container_: AppContainer) -> FastAPI:
    app_ = FastAPI(
        title="Magent API",
        description="a music agent powered by LLMs and Music APIs.",
        version="0.1.0",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
    )
    _add_routers(app_)
    app_.container = container_
    return app_


langfuse_tracer = LangfuseTracer(
    Langfuse(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
    )
)
opik_tracer = OpikTracer(
    Opik(
        project_name="magent",
        host=settings.OPIK_HOST,
    )
)

set_tracer(langfuse_tracer)
container = AppContainer()
container.settings.from_pydantic(settings)
container.wire(packages=[sys.modules["magent.app.api.entrypoints"]])
app = create_app(container)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
