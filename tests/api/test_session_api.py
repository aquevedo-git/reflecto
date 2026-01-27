import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_post_and_get_session(monkeypatch):
    # Patch run_session to return deterministic output
    def fake_run_session(user_state, history, flow_context, raw_response=None):
        return {"avatar_prompt": "A", "questions": [1], "response": "B", "presence": "C", "continuity_phrase": "D", "closing_phrase": "E", "meta": {"foo": "bar"}}
    monkeypatch.setattr("reflecto.session_runner.run_session", fake_run_session)

    req = {
        "user_id": "user42",
        "user_state": {"avatar": "test"},
        "history": [{
            "date": "2026-01-27",
            "energy": 5,
            "mood": 5,
            "stress": 5,
            "focus": 5,
            "confidence": 5,
            "body": 5,
            "meaning": 5
        }],
        "flow_context": {},
        "raw_response": ""
    }
    post_resp = client.post("/session", json=req)
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert "session_id" in data
    assert "session" in data
    session_id = data["session_id"]

    # GET /session/{id}
    get_resp = client.get(f"/session/{session_id}")
    assert get_resp.status_code == 200
    session = get_resp.json()
    assert session["id"] == session_id
    assert session["user_id"] == "user42"
    assert session["data"] == data["session"]

    # GET /sessions/{user_id}
    list_resp = client.get("/sessions/user42")
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert any(s["id"] == session_id for s in sessions)
