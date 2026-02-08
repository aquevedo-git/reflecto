from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.streaming.streaming_service import sse
from application.services import session_service as ss


def test_sse_payload_sorted_keys():
    payload = {"b": 1, "a": 2}
    out = sse("test", payload)
    assert 'data: {"a": 2, "b": 1}' in out


def test_session_events_use_injected_clock_and_ids(tmp_path, monkeypatch):
    repo = SessionRepository(db_path=str(tmp_path / "sessions.db"))

    def fake_run_session(*args, **kwargs):
        return {
            "avatar_prompt": "A",
            "questions": ["Q"],
            "response": "R",
            "presence": {"p": True},
            "continuity_phrase": None,
            "closing_phrase": "C",
            "meta": {},
        }

    monkeypatch.setattr(ss, "run_session", fake_run_session)

    fixed_now = "2026-02-08T00:00:00Z"
    ids = iter(["evt_1", "evt_2", "evt_3", "evt_4", "evt_5", "evt_6"])

    result = ss.create_session(
        user_id="u1",
        input_data={
            "user_state": {"avatar": "reflecto", "date": "2026-02-08"},
            "history": [
                {
                    "date": "2026-02-07",
                    "energy": 5,
                    "mood": 5,
                    "stress": 5,
                    "focus": 5,
                    "confidence": 5,
                    "body": 5,
                    "meaning": 5,
                }
            ],
            "flow_context": {},
            "raw_response": "",
        },
        repo=repo,
        now=fixed_now,
        id_factory=lambda: next(ids),
    )

    session_id = result["session_id"]
    events = repo.get_events(session_id)

    assert [e["id"] for e in events] == ["evt_1", "evt_2", "evt_3", "evt_4", "evt_5", "evt_6"]
    assert all(e["timestamp"] == fixed_now for e in events)
    assert [e["type"] for e in events] == ["avatar", "questions", "response_chunk", "presence", "closing", "done"]
