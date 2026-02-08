from __future__ import annotations

import os

from extensions.llm_bridge.base import LLMBridge


class DeterministicLLMViolation(RuntimeError):
    pass


def enforce_deterministic_llm(adapter: LLMBridge, deterministic: bool | None = None) -> LLMBridge:
    """
    Enforce that only deterministic-safe adapters are used when replay mode is active.
    """
    if deterministic is None:
        deterministic = os.getenv("REFLECTO_DETERMINISTIC") == "1"

    if deterministic and not getattr(adapter, "DETERMINISTIC_SAFE", False):
        raise DeterministicLLMViolation(
            "Non-deterministic LLM adapter blocked in deterministic mode."
        )

    return adapter


class SafeLLMAdapter(LLMBridge):
    """
    Adapter wrapper that enforces deterministic constraints at call time.
    """

    def __init__(self, adapter: LLMBridge, deterministic: bool | None = None):
        self._adapter = enforce_deterministic_llm(adapter, deterministic=deterministic)
        self.DETERMINISTIC_SAFE = getattr(adapter, "DETERMINISTIC_SAFE", False)

    def generate(self, prompt: str) -> str:
        enforce_deterministic_llm(self._adapter)
        return self._adapter.generate(prompt)


def wrap_llm_adapter(adapter: LLMBridge, deterministic: bool | None = None) -> LLMBridge:
    """
    Wrap an adapter with deterministic enforcement to prevent bypass.
    """
    return SafeLLMAdapter(adapter, deterministic=deterministic)
