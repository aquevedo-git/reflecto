
import datetime
import uuid
from persistence.session_repository import SessionRepository
from persistence.models import SessionRecord
from reflecto.session_runner import run_session
from reflecto.core.daily_state import DailyState

repo = SessionRepository()

REFLECTO_VERSION = "reflecto-v1.0"


def _append_stream_events(session_id: str, session_output: dict) -> None:
    """Persist Phase-13 deterministic event journal for SSE + replay."""
    now = datetime.datetime.utcnow().isoformat()
    source = "session_service"

    def append(event_type: str, payload: dict) -> None:
        repo.append_event(
            {
                "id": f"evt_{uuid.uuid4()}",
                "session_id": session_id,
                "timestamp": now,
                "type": event_type,
                "payload": payload,
                "source": source,
            }
        )

    append("avatar", {"avatar_prompt": session_output.get("avatar_prompt")})
    append("questions", {"questions": session_output.get("questions", [])})
    append("response_chunk", {"text": session_output.get("response") or ""})
    append("presence", session_output.get("presence", {}) or {})
    append("closing", {"closing_phrase": session_output.get("closing_phrase")})
    append("done", {"session_id": session_id})

def create_session(user_id: str, input_data: dict) -> dict:
    # Convert history items (which may be Pydantic models) to dicts, then to DailyState
    history_objs = [
        DailyState.from_dict(h.dict() if hasattr(h, 'dict') else h)
        if not isinstance(h, DailyState) else h
        for h in input_data["history"]
    ]
    session_output = run_session(
        input_data["user_state"],
        history_objs,
        input_data["flow_context"],
        input_data.get("raw_response")
    )
    record = SessionRecord(user_id=user_id, data=session_output, version=REFLECTO_VERSION)
    session_id = repo.save(record)
    _append_stream_events(session_id=session_id, session_output=session_output)
    return {"session_id": session_id, "session": session_output}

def get_session(session_id: str) -> dict:
    return repo.get(session_id)

def list_sessions_for_user(user_id: str) -> list:
    return repo.list_for_user(user_id)


# Phase 12B: Session Replay (Audit Mode)
def replay_session(session_id: str) -> dict:
    record = repo.get(session_id)
    if not record:
        return None
    # Only return stored session data, wrapped in replay envelope
    session_data = record['data']
    return {
        "mode": "replay",
        "recomputed": False,
        "session": {
            "avatar_prompt": session_data.get("avatar_prompt"),
            "questions": session_data.get("questions"),
            "response": session_data.get("response"),
            "presence": session_data.get("presence"),
            "continuity_phrase": session_data.get("continuity_phrase"),
            "closing_phrase": session_data.get("closing_phrase"),
            "meta": session_data.get("meta")
        }
    }
