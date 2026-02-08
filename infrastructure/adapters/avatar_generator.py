from pathlib import Path
from typing import Optional, Dict, Any
import os

from domain.ports.avatar_image_port import AvatarImageGenerator

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


def generate_avatar_image(user_state: Dict[str, Any]) -> Optional[str]:
    try:
        from app.client import get_openai_client as app_client
        import requests

        user_id = user_state.get("user_id")
        if not user_id:
            return None

        skills = user_state.get("skills", {})
        presence = user_state.get("presence", {})
        time_of_day = user_state.get("time_of_day", "day")

        client = app_client()
        if client is None:
            return None

        top_skill = max(skills, key=skills.get) if skills else "personal"

        energy_level = presence.get("energy_level", "medium") if isinstance(presence, dict) else getattr(presence, "energy_level", "medium")

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


class OpenAIAvatarGenerator(AvatarImageGenerator):
    def generate(self, user_state: Dict[str, Any]) -> Optional[str]:
        return generate_avatar_image(user_state)
