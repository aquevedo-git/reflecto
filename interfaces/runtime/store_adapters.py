from __future__ import annotations

from typing import Dict, Any

from application.ports.identity_store import IdentityStorePort
from application.ports.prompt_store import PromptStorePort
from infrastructure.adapters.identity_store import load_identity, save_identity
from infrastructure.adapters.prompt_store import load_prompt_bundle


class IdentityStoreAdapter(IdentityStorePort):
    def load_identity(self, user_id: str) -> Dict[str, Any]:
        return load_identity(user_id)

    def save_identity(self, user_id: str, identity: Dict[str, Any]) -> None:
        save_identity(user_id, identity)


class PromptStoreAdapter(PromptStorePort):
    def load_prompt_bundle(self, base_path: str) -> Dict[str, str]:
        return load_prompt_bundle(base_path)


_identity_store = IdentityStoreAdapter()
_prompt_store = PromptStoreAdapter()


def get_identity_store() -> IdentityStorePort:
    return _identity_store


def get_prompt_store() -> PromptStorePort:
    return _prompt_store
