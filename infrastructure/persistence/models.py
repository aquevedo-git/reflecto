from typing import Any
from infrastructure.providers import (
    TimeProvider,
    IdProvider,
    get_time_provider,
    get_id_provider,
    enforce_deterministic_providers,
)

class SessionRecord:
    def __init__(
        self,
        user_id: str,
        data: dict,
        version: str,
        record_id: str | None = None,
        created_at: str | None = None,
        time_provider: TimeProvider | None = None,
        id_provider: IdProvider | None = None,
    ):
        enforce_deterministic_providers(time_provider, id_provider)
        time_provider = get_time_provider(time_provider)
        id_provider = get_id_provider(id_provider)
        self.id = record_id or id_provider.new_id()
        self.user_id = user_id
        self.created_at = created_at or time_provider.now().isoformat()
        self.data = data
        self.version = version
