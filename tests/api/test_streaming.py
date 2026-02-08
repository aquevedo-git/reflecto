"""
Tests for Phase 13: Streaming API (SSE)
"""


from fastapi.testclient import TestClient
from api.main import app
client = TestClient(app)
def session_payload():
    # Provide a minimal valid payload for session creation (must include 'avatar')
    return {
        "input": {
            "user_id": "test-user",
            "user_state": {"avatar": "reflecto"},
            "history": [
                {
                    "date": "2026-01-27",
                    "energy": 7,
                    "mood": 6,
                    "stress": 4,
                    "focus": 5,
                    "meaning": 6
                }
            ],
            "flow_context": {},
            "raw_response": None
        }
    }

def test_streaming_event_order_and_content():
    session_payload_data = session_payload()
    # Create session and stream events
    resp = client.post("/session/stream", json=session_payload_data)
    assert resp.status_code == 200
    events = [line for line in resp.iter_lines() if line.strip()]
    # Check event order and presence of required event types
    event_types = [e.split(": ")[1] for e in events if e.startswith("event:")]
    event_types = [event for event in event_types if event != "timeline_phase"]
    required_order = ["avatar", "questions", "response_chunk", "presence", "closing", "done"]
    assert event_types[:len(required_order)] == required_order

def test_streaming_determinism():
    session_payload_data = session_payload()
    results = []
    for _ in range(2):
        resp = client.post("/session/stream", json=session_payload_data)
        events = [e for e in resp.iter_lines() if e.strip()]
        # Remove session_id from 'done' event for comparison
        filtered = [e if not e.startswith('data: { "session_id":') else 'data: { "session_id": "IGNORED" }' for e in events]
        results.append(filtered)
    assert results[0] == results[1]

def test_streaming_matches_replay():
    session_payload_data = session_payload()
    # Create session via API
    resp = client.post("/session/stream", json=session_payload_data)
    stream_content = resp.text
    stream_events = [e.strip() for e in stream_content.split("\n\n") if e.strip()]
    # Get session_id from done event
    session_id = None
    import re
    for e in stream_events:
        m = re.search(r'session_id":\s*"([^"]+)"', e)
        if m:
            session_id = m.group(1)
            break
    assert session_id is not None
    # Replay (direct call)
    from application.services.streaming_service import stream_session_events
    replay_concat = "".join(list(stream_session_events(session_id=session_id)))
    replay_events = [e.strip() for e in replay_concat.split("\n\n") if e.strip()]
    # Compare event-by-event
    assert stream_events == replay_events
