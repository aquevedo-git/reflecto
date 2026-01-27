from .base import LLMBridge
import openai

class OpenAIAdapter(LLMBridge):
    def __init__(self, client: openai.OpenAI):
        self.client = client

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=512
        )
        return response.choices[0].text.strip()
