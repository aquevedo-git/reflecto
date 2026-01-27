
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
	"""
	Generate a deterministic avatar image for a user for today.
	- user_state: dict, must include 'user_id' (str)
	- Returns the file path to the generated image.
	- Does not regenerate if file exists.
	"""
	user_id = user_state.get('user_id')
	if not user_id:
		raise ValueError("user_state must include 'user_id'")

	today = user_state.get('date') or dt_date.today().isoformat()
	avatar_dir = Path(__file__).resolve().parent.parent / 'data' / 'users' / str(user_id) / 'avatars'
	avatar_dir.mkdir(parents=True, exist_ok=True)
	avatar_path = avatar_dir / f"{today}.png"

	if avatar_path.exists():
		return str(avatar_path)

	prompt = load_avatar_prompt(user_state)

	# Deterministic seed: hash of user_id + date
	import hashlib
	seed_str = f"{user_id}-{today}"
	seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (10**8)

	if openai_client is None:
		raise RuntimeError("OpenAI client is not available.")

	# Call OpenAI image generation API (assume DALL-E 3 or similar)
	response = openai_client.images.generate(
		prompt=prompt,
		n=1,
		size="512x512",
		response_format="url",
		seed=seed  # Assume API supports deterministic seed
	)
	image_url = response.data[0].url

	# Download and save image
	import requests
	img_data = requests.get(image_url).content
	with open(avatar_path, 'wb') as f:
		f.write(img_data)

	return str(avatar_path)

