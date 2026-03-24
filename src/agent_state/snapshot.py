"""StateSnapshot — immutable point-in-time capture of agent state."""

from __future__ import annotations

import copy
import json
from typing import Any


class StateSnapshot:
    """Immutable snapshot of agent state at a specific point in time.

    All data is deep-copied on construction to guarantee immutability.
    """

    def __init__(self, data: dict) -> None:
        # Deep copy to ensure immutability
        self._data: dict = copy.deepcopy(data)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a deep copy of the snapshot data as a plain dict."""
        return copy.deepcopy(self._data)

    def to_json(self) -> str:
        """Serialise snapshot to a JSON string."""
        return json.dumps(self._data, ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "StateSnapshot":
        """Deserialise a snapshot from a JSON string."""
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise ValueError("Snapshot JSON must represent a dict/object.")
        return cls(data)

    # ------------------------------------------------------------------
    # Diff
    # ------------------------------------------------------------------

    def diff(self, other: "StateSnapshot") -> dict:
        """Compare this snapshot with *other* (both treated as flat key sets).

        Returns:
            {
                "added":   list of keys present in *other* but not in self,
                "removed": list of keys present in self but not in *other*,
                "changed": list of keys present in both but with different values,
            }
        """
        self_keys = set(self._data.keys())
        other_keys = set(other._data.keys())

        added = sorted(other_keys - self_keys)
        removed = sorted(self_keys - other_keys)
        changed = sorted(
            k for k in self_keys & other_keys if self._data[k] != other._data[k]
        )

        return {"added": added, "removed": removed, "changed": changed}

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateSnapshot):
            return NotImplemented
        return self._data == other._data

    def __repr__(self) -> str:
        return f"StateSnapshot(keys={list(self._data.keys())})"
