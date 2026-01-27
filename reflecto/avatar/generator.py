
"""
Avatar generation and prompt loading utilities.
"""

from pathlib import Path
from datetime import date as dt_date
import os


# Lazy initialization for OpenAI client
_openai_client = None
try:
	from openai import OpenAI
except ImportError:
	OpenAI = None

def get_openai_client():
	global _openai_client
	if _openai_client is None:
		if OpenAI is None:
			raise ImportError("openai package is not installed")
		_openai_client = OpenAI()
	return _openai_client

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


def generate_avatar_image(user_state: dict) -> str:
	try:
		from app.client import get_openai_client
		import requests
		import os

		user_id = user_state.get('user_id')
		if not user_id:
			return None

		skills = user_state.get('skills', {})
		presence = user_state.get('presence', {})
		time_of_day = user_state.get('time_of_day', 'day')

		client = get_openai_client()
		if client is None:
			return None

		top_skill = max(skills, key=skills.get) if skills else "personal"

		energy_level = presence.get('energy_level', 'medium') if isinstance(presence, dict) else getattr(presence, 'energy_level', 'medium')

		prompt = (
			f"A calm symbolic avatar representing a {time_of_day} mood, "
			f"{energy_level} energy, "
			f"focused on {top_skill} growth, minimalist, soft lighting, "
			"no face, abstract, reflective, life OS assistant"
		)

		avatar_dir = os.path.join("static", "avatars")
		os.makedirs(avatar_dir, exist_ok=True)
		image_path = os.path.join(avatar_dir, f"{user_id}.png")

		result = client.images.generate(
			model="gpt-image-1",
			prompt=prompt,
			size="512x512"
		)

		image_url = result.data[0].url if result.data else None
		if not image_url:
			return None

		img_data = requests.get(image_url, timeout=10).content
		with open(image_path, "wb") as f:
			f.write(img_data)

		return image_path

	except Exception as e:
		import logging
		logging.error(f"Avatar generation failed: {e}")
		return None

