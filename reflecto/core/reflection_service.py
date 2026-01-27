# reflecto/core/reflection_service.py

from typing import Dict, Any
from reflecto.core.prompt_loader import load_prompt_context
from reflecto.chatbot.daily_reflection_prompt import build_daily_reflection_prompt

PROMPT_BASE_PATH = "reflecto/prompts"


def build_daily_reflection(snapshot: Dict[str, Any], avatar_state: Dict[str, Any]) -> str:
    """
    C.3 Step 5 — build reflection prompt (LLM-ready, deterministic)
    """

    identity = load_prompt_context("avatar/identity.txt", PROMPT_BASE_PATH)
    purpose = load_prompt_context("avatar/purpose.txt", PROMPT_BASE_PATH)
    style = load_prompt_context("avatar/style_rules.txt", PROMPT_BASE_PATH)

    return build_daily_reflection_prompt(
        identity=identity,
        purpose=purpose,
        style_rules=style,
        snapshot=snapshot,
        avatar_state=avatar_state,
    )
