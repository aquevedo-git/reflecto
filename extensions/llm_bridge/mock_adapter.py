from .base import LLMBridge

class MockLLMAdapter(LLMBridge):
    def generate(self, prompt: str) -> str:
        return prompt
