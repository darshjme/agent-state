"""Tests for Checkpoint."""

import time

import pytest

from agent_state import Checkpoint, StateStore


@pytest.fixture
def store(tmp_path):
    return StateStore(store_path=str(tmp_path / "state.json"))


@pytest.fixture
def ckpt(store):
    return Checkpoint(store=store, run_id="run-001")


# ── Save / restore ────────────────────────────────────────────────────────────

def test_save_and_restore_specific_step(ckpt):
    ckpt.save(1, {"msg": "step1"})
    ckpt.save(2, {"msg": "step2"})
    assert ckpt.restore(1) == {"msg": "step1"}
    assert ckpt.restore(2) == {"msg": "step2"}


def test_restore_latest(ckpt):
    ckpt.save(1, {"msg": "step1"})
    ckpt.save(3, {"msg": "step3"})
    ckpt.save(2, {"msg": "step2"})
    assert ckpt.restore() == {"msg": "step3"}


def test_restore_missing_step_returns_none(ckpt):
    ckpt.save(1, {"x": 1})
    assert ckpt.restore(99) is None


def test_restore_empty_returns_none(ckpt):
    assert ckpt.restore() is None


def test_save_overwrites_same_step(ckpt):
    ckpt.save(1, {"v": "old"})
    ckpt.save(1, {"v": "new"})
    assert ckpt.restore(1) == {"v": "new"}
    assert len(ckpt.list_checkpoints()) == 1


# ── List checkpoints ──────────────────────────────────────────────────────────

def test_list_checkpoints_metadata(ckpt):
    ckpt.save(1, {"data": "hello"})
    ckpt.save(2, {"data": "world"})
    meta = ckpt.list_checkpoints()
    assert len(meta) == 2
    steps = [m["step"] for m in meta]
    assert 1 in steps and 2 in steps
    for m in meta:
        assert "timestamp" in m
        assert "size_bytes" in m
        assert m["size_bytes"] > 0


def test_list_checkpoints_empty(ckpt):
    assert ckpt.list_checkpoints() == []


# ── Delete before ─────────────────────────────────────────────────────────────

def test_delete_before(ckpt):
    for i in range(1, 6):
        ckpt.save(i, {"step": i})
    ckpt.delete_before(4)
    remaining = [m["step"] for m in ckpt.list_checkpoints()]
    assert remaining == [4, 5]


def test_delete_before_none_removed(ckpt):
    ckpt.save(5, {"x": 1})
    ckpt.delete_before(1)
    assert len(ckpt.list_checkpoints()) == 1


# ── Isolation between run_ids ─────────────────────────────────────────────────

def test_run_id_isolation(store):
    c1 = Checkpoint(store=store, run_id="run-A")
    c2 = Checkpoint(store=store, run_id="run-B")
    c1.save(1, {"owner": "A"})
    c2.save(1, {"owner": "B"})
    assert c1.restore(1) == {"owner": "A"}
    assert c2.restore(1) == {"owner": "B"}
