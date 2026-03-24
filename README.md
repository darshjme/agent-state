# agent-state

**Persistent state management for LLM agents across sessions.**

Zero-dependency Python library (stdlib only) that lets you checkpoint agent runs, track conversation state, and manage session context across restarts.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## The Problem

LLM agents die between sessions. Every restart means:

- Lost conversation context
- No ability to resume a long-running agentic workflow from the last safe point
- Multi-session orchestration requires bespoke bookkeeping

**agent-state** solves all three with four focused classes.

---

## Installation

```bash
pip install agent-state
```

Or from source:

```bash
git clone https://github.com/darshjme-codes/agent-state.git
cd agent-state
pip install -e .
```

---

## Components

### 1. `StateStore` — Persistent key-value store

Thread-safe, file-backed JSON store with optional TTL per key.

```python
from agent_state import StateStore

store = StateStore(store_path="/tmp/my_agent.json")

# Store a value
store.set("last_query", "What is the capital of France?")

# Store with 60-second expiry
store.set("token_cache", "Bearer abc123", ttl_seconds=60)

# Retrieve (returns None or default if missing/expired)
query = store.get("last_query")
missing = store.get("nonexistent", default="fallback")

# Delete a key
store.delete("last_query")  # returns True if it existed

# All non-expired keys
print(store.keys())

# Wipe everything
store.clear()
```

### 2. `Checkpoint` — Save/restore agent run state

Checkpoint agentic workflows step-by-step. Resume from the last safe point after a crash.

```python
from agent_state import StateStore, Checkpoint

store = StateStore()
ckpt = Checkpoint(store=store, run_id="research-agent-run-42")

# Save state at each step
ckpt.save(step=1, data={"sources_found": 12, "query": "climate AI"})
ckpt.save(step=2, data={"sources_found": 12, "summaries": ["..."]})

# Restore latest checkpoint
state = ckpt.restore()          # {"sources_found": 12, "summaries": [...]}

# Restore a specific step
state = ckpt.restore(step=1)    # {"sources_found": 12, "query": "climate AI"}

# List all checkpoints with metadata
for meta in ckpt.list_checkpoints():
    print(meta)  # {"step": 1, "timestamp": 1711234567.8, "size_bytes": 64}

# Prune old checkpoints (keep step >= 2)
ckpt.delete_before(step=2)
```

### 3. `SessionManager` — Multi-session lifecycle management

Track multiple concurrent agent sessions (user threads, parallel agents, etc.).

```python
from agent_state import StateStore, SessionManager

store = StateStore()
sm = SessionManager(store=store)

# Create sessions (auto UUID or custom ID)
sid = sm.create_session()           # "550e8400-e29b-41d4-a716-446655440000"
sid2 = sm.create_session("chat-1")  # "chat-1"

# Inspect a session
record = sm.get_session(sid)
# {
#   "session_id": "...",
#   "created_at": 1711234567.0,
#   "updated_at": 1711234567.0,
#   "active": True,
#   "data": {}
# }

# Update session context
sm.update_session(sid, {"user": "alice", "language": "en"})
sm.update_session(sid, {"messages_count": 3})

# End a session
sm.end_session(sid)

# List only active sessions
active = sm.list_active_sessions()  # ["chat-1"]
```

### 4. `StateSnapshot` — Immutable point-in-time capture

Capture agent state at a moment in time, serialize/deserialize it, and diff two snapshots.

```python
from agent_state import StateSnapshot

snap1 = StateSnapshot({"temperature": 0.7, "model": "gpt-4", "tokens_used": 1000})

# Serialize
json_str = snap1.to_json()
# Deserialize
snap2 = StateSnapshot.from_json(json_str)

assert snap1 == snap2

# Evolve state
snap3 = StateSnapshot({"temperature": 0.9, "model": "gpt-4", "context_window": 128000})

# Diff
diff = snap1.diff(snap3)
# {
#   "added":   ["context_window"],
#   "removed": ["tokens_used"],
#   "changed": ["temperature"],
# }

# Immutable — source mutations don't affect snapshot
data = {"x": [1, 2]}
snap = StateSnapshot(data)
data["x"].append(3)
print(snap.to_dict())  # {"x": [1, 2]} — unchanged
```

---

## Full Example: Resumable Research Agent

```python
from agent_state import StateStore, Checkpoint, SessionManager, StateSnapshot

store = StateStore("/tmp/research_agent.json")
ckpt = Checkpoint(store, run_id="research-001")
sm = SessionManager(store)

# Start or resume a session
sid = sm.create_session("research-session-1")

# Simulate multi-step agent work
for step in range(1, 4):
    # ... do agent work ...
    state = {"step": step, "results": [f"finding-{step}"]}
    ckpt.save(step, state)
    sm.update_session(sid, {"last_step": step})
    print(f"Checkpointed step {step}")

# Take an immutable snapshot of final state
final = StateSnapshot(ckpt.restore())
print(final.to_json())

# End session
sm.end_session(sid)
print("Active sessions:", sm.list_active_sessions())  # []
```

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Zero dependencies | Works anywhere Python 3.10+ runs — no pip hell |
| Atomic file writes | `os.replace()` prevents corrupt state on crash |
| `threading.Lock` everywhere | Safe for multi-threaded LLM frameworks |
| Namespaced keys in StateStore | Checkpoint and SessionManager coexist in one file |
| Deep copy in StateSnapshot | True immutability — no accidental mutations |

---

## Running Tests

```bash
pip install pytest
cd agent-state
python -m pytest tests/ -v
```

---

## License

MIT © Darshankumar Joshi
