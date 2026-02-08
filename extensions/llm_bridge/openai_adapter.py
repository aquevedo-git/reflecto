import os

from .base import LLMBridge
from reflecto.config.env_loader import load_llm_env

class OpenAIAdapter(LLMBridge):
    DETERMINISTIC_SAFE = False

    def __init__(self, client=None):
        self.config = load_llm_env()
        if client is not None:
            self.client = client
        else:
            try:
                from openai import OpenAI
                api_key = self.config.OPENAI_API_KEY.get_secret_value()
                self.client = OpenAI(api_key=api_key)
            except Exception:
                self.client = None

    def generate(self, prompt: str) -> str:
        if os.getenv("REFLECTO_DETERMINISTIC") == "1":
            return "[LLM disabled in deterministic mode]"
        if self.client is None:
            return "[OpenAIAdapter not configured]"

        model = self.config.LLM_MODEL
        timeout = self.config.LLM_TIMEOUT

        # openai>=1.0.0: use client.chat.completions.create
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                timeout=timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Contract tests expect a string return; don't hard-fail when no key/network.
            return f"[OpenAIAdapter error: {type(e).__name__}]"

