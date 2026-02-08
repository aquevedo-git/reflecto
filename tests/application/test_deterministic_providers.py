from datetime import datetime, UTC

from application.services.session_service import create_session, start_session
from domain.core.daily_state import DailyState
from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.providers import FixedTimeProvider


def _make_input_data():
    return {
        "user_state": {"user_id": "u1", "name": "Test"},
        "history": [
            DailyState(
                date="2026-01-01",
                energy=6,
                mood=6,
                stress=4,
                focus=5,
                meaning=6,
            )
        ],
        "flow_context": {"main_mode": "explore"},
        "raw_response": "Today was steady.",
    }


def test_create_session_uses_providers_deterministic(tmp_path, sequence_id_provider):
    fixed_time = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
    time_provider = FixedTimeProvider(fixed_time)
    id_provider = sequence_id_provider(["session-1"])
    event_ids = iter(["evt-1", "evt-2", "evt-3", "evt-4", "evt-5", "evt-6"])

    repo = SessionRepository(
        db_path=str(tmp_path / "sessions.db"),
        time_provider=time_provider,
        id_provider=id_provider,
    )

    out = create_session(
        user_id="u1",
        input_data=_make_input_data(),
        repo=repo,
        time_provider=time_provider,
        id_provider=id_provider,
        id_factory=lambda: next(event_ids),
    )

    session_id = out["session_id"]
    record = repo.get(session_id)
    assert record is not None
    assert record["id"] == "session-1"
    assert record["created_at"] == fixed_time.isoformat()

    events = repo.get_events(session_id)
    assert len(events) == 6
    assert all(e["timestamp"] == fixed_time.isoformat() for e in events)
    assert [e["id"] for e in events] == [
        "evt-1",
        "evt-2",
        "evt-3",
        "evt-4",
        "evt-5",
        "evt-6",
    ]


def test_start_session_uses_providers_deterministic(tmp_path, sequence_id_provider):
    fixed_time = datetime(2026, 2, 8, 12, 30, 0, tzinfo=UTC)
    time_provider = FixedTimeProvider(fixed_time)
    id_provider = sequence_id_provider(["session-2"])

    repo = SessionRepository(
        db_path=str(tmp_path / "sessions.db"),
        time_provider=time_provider,
        id_provider=id_provider,
    )

    out = start_session(
        user_id="u1",
        repo=repo,
        time_provider=time_provider,
        id_provider=id_provider,
    )

    session_id = out["session_id"]
    record = repo.get(session_id)
    assert record is not None
    assert record["id"] == "session-2"
    assert record["created_at"] == fixed_time.isoformat()
