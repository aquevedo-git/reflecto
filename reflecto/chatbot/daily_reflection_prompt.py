# reflecto/chatbot/daily_reflection_prompt.py

from typing import Dict, Any

def build_daily_reflection_prompt(identity: str, purpose: str, style_rules: str,
                                  snapshot: Dict[str, Any], avatar_state: Dict[str, Any]) -> str:
    return f"""
You are Reflecto Life-OS.

IDENTITY:
{identity}

PURPOSE:
{purpose}

STYLE RULES:
{style_rules}

TODAY SNAPSHOT (structured data):
{snapshot}

AVATAR STATE:
{avatar_state}

TASK:
Write a short daily reflection:
- 3 bullet summary of today
- 1 pattern you notice
- 1 suggestion for tomorrow (small + achievable)
Keep tone aligned with style rules.
""".strip()
