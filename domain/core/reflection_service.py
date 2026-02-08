# reflecto/core/reflection_service.py

from typing import Dict, Any, Callable

def build_daily_reflection(
    snapshot: Dict[str, Any],
    avatar_state: Dict[str, Any],
    identity: Dict[str, Any],
    purpose: Dict[str, Any],
    style_rules: Dict[str, Any],
    prompt_builder: Callable[..., str],
) -> str:
    """
    Pure reflection prompt builder. All external data must be injected.
    """

    return prompt_builder(
        identity=identity,
        purpose=purpose,
        style_rules=style_rules,
        snapshot=snapshot,
        avatar_state=avatar_state,
    )
