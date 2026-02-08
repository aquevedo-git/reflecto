# Entry point for Reflecto app with LLM Bridge integration
from extensions.llm_bridge.base import LLMBridge
from extensions.llm_bridge.openai_adapter import OpenAIAdapter
from extensions.llm_bridge.mock_adapter import MockLLMAdapter as MockAdapter
from application.services.llm_guard import enforce_deterministic_llm, wrap_llm_adapter


# Example usage (choose adapter as needed)
# import openai
# client = openai.OpenAI(api_key="YOUR_KEY")
# llm = OpenAIAdapter(client)
llm = wrap_llm_adapter(MockAdapter())

if __name__ == "__main__":
    prompt = "Hello, Reflecto!"
    print(llm.generate(prompt))
