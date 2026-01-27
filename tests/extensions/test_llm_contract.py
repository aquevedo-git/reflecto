import inspect
from extensions.llm_bridge.base import LLMBridge
from extensions.llm_bridge.mock_adapter import MockLLMAdapter
from extensions.llm_bridge.openai_adapter import OpenAIAdapter


def _assert_contract(adapter_cls):
    adapter = adapter_cls()

    # must subclass
    assert issubclass(adapter_cls, LLMBridge)

    # must implement generate
    assert hasattr(adapter, "generate")
    assert callable(adapter.generate)

    # signature must be (prompt: str) -> str
    sig = inspect.signature(adapter.generate)
    assert len(sig.parameters) == 1

    # must return string
    out = adapter.generate("test prompt")
    assert isinstance(out, str)
    assert out is not None


def test_mock_adapter_contract():
    _assert_contract(MockLLMAdapter)


def test_openai_adapter_contract():
    _assert_contract(OpenAIAdapter)
