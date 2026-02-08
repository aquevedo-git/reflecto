from .base import LLMBridge

class MockLLMAdapter(LLMBridge):
    DETERMINISTIC_SAFE = True

    def generate(self, prompt: str) -> str:
        return prompt
