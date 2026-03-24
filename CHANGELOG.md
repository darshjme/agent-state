# Changelog

All notable changes to **agent-state** will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-03-24

### Added

- **StateStore** — Thread-safe, file-backed JSON key-value store with optional TTL per key.
- **Checkpoint** — Named checkpoint manager for saving and restoring agent run state by step number.
- **SessionManager** — Multi-session lifecycle management (create, update, end, list active).
- **StateSnapshot** — Immutable point-in-time capture with JSON serialisation and `diff()` support.
- Zero external dependencies — uses only Python stdlib (`json`, `threading`, `uuid`, `time`, `os`, `copy`).
- 20+ pytest tests with full coverage of all four components.
- MIT licence.
