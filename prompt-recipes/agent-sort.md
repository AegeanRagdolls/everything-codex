# Agent Sort Prompt Recipe

## Codex invocation

Ask Codex to execute the `agent-sort` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

## Inputs

- Target files, folders, issue text, or feature request.
- Any constraints on edits, tests, external services, or output format.
- Explicit permission before actions with external side effects.

## Workflow

1. Read the relevant local files or pasted context.
2. Identify the smallest safe set of actions for the requested workflow.
3. Use dry-run or mock mode for external integrations unless real credentials and explicit permission are present.
4. Execute local, reversible steps first.
5. Report missing tools or credentials instead of blocking silently.

## Output format

Return a concise Codex response with:

- Summary of actions or findings.
- Files changed or reviewed.
- Validation commands and results.
- External dependency status, if any.
- Follow-up fixes required before real integration use.

## Safety / side effects

This recipe is a prompt workflow, not a native slash command. Do not assume Claude Code hooks, Claude-only slash commands, or Claude-only agent runtime are available. Do not perform network, posting, email, payment, or destructive file operations unless the user explicitly authorizes them and required credentials are configured.

## Historical Claude Code reference

The content below is retained as migration reference only. Slash-command examples are historical notes and are not Codex runtime requirements.

# Agent Sort Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `agent-sort` prompt recipe for <task>."

**Original command intent:** Legacy slash-entry shim for the agent-sort skill. Prefer the skill directly. Use when Codex needs support for: Legacy slash-entry shim for the agent-sort skill. Prefer the skill directly.

---

# Agent Sort (Legacy Shim)

Use this only if you still invoke `/agent-sort`. The maintained workflow lives in `skills/agent-sort/SKILL.md`.

## Canonical Surface

- Prefer the `agent-sort` skill directly.
- Keep this file only as a compatibility entry point.

## Arguments

`$ARGUMENTS`

## Delegation

Apply the `agent-sort` skill.
- Classify ECC surfaces with concrete repo evidence.
- Keep the result to DAILY vs LIBRARY.
- If an install change is needed afterward, hand off to `configure-ecc` instead of re-implementing install logic here.
