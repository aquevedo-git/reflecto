
import asyncio
import json
from collections import defaultdict, deque
from typing import Dict, Deque, Any, AsyncGenerator
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

async def stream_session_events(session_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator for session-scoped event streaming.
    Maintains deterministic order, supports replay, and safe closing.
    """
    print("STREAM START")
    try:
        # Replay alignment: load all past events
        events = repo.get_events(session_id)
        found_done = False
        for event in events:
            print("STREAM EVENT:", event)
            yield sse(event["type"], event["payload"])
            if event["type"] == "done":
                found_done = True
                print("STREAM REPLAY COMPLETE")
                print("STREAM TERMINATED")
                return

        print("STREAM REPLAY COMPLETE")

        # Only subscribe to live events if session is not done
        print("STREAM SUBSCRIBED TO LIVE EVENTS")
        queue = _event_queues[session_id]
        cond = _event_conditions[session_id]
        while True:
            async with cond:
                while not queue:
                    await cond.wait()
                event = queue.popleft()
            print("STREAM EVENT:", event)
            yield sse(event["type"], event["payload"])
            if event["type"] == "done":
                print("STREAM TERMINATED")
                return
    finally:
        print("STREAM EXITED")

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
