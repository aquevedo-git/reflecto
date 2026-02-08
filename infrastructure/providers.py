from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, UTC
import os
import uuid


class TimeProvider(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Return current time as timezone-aware datetime."""
        raise NotImplementedError()


class IdProvider(ABC):
    @abstractmethod
    def new_id(self) -> str:
        """Return a new unique identifier string."""
        raise NotImplementedError()


@dataclass(frozen=True)
class SystemTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True)
class UUIDProvider(IdProvider):
    def new_id(self) -> str:
        return str(uuid.uuid4())


@dataclass(frozen=True)
class FixedTimeProvider(TimeProvider):
    fixed_time: datetime

    def now(self) -> datetime:
        return self.fixed_time


@dataclass(frozen=True)
class FixedIdProvider(IdProvider):
    fixed_id: str

    def new_id(self) -> str:
        return self.fixed_id


_DEFAULT_TIME_PROVIDER = SystemTimeProvider()
_DEFAULT_ID_PROVIDER = UUIDProvider()


class DeterministicProviderViolation(RuntimeError):
    pass


def enforce_deterministic_providers(
    time_provider: TimeProvider | None,
    id_provider: IdProvider | None,
) -> None:
    if os.getenv("REFLECTO_DETERMINISTIC") == "1":
        if time_provider is None or id_provider is None:
            raise DeterministicProviderViolation(
                "Deterministic mode requires explicit TimeProvider and IdProvider."
            )


def get_time_provider(provider: TimeProvider | None = None) -> TimeProvider:
    return provider or _DEFAULT_TIME_PROVIDER


def get_id_provider(provider: IdProvider | None = None) -> IdProvider:
    return provider or _DEFAULT_ID_PROVIDER
