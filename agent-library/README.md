# Agent Library

These are Claude-derived ECC agent playbooks preserved as references. Codex does not automatically load all of them. The project-local `.codex/config.toml` exposes 8 core roles only, keeping startup context small.

To create another Codex role, copy the relevant Markdown guidance into `.codex/agents/<role>.toml` as `developer_instructions`, then register it under `[agents.<role>]` in `.codex/config.toml`.
