# Harness Audit Prompt Recipe

## Codex invocation

Ask Codex to execute the `harness-audit` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Harness Audit Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `harness-audit` prompt recipe for <task>."

**Original command intent:** harness audit. Use when Codex needs support for: harness audit.

---

# Harness Audit Command

Run a deterministic repository harness audit and return a prioritized scorecard.

## Usage

`/harness-audit [scope] [--format text|json] [--root path]`

- `scope` (optional): `repo` (default), `hooks`, `skills`, `commands`, `agents`
- `--format`: output style (`text` default, `json` for automation)
- `--root`: audit a specific path instead of the current working directory

## Deterministic Engine

Always run:

```bash
node scripts/harness-audit.js <scope> --format <text|json> [--root <path>]
```

This script is the source of truth for scoring and checks. Do not invent additional dimensions or ad-hoc points.

Rubric version: `2026-03-30`.

The script computes 7 fixed categories (`0-10` normalized each):

1. Tool Coverage
2. Context Efficiency
3. Quality Gates
4. Memory Persistence
5. Eval Coverage
6. Security Guardrails
7. Cost Efficiency

Scores are derived from explicit file/rule checks and are reproducible for the same commit.
The script audits the current working directory by default and auto-detects whether the target is the ECC repo itself or a consumer project using ECC.

## Output Contract

Return:

1. `overall_score` out of `max_score` (70 for `repo`; smaller for scoped audits)
2. Category scores and concrete findings
3. Failed checks with exact file paths
4. Top 3 actions from the deterministic output (`top_actions`)
5. Suggested ECC skills to apply next

## Checklist

- Use script output directly; do not rescore manually.
- If `--format json` is requested, return the script JSON unchanged.
- If text is requested, summarize failing checks and top actions.
- Include exact file paths from `checks[]` and `top_actions[]`.

## Example Result

```text
Harness Audit (repo): 66/70
- Tool Coverage: 10/10 (10/10 pts)
- Context Efficiency: 9/10 (9/10 pts)
- Quality Gates: 10/10 (10/10 pts)

Top 3 Actions:
1) [Security Guardrails] Add prompt/tool preflight security guards in hooks/hooks.json. (hooks/hooks.json)
2) [Tool Coverage] Sync commands/harness-audit.md and .opencode/commands/harness-audit.md. (.opencode/commands/harness-audit.md)
3) [Eval Coverage] Increase automated test coverage across scripts/hooks/lib. (tests/)
```

## Arguments

$ARGUMENTS:
- `repo|hooks|skills|commands|agents` (optional scope)
- `--format text|json` (optional output format)
