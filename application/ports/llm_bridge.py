from __future__ import annotations

from typing import Protocol


class LLMBridgePort(Protocol):
    DETERMINISTIC_SAFE: bool

    def generate(self, prompt: str) -> str:
        """Send prompt to LLM and return response as string."""
        ...
