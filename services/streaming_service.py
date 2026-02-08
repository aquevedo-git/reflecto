
import asyncio
import json
from collections import defaultdict, deque
from typing import Dict, Deque, AsyncIterator, Iterator
from persistence.session_repository import SessionRepository

repo = SessionRepository()

# Session event queues (in-memory, per session)
_event_queues: Dict[str, Deque[dict]] = defaultdict(deque)
_event_conditions: Dict[str, asyncio.Condition] = defaultdict(asyncio.Condition)

# Helper: format SSE event
def sse(event_type: str, payload: dict) -> str:
    if event_type == "done" and "session_id" in payload:
        return (
            f"event: done\n"
            f'data: {{ "session_id": "{payload["session_id"]}" }}\n\n'
        )
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"

class _SessionEventStream:
    def __init__(self, session_id: str):
        self._session_id = session_id

    def __iter__(self) -> Iterator[str]:
        print("STREAM START")
        try:
            for event in repo.get_events(self._session_id):
                print("STREAM EVENT:", event)
                yield sse(event["type"], event["payload"])
                if event["type"] == "done":
                    print("STREAM TERMINATED")
                    return
        finally:
            print("STREAM EXITED")

    def __aiter__(self) -> AsyncIterator[str]:
        async def gen() -> AsyncIterator[str]:
            for chunk in self:
                yield chunk

        return gen()


def stream_session_events(session_id: str) -> _SessionEventStream:
    """Deterministic session SSE stream (sync + async iterable)."""
    return _SessionEventStream(session_id)

def publish_event(session_id: str, event_type: str, payload: dict):
    """
    Publish an event to a session's queue and notify listeners.
    """
    event = {"type": event_type, "payload": payload}
    _event_queues[session_id].append(event)
    cond = _event_conditions[session_id]
    # Notify all listeners
    async def notify():
        async with cond:
            cond.notify_all()
    asyncio.create_task(notify())
