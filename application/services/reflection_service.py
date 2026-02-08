from typing import Dict, Any

from application.ports.prompt_store import PromptStorePort
from reflecto.chatbot.daily_reflection_prompt import build_daily_reflection_prompt
from domain.core.reflection_service import build_daily_reflection

PROMPT_BASE_PATH = "reflecto/prompts"


def build_reflection_prompt(
    snapshot: Dict[str, Any],
    avatar_state: Dict[str, Any],
    prompt_store: PromptStorePort,
) -> str:
    bundle = prompt_store.load_prompt_bundle(PROMPT_BASE_PATH)
    return build_daily_reflection(
        snapshot=snapshot,
        avatar_state=avatar_state,
        identity=bundle["identity"],
        purpose=bundle["purpose"],
        style_rules=bundle["style_rules"],
        prompt_builder=build_daily_reflection_prompt,
    )
