from abc import ABC, abstractmethod

class LLMBridge(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send prompt to LLM and return response as string."""
        pass
