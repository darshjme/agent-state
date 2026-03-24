"""SessionManager — multi-session agent state lifecycle management."""

from __future__ import annotations

import time
import uuid

from .store import StateStore


class SessionManager:
    """Manage multiple named agent sessions inside a StateStore.

    Session records are stored under ``__session__:<session_id>`` with the
    following schema:
        {
            "session_id": str,
            "created_at": float,
            "updated_at": float,
            "active": bool,
            "data": dict,
        }
    """

    _PREFIX = "__session__"

    def __init__(self, store: StateStore) -> None:
        self._store = store

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(self, session_id: str | None = None) -> str:
        """Create a new session.  Auto-generates a UUID v4 if *session_id* is None.

        Returns the session_id string.
        """
        sid = session_id or str(uuid.uuid4())
        now = time.time()
        record = {
            "session_id": sid,
            "created_at": now,
            "updated_at": now,
            "active": True,
            "data": {},
        }
        self._store.set(self._key(sid), record)
        return sid

    def get_session(self, session_id: str) -> dict | None:
        """Return the full session record, or None if not found."""
        return self._store.get(self._key(session_id), default=None)

    def update_session(self, session_id: str, data: dict) -> None:
        """Merge *data* into the session's data payload and update timestamp.

        Raises KeyError if the session does not exist.
        """
        record = self.get_session(session_id)
        if record is None:
            raise KeyError(f"Session '{session_id}' not found")
        record["data"].update(data)
        record["updated_at"] = time.time()
        self._store.set(self._key(session_id), record)

    def end_session(self, session_id: str) -> None:
        """Mark session as ended (active=False).

        Raises KeyError if the session does not exist.
        """
        record = self.get_session(session_id)
        if record is None:
            raise KeyError(f"Session '{session_id}' not found")
        record["active"] = False
        record["updated_at"] = time.time()
        self._store.set(self._key(session_id), record)

    def list_active_sessions(self) -> list[str]:
        """Return IDs of all sessions where active=True."""
        prefix = self._PREFIX + ":"
        active = []
        for key in self._store.keys():
            if key.startswith(prefix):
                record = self._store.get(key)
                if record and record.get("active", False):
                    active.append(record["session_id"])
        return active

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _key(self, session_id: str) -> str:
        return f"{self._PREFIX}:{session_id}"
