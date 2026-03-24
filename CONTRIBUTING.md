# Contributing to agent-state

Thank you for considering a contribution! This is a small, focused library — keep changes minimal and well-tested.

## Development Setup

```bash
git clone https://github.com/darshjme-codes/agent-state.git
cd agent-state
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests must pass before opening a pull request.

## Code Style

- Standard library only — **no new dependencies**.
- Type annotations on all public methods.
- Docstrings on all public classes and methods.
- Follow PEP 8.

## Pull Request Guidelines

1. Fork the repo and create a feature branch from `main`.
2. Write tests for every new code path.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Open a PR with a clear description of what and why.

## Reporting Issues

Open a GitHub issue with a minimal reproducible example and your Python version.
