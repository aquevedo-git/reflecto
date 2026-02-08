import pytest

from infrastructure.providers import IdProvider


class SequenceIdProvider(IdProvider):
    def __init__(self, ids: list[str]):
        self._ids = iter(ids)

    def new_id(self) -> str:
        return next(self._ids)


@pytest.fixture
def sequence_id_provider():
    def _factory(ids: list[str]) -> SequenceIdProvider:
        return SequenceIdProvider(ids)

    return _factory
