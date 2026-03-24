"""Tests for SessionManager."""

import pytest

from agent_state import SessionManager, StateStore


@pytest.fixture
def store(tmp_path):
    return StateStore(store_path=str(tmp_path / "state.json"))


@pytest.fixture
def sm(store):
    return SessionManager(store=store)


# ── Create / get ──────────────────────────────────────────────────────────────

def test_create_session_returns_id(sm):
    sid = sm.create_session()
    assert isinstance(sid, str)
    assert len(sid) > 0


def test_create_session_custom_id(sm):
    sid = sm.create_session("my-session")
    assert sid == "my-session"


def test_get_session_returns_record(sm):
    sid = sm.create_session("sess1")
    record = sm.get_session(sid)
    assert record is not None
    assert record["session_id"] == "sess1"
    assert record["active"] is True
    assert "created_at" in record
    assert "data" in record


def test_get_session_missing_returns_none(sm):
    assert sm.get_session("ghost") is None


# ── Update ────────────────────────────────────────────────────────────────────

def test_update_session_merges_data(sm):
    sid = sm.create_session()
    sm.update_session(sid, {"key": "value"})
    sm.update_session(sid, {"another": 42})
    record = sm.get_session(sid)
    assert record["data"] == {"key": "value", "another": 42}


def test_update_session_missing_raises(sm):
    with pytest.raises(KeyError):
        sm.update_session("nonexistent", {"x": 1})


# ── End session ───────────────────────────────────────────────────────────────

def test_end_session_marks_inactive(sm):
    sid = sm.create_session()
    sm.end_session(sid)
    record = sm.get_session(sid)
    assert record["active"] is False


def test_end_session_missing_raises(sm):
    with pytest.raises(KeyError):
        sm.end_session("ghost")


# ── List active sessions ──────────────────────────────────────────────────────

def test_list_active_sessions(sm):
    s1 = sm.create_session("s1")
    s2 = sm.create_session("s2")
    s3 = sm.create_session("s3")
    sm.end_session(s3)
    active = sm.list_active_sessions()
    assert "s1" in active
    assert "s2" in active
    assert "s3" not in active


def test_list_active_sessions_empty(sm):
    assert sm.list_active_sessions() == []


def test_list_active_sessions_all_ended(sm):
    s1 = sm.create_session()
    sm.end_session(s1)
    assert sm.list_active_sessions() == []


# ── UUID generation ───────────────────────────────────────────────────────────

def test_auto_uuid_unique(sm):
    ids = {sm.create_session() for _ in range(20)}
    assert len(ids) == 20
