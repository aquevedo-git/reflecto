from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, ValidationError
import os

class LLMEnvConfig(BaseSettings):
    OPENAI_API_KEY: SecretStr
    LLM_PROVIDER: str
    LLM_MODEL: str
    LLM_TIMEOUT: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    def safe_dict(self):
        # Return config without secrets
        return {
            'LLM_PROVIDER': self.LLM_PROVIDER,
            'LLM_MODEL': self.LLM_MODEL,
            'LLM_TIMEOUT': self.LLM_TIMEOUT
        }

# Centralized loader function

def load_llm_env():
    try:
        config = LLMEnvConfig()
        return config
    except ValidationError as e:
        missing = [err['loc'][0] for err in e.errors()]
        raise RuntimeError(f"Missing required environment variables: {missing}")
