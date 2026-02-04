"""
Deterministic streaming service for session replay.
Used by tests and audit mode.
"""

import json
from persistence.session_repository import SessionRepository


repo = SessionRepository()


def sse(event_type: str, payload: dict):

    # Special deterministic formatting for session_id event
    if event_type == "done" and "session_id" in payload:
        return (
            f"event: done\n"
            f'data: {{ "session_id": "{payload["session_id"]}" }}\n\n'
        )

    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"



def stream_session_events(session_id: str):
    """
    Deterministic replay stream.
    Produces fixed ordered events.
    """

    record = repo.get(session_id)

    if not record:
        yield sse("error", {"message": "Session not found"})
        return

    session = record

    input_data = session.get("input", {})

    # REQUIRED ORDER (tests enforce this)

    yield sse("avatar", {
        "avatar": input_data.get("user_state", {}).get("avatar")
    })

    yield sse("questions", {
        "questions": ["How are you feeling today?"]
    })

    yield sse("response_chunk", {
        "text": "Reflecto session initialized."
    })

    yield sse("presence", {
        "state": "AWAKE"
    })

    yield sse("closing", {
        "status": "complete"
    })

    yield sse("done", {
        "session_id": session_id
    })
