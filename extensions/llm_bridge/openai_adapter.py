from .base import LLMBridge
import openai
from reflecto.config.env_loader import load_llm_env

class OpenAIAdapter(LLMBridge):
    def __init__(self, client=None):
        self.config = load_llm_env()
        self.client = client or openai

    def generate(self, prompt: str) -> str:
        if self.client is None:
            return "[OpenAIAdapter not configured]"

        # Use environment config
        api_key = self.config.OPENAI_API_KEY.get_secret_value()
        model = self.config.LLM_MODEL
        timeout = self.config.LLM_TIMEOUT

        # Configure OpenAI client
        self.client.api_key = api_key

        response = self.client.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            timeout=timeout
        )
        return response.choices[0].message['content']

