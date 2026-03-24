"""Checkpoint — save/restore agent run state across steps."""

from __future__ import annotations

import json
import time
from typing import Any

from .store import StateStore


class Checkpoint:
    """Named checkpoint manager tied to a specific *run_id*.

    Checkpoints are stored inside the shared StateStore under a namespaced
    key ``__ckpt__:<run_id>``.

    Each checkpoint entry is a dict:
        {
            "step": int,
            "timestamp": float,
            "data": dict,
        }
    """

    _PREFIX = "__ckpt__"

    def __init__(self, store: StateStore, run_id: str) -> None:
        self._store = store
        self._run_id = run_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, step: int, data: dict) -> None:
        """Persist *data* at *step* with the current UTC timestamp."""
        checkpoints = self._load_all()
        entry = {
            "step": step,
            "timestamp": time.time(),
            "data": data,
        }
        # Overwrite if step already exists
        checkpoints = [c for c in checkpoints if c["step"] != step]
        checkpoints.append(entry)
        checkpoints.sort(key=lambda c: c["step"])
        self._store.set(self._key(), checkpoints)

    def restore(self, step: int | None = None) -> dict | None:
        """Return data for *step* (or the latest step if None).

        Returns None if no checkpoints exist.
        """
        checkpoints = self._load_all()
        if not checkpoints:
            return None
        if step is None:
            entry = checkpoints[-1]
        else:
            matches = [c for c in checkpoints if c["step"] == step]
            if not matches:
                return None
            entry = matches[0]
        return entry["data"]

    def list_checkpoints(self) -> list[dict]:
        """Return metadata for all checkpoints: [{step, timestamp, size_bytes}]."""
        checkpoints = self._load_all()
        result = []
        for c in checkpoints:
            size_bytes = len(json.dumps(c["data"]).encode("utf-8"))
            result.append(
                {
                    "step": c["step"],
                    "timestamp": c["timestamp"],
                    "size_bytes": size_bytes,
                }
            )
        return result

    def delete_before(self, step: int) -> None:
        """Prune all checkpoints with step < *step*."""
        checkpoints = self._load_all()
        checkpoints = [c for c in checkpoints if c["step"] >= step]
        self._store.set(self._key(), checkpoints)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _key(self) -> str:
        return f"{self._PREFIX}:{self._run_id}"

    def _load_all(self) -> list[dict]:
        raw = self._store.get(self._key(), default=[])
        if not isinstance(raw, list):
            return []
        return raw
