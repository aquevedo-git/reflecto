import os
import tempfile
import shutil
import pytest
from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.persistence.models import SessionRecord

@pytest.fixture
def temp_db():
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_sessions.db")
    yield db_path
    shutil.rmtree(tmpdir)

def make_record(user_id, data, version="reflecto-v1.0"):
    return SessionRecord(user_id=user_id, data=data, version=version)

def test_save_and_get(temp_db):
    repo = SessionRepository(temp_db)
    rec = make_record("user1", {"foo": "bar"})
    session_id = repo.save(rec)
    loaded = repo.get(session_id)
    assert loaded is not None
    assert loaded["id"] == rec.id
    assert loaded["user_id"] == rec.user_id
    assert loaded["data"] == rec.data
    assert loaded["version"] == rec.version

def test_list_for_user(temp_db):
    repo = SessionRepository(temp_db)
    rec1 = make_record("userA", {"a": 1})
    rec2 = make_record("userA", {"b": 2})
    rec3 = make_record("userB", {"c": 3})
    repo.save(rec1)
    repo.save(rec2)
    repo.save(rec3)
    userA_sessions = repo.list_for_user("userA")
    assert len(userA_sessions) == 2
    userB_sessions = repo.list_for_user("userB")
    assert len(userB_sessions) == 1

def test_get_missing(temp_db):
    repo = SessionRepository(temp_db)
    assert repo.get("not-a-real-id") is None
