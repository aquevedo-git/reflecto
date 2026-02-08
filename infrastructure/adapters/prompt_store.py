from pathlib import Path
from typing import Dict


def load_prompt_text(relative_path: str, base_path: str) -> str:
    path = Path(base_path) / relative_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_prompt_bundle(base_path: str) -> Dict[str, str]:
    return {
        "identity": load_prompt_text("avatar/identity.txt", base_path),
        "purpose": load_prompt_text("avatar/purpose.txt", base_path),
        "style_rules": load_prompt_text("avatar/style_rules.txt", base_path),
    }
