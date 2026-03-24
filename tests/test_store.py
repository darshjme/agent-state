"""Tests for StateStore."""

import os
import tempfile
import threading
import time

import pytest

from agent_state import StateStore


@pytest.fixture
def tmp_store(tmp_path):
    path = str(tmp_path / "state.json")
    return StateStore(store_path=path)


# ── Basic set / get ────────────────────────────────────────────────────────────

def test_set_and_get(tmp_store):
    tmp_store.set("key1", "hello")
    assert tmp_store.get("key1") == "hello"


def test_get_missing_returns_default(tmp_store):
    assert tmp_store.get("missing") is None
    assert tmp_store.get("missing", default=42) == 42


def test_set_overwrite(tmp_store):
    tmp_store.set("k", 1)
    tmp_store.set("k", 2)
    assert tmp_store.get("k") == 2


def test_set_complex_value(tmp_store):
    data = {"nested": [1, 2, {"deep": True}]}
    tmp_store.set("complex", data)
    assert tmp_store.get("complex") == data


# ── Delete ─────────────────────────────────────────────────────────────────────

def test_delete_existing(tmp_store):
    tmp_store.set("x", 10)
    result = tmp_store.delete("x")
    assert result is True
    assert tmp_store.get("x") is None


def test_delete_missing(tmp_store):
    result = tmp_store.delete("nonexistent")
    assert result is False


# ── Keys ──────────────────────────────────────────────────────────────────────

def test_keys_returns_all(tmp_store):
    tmp_store.set("a", 1)
    tmp_store.set("b", 2)
    assert set(tmp_store.keys()) == {"a", "b"}


def test_keys_empty(tmp_store):
    assert tmp_store.keys() == []


# ── Clear ─────────────────────────────────────────────────────────────────────

def test_clear(tmp_store):
    tmp_store.set("a", 1)
    tmp_store.set("b", 2)
    tmp_store.clear()
    assert tmp_store.keys() == []
    assert tmp_store.get("a") is None


# ── TTL ───────────────────────────────────────────────────────────────────────

def test_ttl_not_expired(tmp_store):
    tmp_store.set("ttl_key", "alive", ttl_seconds=10)
    assert tmp_store.get("ttl_key") == "alive"


def test_ttl_expired(tmp_store):
    tmp_store.set("ttl_key", "dead", ttl_seconds=0.05)
    time.sleep(0.1)
    assert tmp_store.get("ttl_key") is None


def test_ttl_expired_not_in_keys(tmp_store):
    tmp_store.set("ttl_key", "dead", ttl_seconds=0.05)
    time.sleep(0.1)
    assert "ttl_key" not in tmp_store.keys()


# ── Persistence ───────────────────────────────────────────────────────────────

def test_persistence_across_instances(tmp_path):
    path = str(tmp_path / "persist.json")
    s1 = StateStore(store_path=path)
    s1.set("persistent", 99)

    s2 = StateStore(store_path=path)
    assert s2.get("persistent") == 99


# ── Thread safety ─────────────────────────────────────────────────────────────

def test_thread_safety(tmp_store):
    results = []
    errors = []

    def worker(i):
        try:
            tmp_store.set(f"key_{i}", i)
            val = tmp_store.get(f"key_{i}")
            results.append(val)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert len(results) == 50
