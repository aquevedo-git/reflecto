import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.session_service import create_session
import uuid

client = TestClient(app)

def make_fake_session():
    # Minimal session data for replay
    session_data = {
        "avatar_prompt": "Test avatar prompt",
        "questions": ["Q1", "Q2"],
        "response": "Test response",
        "presence": "Test presence",
        "continuity_phrase": "Test continuity",
        "closing_phrase": "Test closing",
        "meta": {"foo": "bar"}
    }
    user_id = f"user-{uuid.uuid4()}"
    from infrastructure.persistence.models import SessionRecord
    from infrastructure.persistence.session_repository import SessionRepository
    repo = SessionRepository()
    record = SessionRecord(user_id=user_id, data=session_data, version="reflecto-v1.0")
    session_id = repo.save(record)
    return session_id, session_data

def test_replay_returns_identical_data():
    session_id, session_data = make_fake_session()
    resp = client.get(f"/session/{session_id}/replay")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["mode"] == "replay"
    assert payload["recomputed"] is False
    assert payload["session"] == session_data

def test_replay_not_found():
    resp = client.get("/session/does-not-exist/replay")
    assert resp.status_code == 404

def test_replay_does_not_call_core(monkeypatch):
    # Patch run_session and orchestrator to fail if called
    import api.session_service
    monkeypatch.setattr(api.session_service, "run_session", lambda *a, **kw: (_ for _ in ()).throw(Exception("run_session called!")))
    # Should not raise
    session_id, _ = make_fake_session()
    resp = client.get(f"/session/{session_id}/replay")
    assert resp.status_code == 200

def test_replay_determinism():
    session_id, session_data = make_fake_session()
    # Call replay multiple times, should always match
    for _ in range(3):
        resp = client.get(f"/session/{session_id}/replay")
        assert resp.status_code == 200
        assert resp.json()["session"] == session_data
