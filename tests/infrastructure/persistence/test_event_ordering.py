from infrastructure.persistence.session_repository import SessionRepository


def test_event_ordering_uses_append_order(tmp_path):
    db_path = tmp_path / "sessions.db"
    repo = SessionRepository(db_path=str(db_path))
    session_id = "s1"

    base_event = {
        "session_id": session_id,
        "timestamp": "2026-02-08T00:00:00Z",
        "source": "test",
        "payload": {},
    }

    repo.append_event({**base_event, "id": "e1", "type": "first"})
    repo.append_event({**base_event, "id": "e2", "type": "second"})
    repo.append_event({**base_event, "id": "e3", "type": "third"})

    events = repo.get_events(session_id)
    assert [e["type"] for e in events] == ["first", "second", "third"]
