# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅         |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Send a private report to **darshjme@gmail.com** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested fix (optional)

We aim to respond within **48 hours** and will coordinate a fix and responsible disclosure timeline with you.

## Scope

agent-state stores data in local JSON files on disk. Security considerations include:

- **File permissions:** The library does not set restrictive permissions on the state file. Ensure your deployment restricts access to the store path (e.g., `/tmp/agent_state.json`) appropriately.
- **Sensitive data:** Do not store secrets, tokens, or PII in the state store without additional encryption at the application layer.
- **Path traversal:** Do not construct store paths from untrusted user input.
