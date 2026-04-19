---
name: nanoclaw-repl
description: >-
  Operate and extend NanoClaw v2, ECC's zero-dependency session-aware REPL built on
  claude -p. Use when Codex needs support for: Operate and extend NanoClaw v2, ECC's
  zero-dependency session-aware REPL built on claude -p. Do not use for unrelated tasks.
  Inputs should include relevant files, constraints, and available tools. Output should
  be a concise plan, result, or verification summary.
---

# NanoClaw REPL

Use this skill when running or extending `scripts/claw.js`.

## Capabilities

- persistent markdown-backed sessions
- model switching with `/model`
- dynamic skill loading with `/load`
- session branching with `/branch`
- cross-session search with `/search`
- history compaction with `/compact`
- export to md/json/txt with `/export`
- session metrics with `/metrics`

## Operating Guidance

1. Keep sessions task-focused.
2. Branch before high-risk changes.
3. Compact after major milestones.
4. Export before sharing or archival.

## Extension Rules

- keep zero external runtime dependencies
- preserve markdown-as-database compatibility
- keep command handlers deterministic and local
