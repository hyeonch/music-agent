from typing import Protocol, Any


class WorkflowOrchestrator(Protocol):
    def run(
        self, user_id: str, session_id: str, query: Any, meta: dict[str, Any]
    ) -> Any: ...

    async def arun(
        self, user_id: str, session_id: str, query: Any, meta: dict[str, Any]
    ) -> Any: ...
