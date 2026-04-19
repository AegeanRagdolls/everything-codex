# Promote Prompt Recipe

## Codex invocation

Ask Codex to execute the `promote` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Promote Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `promote` prompt recipe for <task>."

**Original command intent:** Promote project-scoped instincts to global scope. Use when Codex needs support for: Promote project-scoped instincts to global scope.

---

# Promote Command

Promote instincts from project scope to global scope in continuous-learning-v2.

## Implementation

Run the instinct CLI using the plugin root path:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" promote [instinct-id] [--force] [--dry-run]
```

Or if `CLAUDE_PLUGIN_ROOT` is not set (manual installation):

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py promote [instinct-id] [--force] [--dry-run]
```

## Usage

```bash
Codex prompt recipe equivalent: ask Codex to execute the `promote` workflow with arguments `# Auto-detect promotion candidates`.
Codex prompt recipe equivalent: ask Codex to execute the `promote` workflow with arguments `--dry-run            # Preview auto-promotion candidates`.
Codex prompt recipe equivalent: ask Codex to execute the `promote` workflow with arguments `--force              # Promote all qualified candidates without prompt`.
Codex prompt recipe equivalent: ask Codex to execute the `promote` workflow with arguments `grep-before-edit     # Promote one specific instinct from current project`.
```

## What to Do

1. Detect current project
2. If `instinct-id` is provided, promote only that instinct (if present in current project)
3. Otherwise, find cross-project candidates that:
   - Appear in at least 2 projects
   - Meet confidence threshold
4. Write promoted instincts to `~/.claude/homunculus/instincts/personal/` with `scope: global`
