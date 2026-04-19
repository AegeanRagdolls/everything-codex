# Instinct Export Prompt Recipe

## Codex invocation

Ask Codex to execute the `instinct-export` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Instinct Export Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `instinct-export` prompt recipe for <task>."

**Original command intent:** Export instincts from project/global scope to a file. Use when Codex needs support for: Export instincts from project/global scope to a file.

---

# Instinct Export Command

Exports instincts to a shareable format. Perfect for:
- Sharing with teammates
- Transferring to a new machine
- Contributing to project conventions

## Usage

```
Codex prompt recipe equivalent: ask Codex to execute the `instinct-export` workflow with arguments `# Export all personal instincts`.
Codex prompt recipe equivalent: ask Codex to execute the `instinct-export` workflow with arguments `--domain testing          # Export only testing instincts`.
Codex prompt recipe equivalent: ask Codex to execute the `instinct-export` workflow with arguments `--min-confidence 0.7      # Only export high-confidence instincts`.
Codex prompt recipe equivalent: ask Codex to execute the `instinct-export` workflow with arguments `--output team-instincts.yaml`.
Codex prompt recipe equivalent: ask Codex to execute the `instinct-export` workflow with arguments `--scope project --output project-instincts.yaml`.
```

## What to Do

1. Detect current project context
2. Load instincts by selected scope:
   - `project`: current project only
   - `global`: global only
   - `all`: project + global merged (default)
3. Apply filters (`--domain`, `--min-confidence`)
4. Write YAML-style export to file (or stdout if no output path provided)

## Output Format

Creates a YAML file:

```yaml
# Instincts Export
# Generated: 2025-01-22
# Source: personal
# Count: 12 instincts

---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.8
domain: code-style
source: session-observation
scope: project
project_id: a1b2c3d4e5f6
project_name: my-app
---

# Prefer Functional Style

## Action
Use functional patterns over classes.
```

## Flags

- `--domain <name>`: Export only specified domain
- `--min-confidence <n>`: Minimum confidence threshold
- `--output <file>`: Output file path (prints to stdout when omitted)
- `--scope <project|global|all>`: Export scope (default: `all`)
