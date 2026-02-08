from __future__ import annotations

from api.contracts.write import ActionWrite
from application.ports.action_store import ActionStorePort
from infrastructure.adapters.action_store import add_action as _add_action


class ActionStoreAdapter(ActionStorePort):
    def add_action(self, session_id: str, action: ActionWrite) -> int:
        return _add_action(session_id, action)


_action_store = ActionStoreAdapter()


def get_action_store() -> ActionStorePort:
    return _action_store
