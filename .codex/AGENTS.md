# Codex Configuration Area

This directory contains Codex-native configuration. When editing these files:

- Keep `model` unset unless the user explicitly wants a pinned Codex model.
- Use Codex config keys from the current schema only. Avoid Claude-only settings.
- Keep role configs short and put large reusable workflows in skills.
- Do not add secrets to `config.toml`; MCP credentials must come from environment variables or user-level config.
- Validate after changes with `python3 -S scripts/validate_codex_package.py`.
