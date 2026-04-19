# Migration Report: Everything Claude Code -> Everything Codex Code

## Codex-first decisions

- Converted Claude command files into pasteable `prompt-recipes/` rather than pretending they are native Codex slash commands.
- Converted skills into Codex skill folders with `SKILL.md` frontmatter limited to `name` and `description`.
- Added `agents/openai.yaml` metadata for each skill.
- Added `.agents/skills` with the curated core set so Codex can discover skills directly when launched from this repository.
- Updated installers to copy skills to the official user-level path `$HOME/.agents/skills`.
- Kept `.codex/config.toml` for project/user config, subagent settings, profiles, and optional MCP definitions.
- Disabled optional MCP servers by default to avoid first-run failures from missing Node/network/API keys.

## What remains intentionally non-native

- `prompt-recipes/` are not native slash commands. They are preserved workflows that the user can ask Codex to apply.
- `hooks/` are git hook examples and notes, not Claude-style runtime hooks.
- `agent-library/` is a reference library. Active Codex custom agents live in `.codex/agents`.
