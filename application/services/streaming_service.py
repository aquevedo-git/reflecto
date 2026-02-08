from typing import Optional

from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.streaming.streaming_service import stream_session_events as _stream_session_events


def stream_session_events(session_id: str, repo: Optional[SessionRepository] = None):
    repo = repo or SessionRepository()
    return _stream_session_events(session_id=session_id, repo=repo)
