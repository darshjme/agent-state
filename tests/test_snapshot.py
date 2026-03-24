"""Tests for StateSnapshot."""

import json

import pytest

from agent_state import StateSnapshot


# ── Construction / immutability ───────────────────────────────────────────────

def test_to_dict_returns_copy(snapshot_simple):
    d = snapshot_simple.to_dict()
    d["a"] = 999
    assert snapshot_simple.to_dict()["a"] == 1  # unchanged


def test_mutation_of_source_does_not_affect_snapshot():
    data = {"x": [1, 2, 3]}
    snap = StateSnapshot(data)
    data["x"].append(4)
    assert snap.to_dict()["x"] == [1, 2, 3]


# ── Serialisation ─────────────────────────────────────────────────────────────

def test_to_json(snapshot_simple):
    j = snapshot_simple.to_json()
    parsed = json.loads(j)
    assert parsed == {"a": 1, "b": "hello"}


def test_from_json_roundtrip(snapshot_simple):
    j = snapshot_simple.to_json()
    snap2 = StateSnapshot.from_json(j)
    assert snap2 == snapshot_simple


def test_from_json_invalid_raises():
    with pytest.raises((json.JSONDecodeError, ValueError)):
        StateSnapshot.from_json("not-json")


def test_from_json_non_dict_raises():
    with pytest.raises(ValueError):
        StateSnapshot.from_json("[1, 2, 3]")


# ── Diff ──────────────────────────────────────────────────────────────────────

def test_diff_no_changes(snapshot_simple):
    other = StateSnapshot({"a": 1, "b": "hello"})
    d = snapshot_simple.diff(other)
    assert d == {"added": [], "removed": [], "changed": []}


def test_diff_added_key():
    s1 = StateSnapshot({"a": 1})
    s2 = StateSnapshot({"a": 1, "b": 2})
    d = s1.diff(s2)
    assert d["added"] == ["b"]
    assert d["removed"] == []
    assert d["changed"] == []


def test_diff_removed_key():
    s1 = StateSnapshot({"a": 1, "b": 2})
    s2 = StateSnapshot({"a": 1})
    d = s1.diff(s2)
    assert d["removed"] == ["b"]
    assert d["added"] == []


def test_diff_changed_key():
    s1 = StateSnapshot({"a": 1, "b": 2})
    s2 = StateSnapshot({"a": 99, "b": 2})
    d = s1.diff(s2)
    assert d["changed"] == ["a"]


def test_diff_all_three():
    s1 = StateSnapshot({"keep": 0, "remove": 1, "change": 10})
    s2 = StateSnapshot({"keep": 0, "change": 99, "add": 5})
    d = s1.diff(s2)
    assert d["added"] == ["add"]
    assert d["removed"] == ["remove"]
    assert d["changed"] == ["change"]


def test_diff_empty_snapshots():
    s1 = StateSnapshot({})
    s2 = StateSnapshot({})
    assert s1.diff(s2) == {"added": [], "removed": [], "changed": []}


# ── Equality ──────────────────────────────────────────────────────────────────

def test_equality_same_data(snapshot_simple):
    other = StateSnapshot({"a": 1, "b": "hello"})
    assert snapshot_simple == other


def test_inequality_different_data(snapshot_simple):
    other = StateSnapshot({"a": 2})
    assert snapshot_simple != other


def test_repr_contains_keys(snapshot_simple):
    r = repr(snapshot_simple)
    assert "StateSnapshot" in r


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def snapshot_simple():
    return StateSnapshot({"a": 1, "b": "hello"})
