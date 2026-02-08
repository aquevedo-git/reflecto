from __future__ import annotations

from typing import Protocol, Dict


class PromptStorePort(Protocol):
    def load_prompt_bundle(self, base_path: str) -> Dict[str, str]:
        ...
