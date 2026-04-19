# Hookify Prompt Recipe

## Codex invocation

Ask Codex to execute the `hookify` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Hookify Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `hookify` prompt recipe for <task>."

**Original command intent:** Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions. Use when Codex needs support for: Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions.

---

Create hook rules to prevent unwanted Claude Code behaviors by analyzing conversation patterns or explicit user instructions.

## Usage

`/hookify [description of behavior to prevent]`

If no arguments are provided, analyze the current conversation to find behaviors worth preventing.

## Workflow

### Step 1: Gather Behavior Info

- With arguments: parse the user's description of the unwanted behavior
- Without arguments: use the `conversation-analyzer` agent to find:
  - explicit corrections
  - frustrated reactions to repeated mistakes
  - reverted changes
  - repeated similar issues

### Step 2: Present Findings

Show the user:

- behavior description
- proposed event type
- proposed pattern or matcher
- proposed action

### Step 3: Generate Rule Files

For each approved rule, create a file at `.claude/hookify.{name}.local.md`:

```yaml
---
name: rule-name
enabled: true
event: bash|file|stop|prompt|all
action: block|warn
pattern: "regex pattern"
---
Message shown when rule triggers.
```

### Step 4: Confirm

Report created rules and how to manage them with `/hookify-list` and `/hookify-configure`.
