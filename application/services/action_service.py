from __future__ import annotations

from api.contracts.write import ActionWrite
from application.ports.action_store import ActionStorePort


def add_action(session_id: str, action: ActionWrite, store: ActionStorePort) -> int:
    return store.add_action(session_id, action)
