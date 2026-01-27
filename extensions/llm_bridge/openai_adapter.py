from .base import LLMBridge
import openai

class OpenAIAdapter(LLMBridge):
    def __init__(self, client=None):
        self.client = client

    def generate(self, prompt: str) -> str:
        if self.client is None:
            return "[OpenAIAdapter not configured]"

        response = self.client.responses.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=512
        )
        return response.output_text

