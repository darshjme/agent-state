"""StateStore — thread-safe, file-backed, JSON key-value store with TTL support."""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Any


class StateStore:
    """Persistent key-value store backed by a JSON file.

    Features:
    - Thread-safe via threading.Lock
    - Optional per-key TTL (auto-expire)
    - Atomic writes (write to temp file, then rename)
    """

    def __init__(self, store_path: str = "/tmp/agent_state.json") -> None:
        self._path = store_path
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {}   # {key: value}
        self._meta: dict[str, Any] = {}   # {key: {expires_at: float|None}}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        """Store *value* under *key*.  Optionally expire after *ttl_seconds*."""
        expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
        with self._lock:
            self._data[key] = value
            self._meta[key] = {"expires_at": expires_at}
            self._save()

    def get(self, key: str, default: Any = None) -> Any:
        """Return value for *key*, or *default* if missing / expired."""
        with self._lock:
            if key not in self._data:
                return default
            meta = self._meta.get(key, {})
            expires_at = meta.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                # Lazy eviction
                del self._data[key]
                del self._meta[key]
                self._save()
                return default
            return self._data[key]

    def delete(self, key: str) -> bool:
        """Delete *key*.  Returns True if it existed."""
        with self._lock:
            existed = key in self._data
            if existed:
                del self._data[key]
                self._meta.pop(key, None)
                self._save()
            return existed

    def keys(self) -> list[str]:
        """Return all non-expired keys."""
        now = time.time()
        with self._lock:
            expired = [
                k for k, m in self._meta.items()
                if m.get("expires_at") is not None and now > m["expires_at"]
            ]
            for k in expired:
                self._data.pop(k, None)
                self._meta.pop(k, None)
            if expired:
                self._save()
            return list(self._data.keys())

    def clear(self) -> None:
        """Wipe all stored state."""
        with self._lock:
            self._data.clear()
            self._meta.clear()
            self._save()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._data = raw.get("data", {})
            self._meta = raw.get("meta", {})
        except (json.JSONDecodeError, OSError):
            # Corrupt / missing file — start fresh
            self._data = {}
            self._meta = {}

    def _save(self) -> None:
        """Atomic write: dump to temp file, then os.replace."""
        tmp = self._path + ".tmp"
        payload = {"data": self._data, "meta": self._meta}
        os.makedirs(os.path.dirname(os.path.abspath(self._path)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        os.replace(tmp, self._path)
