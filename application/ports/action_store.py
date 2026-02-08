from __future__ import annotations

from typing import Protocol

from api.contracts.write import ActionWrite


class ActionStorePort(Protocol):
    def add_action(self, session_id: str, action: ActionWrite) -> int:
        ...
