from __future__ import annotations

from typing import Protocol, Optional, Dict, Any


class AvatarImageGenerator(Protocol):
    def generate(self, user_state: Dict[str, Any]) -> Optional[str]:
        ...
