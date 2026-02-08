from __future__ import annotations

from typing import Protocol, Dict, Any


class IdentityStorePort(Protocol):
    def load_identity(self, user_id: str) -> Dict[str, Any]:
        ...

    def save_identity(self, user_id: str, identity: Dict[str, Any]) -> None:
        ...
