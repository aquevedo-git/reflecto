
"""
Avatar generation and prompt loading utilities.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from domain.ports.avatar_image_port import AvatarImageGenerator

# Expose OpenAI symbol for tests that monkeypatch it
try:
	from openai import OpenAI
except ImportError:
	OpenAI = None

def load_avatar_prompt(user_state: dict) -> str:
	"""
	Loads and formats the avatar prompt for Reflecto by combining identity, context, daily state,
	style rules, and purpose files. Context and daily state are formatted with user_state.
	Returns the concatenated prompt string.
	Works in both Jupyter and Dash environments.
	"""
	try:
		base_dir = Path(__file__).resolve().parent.parent / 'prompts' / 'avatar'
		files = {
			'identity': base_dir / 'identity.txt',
			'context': base_dir / 'context.txt',
			'daily_state': base_dir / 'daily_state.txt',
			'style_rules': base_dir / 'style_rules.txt',
			'purpose': base_dir / 'purpose.txt',
		}

		# Read files
		identity = files['identity'].read_text(encoding='utf-8') if files['identity'].exists() else ''
		context = files['context'].read_text(encoding='utf-8') if files['context'].exists() else ''
		daily_state = files['daily_state'].read_text(encoding='utf-8') if files['daily_state'].exists() else ''
		style_rules = files['style_rules'].read_text(encoding='utf-8') if files['style_rules'].exists() else ''
		purpose = files['purpose'].read_text(encoding='utf-8') if files['purpose'].exists() else ''

		# Format context and daily_state with user_state
		try:
			context = context.format(**user_state)
		except Exception:
			pass  # If formatting fails, use raw text
		try:
			daily_state = daily_state.format(**user_state)
		except Exception:
			pass

		# Concatenate in correct order
		prompt = '\n'.join([
			identity.strip(),
			context.strip(),
			daily_state.strip(),
			style_rules.strip(),
			purpose.strip()
		])
		return prompt.strip()
	except Exception as e:
		# Basic error handling: return error message as prompt
		return f"[Error loading avatar prompt: {e}]"


def generate_avatar_image(
	user_state: Dict[str, Any],
	generator: Optional[AvatarImageGenerator] = None
) -> Optional[str]:
	if generator is None:
		return None
	return generator.generate(user_state)

