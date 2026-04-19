# Everything Codex Code - Agent Instructions

This repository is a Codex-first skill and workflow catalog converted from ECC. Treat Codex as the runtime. Do not assume Claude Code-only hooks, slash commands, or Task-tool subagents exist.

## Setup commands

- Validate package structure: `python -S scripts/validate_codex_package.py`
- Cross-platform dry-run skill installation: `python scripts/install-codex.py --dry-run --core --codex-home .codex-test/tmp/ecc-codex-home`
- Install curated skills: `python scripts/install-codex.py --core`
- Install all migrated skills: `python scripts/install-codex.py --all`
- Windows fallback installer: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-codex.ps1 -Core -DryRun`
- Unix fallback installer: `bash scripts/install-codex.sh --dry-run --core`

## Codex operating rules

- Prefer repo skills from `.agents/skills` or installed user skills from the user's home `.agents/skills` directory over reading large workflow files.
- Use `.agents/skills` for direct repo-scoped testing. Use `skills/.curated` as the default user installation set. Use `skills/.experimental` only when the task needs the larger library.
- For code changes, inspect files first, make minimal diffs, run relevant checks, then summarize exact evidence.
- For research or package/API claims, use MCP/web only when available and cite primary sources in the final answer.
- Keep secrets out of files. Use environment variables or user-level Codex config for MCP credentials.
- Use `approval_policy = "on-request"` and `sandbox_mode = "workspace-write"` as the recommended default unless the user explicitly asks for a stricter or more autonomous profile.
- External integrations must distinguish mock/dry-run PASS from real integration PASS. If env vars, tools, MCP servers, or credentials are missing, report `EXTERNAL_NOT_CONFIGURED` and setup steps rather than claiming real PASS.

## Custom agent rules

- Core active agents are the 8 daily-use TOMLs: `build_fixer`, `code_reviewer`, `docs_researcher`, `explorer`, `planner`, `refactor_cleaner`, `security_reviewer`, and `test_runner`.
- Playbook-derived agents are generated as `.codex/agents/playbook_*.toml` from `agent-library/*.md`. They are Codex-compatible optional custom agents, not the same thing as the source playbook Markdown.
- Install only core agents for normal use. Install playbook agents only when the larger role library is useful, because many agents add selector noise and token cost.
- Every custom agent must obey the anti-hang contract in its TOML: finish small smoke tasks quickly, avoid whole-repo scans, avoid child agents, avoid waiting on unavailable tools, and avoid edits unless explicitly requested by the parent task.

## Skill rules

Every skill must follow Codex skill anatomy:

- Folder name matches `name` in `SKILL.md`.
- `SKILL.md` frontmatter contains only `name` and `description`.
- Description must include trigger context so Codex can decide when to load it.
- Optional UI metadata lives at `agents/openai.yaml`.
- Avoid symlinked `SKILL.md`; materialize files for compatibility.

## Prompt recipe rules

Files in `prompt-recipes/` are not native slash commands. They preserve old command workflows as pasteable instructions. When a user asks for an old command, use the matching prompt recipe and adapt it to the current repo.

## PR / commit guidance

- Explain what changed and why.
- Include validation commands and results.
- Do not claim real Codex CLI execution unless `codex` was actually run.

## First-run note

Optional MCP servers in `.codex/config.toml` are disabled by default. Enable them only after dependencies and credentials are ready.
