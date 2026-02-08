
import json
from typing import AsyncIterator, Iterator, Optional
from infrastructure.persistence.session_repository import SessionRepository

# Helper: format SSE event
def sse(event_type: str, payload: dict) -> str:
    if event_type == "done" and "session_id" in payload:
        return (
            f"event: done\n"
            f'data: {{ "session_id": "{payload["session_id"]}" }}\n\n'
        )
    return f"event: {event_type}\ndata: {json.dumps(payload, sort_keys=True)}\n\n"

class _SessionEventStream:
    def __init__(self, session_id: str, repo: SessionRepository):
        self._session_id = session_id
        self._repo = repo

    def __iter__(self) -> Iterator[str]:
        try:
            for event in self._repo.get_events(self._session_id):
                yield sse(event["type"], event["payload"])
                if event["type"] == "done":
                    return
        finally:
            pass

    def __aiter__(self) -> AsyncIterator[str]:
        async def gen() -> AsyncIterator[str]:
            for chunk in self:
                yield chunk

        return gen()

def stream_session_events(
    session_id: str,
    repo: Optional[SessionRepository] = None,
) -> _SessionEventStream:
    """Deterministic session SSE stream (sync + async iterable)."""
    return _SessionEventStream(session_id, repo or SessionRepository())
