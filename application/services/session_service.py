from typing import Dict, Any, List, Optional, Callable
import hashlib
import json

from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.persistence.models import SessionRecord
from infrastructure.providers import (
    TimeProvider,
    IdProvider,
    get_time_provider,
    get_id_provider,
    enforce_deterministic_providers,
)
from reflecto.session_runner import run_session
from domain.core.daily_state import DailyState

REFLECTO_VERSION = "reflecto-v1.0"


def _normalize_history_for_hash(history: List[DailyState]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for h in history:
        if isinstance(h, DailyState):
            out.append(h.to_dict())
        elif hasattr(h, "model_dump"):
            out.append(h.model_dump())
        elif hasattr(h, "dict"):
            out.append(h.dict())
        else:
            out.append(h)
    return out


def _compute_input_hash(
    user_state: dict,
    history: List[DailyState],
    flow_context: dict,
    raw_response: Optional[str],
) -> str:
    payload = {
        "user_state": user_state,
        "history": _normalize_history_for_hash(history),
        "flow_context": flow_context,
        "raw_response": raw_response,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def _append_stream_events(
    session_id: str,
    session_output: dict,
    repo: SessionRepository,
    now: Optional[str] = None,
    id_factory: Optional[Callable[[], str]] = None,
    time_provider: Optional[TimeProvider] = None,
    id_provider: Optional[IdProvider] = None,
) -> None:
    """Persist deterministic event journal for SSE + replay."""
    enforce_deterministic_providers(time_provider, id_provider)
    time_provider = get_time_provider(time_provider)
    id_provider = get_id_provider(id_provider)
    timestamp = now or time_provider.now().isoformat()
    source = "session_service"
    event_id = id_factory or (lambda: f"evt_{id_provider.new_id()}")

    event_index = 0
    prev_hash: str | None = None

    def _event_hash(event_type: str, payload: dict, event_index: int, timestamp: str, prev: str | None) -> str:
        canonical = {
            "type": event_type,
            "payload": payload,
            "event_index": event_index,
            "timestamp": timestamp,
            "prev_hash": prev,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def append(event_type: str, payload: dict) -> None:
        nonlocal event_index, prev_hash
        event_index += 1
        event_hash = _event_hash(event_type, payload, event_index, timestamp, prev_hash)
        repo.append_event(
            {
                "id": event_id(),
                "session_id": session_id,
                "timestamp": timestamp,
                "event_index": event_index,
                "type": event_type,
                "payload": payload,
                "source": source,
                "event_hash": event_hash,
                "prev_hash": prev_hash,
            }
        )
        prev_hash = event_hash

    def _coerce_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            if isinstance(value.get("text"), str):
                return value.get("text")
            return json.dumps(value, sort_keys=True)
        return str(value)

    def _coerce_phrase(value: Any, key: str) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(key)
        if isinstance(value, str):
            return value
        return str(value)

    avatar_prompt = _coerce_text(session_output.get("avatar_prompt"))
    response_text = _coerce_text(session_output.get("response"))
    closing_phrase = _coerce_phrase(session_output.get("closing_phrase"), "closing_phrase")

    append("timeline_phase", {"phase": "start"})
    append("avatar", {"avatar_prompt": avatar_prompt})
    append("questions", {"questions": session_output.get("questions", [])})
    append("response_chunk", {"text": response_text})
    append("presence", session_output.get("presence", {}) or {})
    append("timeline_phase", {"phase": "presence"})
    append("timeline_phase", {"phase": "memory"})
    append("timeline_phase", {"phase": "voice"})
    append("timeline_phase", {"phase": "continuity"})
    append("closing", {"closing_phrase": closing_phrase})
    append("timeline_phase", {"phase": "closing"})
    append("done", {"session_id": session_id})


def create_session(
    user_id: str,
    input_data: dict,
    repo: Optional[SessionRepository] = None,
    now: Optional[str] = None,
    id_factory: Optional[Callable[[], str]] = None,
    time_provider: Optional[TimeProvider] = None,
    id_provider: Optional[IdProvider] = None,
    record_id: Optional[str] = None,
    record_created_at: Optional[str] = None,
) -> dict:
    enforce_deterministic_providers(time_provider, id_provider)
    repo = repo or SessionRepository(time_provider=time_provider, id_provider=id_provider)
    time_provider = get_time_provider(time_provider)
    id_provider = get_id_provider(id_provider)
    history_objs = [
        DailyState.from_dict(
            h.model_dump() if hasattr(h, "model_dump") else (h.dict() if hasattr(h, "dict") else h)
        )
        if not isinstance(h, DailyState) else h
        for h in input_data["history"]
    ]
    session_output = run_session(
        input_data["user_state"],
        history_objs,
        input_data["flow_context"],
        input_data.get("raw_response")
    )
    input_hash = _compute_input_hash(
        input_data["user_state"],
        history_objs,
        input_data["flow_context"],
        input_data.get("raw_response"),
    )
    if isinstance(session_output, dict):
        meta = session_output.get("meta")
        if not isinstance(meta, dict):
            meta = {}
        meta["input_hash"] = input_hash
        meta["input_hash_algo"] = "sha256"
        session_output["meta"] = meta
    record = SessionRecord(
        user_id=user_id,
        data=session_output,
        version=REFLECTO_VERSION,
        record_id=record_id,
        created_at=record_created_at or now,
        time_provider=time_provider,
        id_provider=id_provider,
    )
    session_id = repo.save(record)
    _append_stream_events(
        session_id=session_id,
        session_output=session_output,
        repo=repo,
        now=now,
        id_factory=id_factory,
        time_provider=time_provider,
        id_provider=id_provider,
    )
    return {"session_id": session_id, "session": session_output}


def get_session(session_id: str, repo: Optional[SessionRepository] = None) -> Optional[dict]:
    repo = repo or SessionRepository()
    return repo.get(session_id)


def list_sessions_for_user(user_id: str, repo: Optional[SessionRepository] = None) -> List[dict]:
    repo = repo or SessionRepository()
    return repo.list_for_user(user_id)


# Phase 12B: Session Replay (Audit Mode)

def replay_session(session_id: str, repo: Optional[SessionRepository] = None) -> Optional[dict]:
    repo = repo or SessionRepository()
    record = repo.get(session_id)
    if not record:
        return None
    session_data = record["data"]
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
            "meta": session_data.get("meta"),
        }
    }


def verify_event_chain(
    session_id: str,
    repo: Optional[SessionRepository] = None,
) -> dict:
    """
    Verify deterministic hash chain integrity for a session's event journal.
    Returns status and first mismatch details if any.
    """
    repo = repo or SessionRepository()
    events = repo.get_events(session_id)
    prev: str | None = None
    for event in events:
        payload = event.get("payload", {})
        canonical = {
            "type": event.get("type"),
            "payload": payload,
            "event_index": event.get("event_index"),
            "timestamp": event.get("timestamp"),
            "prev_hash": prev,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
        computed = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        stored = event.get("event_hash")
        if stored and computed != stored:
            return {
                "session_id": session_id,
                "valid": False,
                "index": event.get("event_index"),
                "expected": stored,
                "computed": computed,
            }
        prev = stored or computed
    return {"session_id": session_id, "valid": True}


def verify_session_replay(
    session_id: str,
    input_data: dict,
    repo: Optional[SessionRepository] = None,
) -> Optional[dict]:
    repo = repo or SessionRepository()
    record = repo.get(session_id)
    if not record:
        return None
    session_data = record.get("data", {})
    stored_hash = session_data.get("meta", {}).get("input_hash")

    history_objs = [
        DailyState.from_dict(
            h.model_dump() if hasattr(h, "model_dump") else (h.dict() if hasattr(h, "dict") else h)
        )
        if not isinstance(h, DailyState) else h
        for h in input_data.get("history", [])
    ]

    computed_hash = _compute_input_hash(
        input_data.get("user_state", {}),
        history_objs,
        input_data.get("flow_context", {}),
        input_data.get("raw_response"),
    )

    return {
        "session_id": session_id,
        "match": stored_hash == computed_hash,
        "stored_hash": stored_hash,
        "computed_hash": computed_hash,
        "algorithm": "sha256",
    }


def start_session(
    user_id: str,
    session_id: Optional[str] = None,
    repo: Optional[SessionRepository] = None,
    now: Optional[str] = None,
    id_factory: Optional[Callable[[], str]] = None,
    time_provider: Optional[TimeProvider] = None,
    id_provider: Optional[IdProvider] = None,
) -> dict:
    enforce_deterministic_providers(time_provider, id_provider)
    repo = repo or SessionRepository(time_provider=time_provider, id_provider=id_provider)
    time_provider = get_time_provider(time_provider)
    id_provider = get_id_provider(id_provider)
    session_id = session_id or (id_factory() if id_factory else id_provider.new_id())
    record = SessionRecord(
        user_id=user_id,
        data={},
        version=REFLECTO_VERSION,
        record_id=session_id,
        created_at=now,
        time_provider=time_provider,
        id_provider=id_provider,
    )
    repo.save(record)
    return {"session_id": session_id, "status": "started"}
