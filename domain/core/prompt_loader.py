
"""Prompt context builder (pure)."""
from typing import Dict, Any

def build_prompt_context(memory: Dict[str, Any] | None) -> Dict[str, Any]:
	"""
	Pure transformation: normalize memory into prompt context.
	"""
	memory = memory or {}
	return {
		"recurring_moods": memory.get("recurring_moods", []),
		"recurring_stressors": memory.get("recurring_stressors", []),
		"recurring_focus_patterns": memory.get("recurring_focus_patterns", []),
		"recurring_themes": memory.get("recurring_themes", [])
	}

