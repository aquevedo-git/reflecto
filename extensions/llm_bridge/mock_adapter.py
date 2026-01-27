from .base import LLMBridge

class MockAdapter(LLMBridge):
    def generate(self, prompt: str) -> str:
        return prompt
