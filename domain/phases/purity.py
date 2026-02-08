from __future__ import annotations

import copy
from typing import Any, Callable


class FrozenList(list):
    def _blocked(self, *args, **kwargs):
        raise TypeError("FrozenList is immutable")

    def append(self, __object) -> None:  # type: ignore[override]
        self._blocked()

    def extend(self, __iterable) -> None:  # type: ignore[override]
        self._blocked()

    def insert(self, __index, __object) -> None:  # type: ignore[override]
        self._blocked()

    def pop(self, __index: int = -1):  # type: ignore[override]
        self._blocked()

    def remove(self, __value) -> None:  # type: ignore[override]
        self._blocked()

    def clear(self) -> None:  # type: ignore[override]
        self._blocked()

    def sort(self, *, key=None, reverse: bool = False) -> None:  # type: ignore[override]
        self._blocked()

    def reverse(self) -> None:  # type: ignore[override]
        self._blocked()

    def __setitem__(self, key, value) -> None:  # type: ignore[override]
        self._blocked()

    def __delitem__(self, key) -> None:  # type: ignore[override]
        self._blocked()

    def __deepcopy__(self, memo):
        return self


class FrozenDict(dict):
    def _blocked(self, *args, **kwargs):
        raise TypeError("FrozenDict is immutable")

    def clear(self) -> None:  # type: ignore[override]
        self._blocked()

    def pop(self, __key, __default=None):  # type: ignore[override]
        self._blocked()

    def popitem(self):  # type: ignore[override]
        self._blocked()

    def setdefault(self, __key, __default=None):  # type: ignore[override]
        self._blocked()

    def update(self, *args, **kwargs) -> None:  # type: ignore[override]
        self._blocked()

    def __setitem__(self, key, value) -> None:  # type: ignore[override]
        self._blocked()

    def __delitem__(self, key) -> None:  # type: ignore[override]
        self._blocked()

    def __deepcopy__(self, memo):
        return self


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return FrozenDict({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return FrozenList([_freeze(v) for v in value])
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    return value


def freeze_value(value: Any) -> Any:
    """
    Public helper to deep-copy then freeze a value tree.
    Useful for enforcing immutability at architectural boundaries.
    """
    return _freeze(copy.deepcopy(value))


def phase_pure(func: Callable[..., Any]) -> Callable[..., Any]:
    """Deep-copy inputs and freeze outputs to enforce purity boundaries."""

    def wrapper(*args, **kwargs):
        frozen_args = copy.deepcopy(args)
        frozen_kwargs = copy.deepcopy(kwargs)
        result = func(*frozen_args, **frozen_kwargs)
        return _freeze(copy.deepcopy(result))

    wrapper.__name__ = getattr(func, "__name__", "phase_pure")
    wrapper.__doc__ = getattr(func, "__doc__", None)
    module = getattr(func, "__module__", None)
    if module is not None:
        wrapper.__module__ = module
    return wrapper
