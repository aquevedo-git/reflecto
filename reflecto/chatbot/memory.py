
"""User memory data structure and update logic for Reflecto."""
import json
from typing import Dict, Any, List
from collections import Counter

def load_memory(user_id: str, storage_path: str) -> Dict[str, Any]:
	try:
		with open(f"{storage_path}/{user_id}_memory.json", "r") as f:
			return json.load(f)
	except FileNotFoundError:
		return {
			"recurring_moods": [],
			"recurring_stressors": [],
			"recurring_focus_patterns": [],
			"recurring_themes": [],
			"history": []
		}

def save_memory(user_id: str, storage_path: str, memory: Dict[str, Any]):
	with open(f"{storage_path}/{user_id}_memory.json", "w") as f:
		json.dump(memory, f, indent=2)

def update_memory(old_memory: Dict[str, Any], daily_state: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Update user memory conservatively based on daily_state.
	Only update if a pattern appears 3+ times in history.
	Do not draw conclusions from single days.
	Reflect slowly and be conservative.
	"""
	# Append today's state to history (do not mutate input)
	history = list(old_memory.get("history", []))
	history.append(daily_state)
	# Only keep last 30 days for memory
	history = history[-30:]

	def extract(field: str) -> List:
		return [d.get(field) for d in history if d.get(field) is not None]

	def recurring(items: List) -> List:
		c = Counter(items)
		return [k for k, v in c.items() if v >= 3]

	new_memory = {
		"recurring_moods": recurring(extract("mood")),
		"recurring_stressors": recurring(extract("optional_topic")),
		"recurring_focus_patterns": recurring(extract("focus")),
		"recurring_themes": recurring(extract("optional_text")),
		"history": history
	}
	return new_memory

