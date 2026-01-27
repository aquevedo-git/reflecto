
"""Prompt loader with memory context support for Reflecto."""
from pathlib import Path
from typing import Dict, Any
import json

def load_prompt_context(user_id: str, storage_path: str) -> Dict[str, Any]:
	"""
	Loads user memory and returns a dict for prompt context.
	"""
	memory_path = Path(storage_path) / f"{user_id}_memory.json"
	if memory_path.exists():
		with open(memory_path, "r") as f:
			memory = json.load(f)
	else:
		memory = {}
	# Only include memory fields relevant for prompt context
	return {
		"recurring_moods": memory.get("recurring_moods", []),
		"recurring_stressors": memory.get("recurring_stressors", []),
		"recurring_focus_patterns": memory.get("recurring_focus_patterns", []),
		"recurring_themes": memory.get("recurring_themes", [])
	}

