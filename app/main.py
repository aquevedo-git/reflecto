# Entry point for Reflecto app with LLM Bridge integration
from extensions.llm_bridge.base import LLMBridge
from extensions.llm_bridge.openai_adapter import OpenAIAdapter
from extensions.llm_bridge.mock_adapter import MockAdapter

# Example usage (choose adapter as needed)
# import openai
# client = openai.OpenAI(api_key="YOUR_KEY")
# llm = OpenAIAdapter(client)
llm = MockAdapter()

if __name__ == "__main__":
    prompt = "Hello, Reflecto!"
    print(llm.generate(prompt))
