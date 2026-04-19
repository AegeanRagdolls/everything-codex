# Setup Pm Prompt Recipe

## Codex invocation

Ask Codex to execute the `setup-pm` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Setup Pm Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `setup-pm` prompt recipe for <task>."

**Original command intent:** Configure your preferred package manager (npm/pnpm/yarn/bun). Use when Codex needs support for: Configure your preferred package manager (npm/pnpm/yarn/bun).

---

# Package Manager Setup

Configure your preferred package manager for this project or globally.

## Usage

```bash
# Detect current package manager
node scripts/setup-package-manager.js --detect

# Set global preference
node scripts/setup-package-manager.js --global pnpm

# Set project preference
node scripts/setup-package-manager.js --project bun

# List available package managers
node scripts/setup-package-manager.js --list
```

## Detection Priority

When determining which package manager to use, the following order is checked:

1. **Environment variable**: `CLAUDE_PACKAGE_MANAGER`
2. **Project config**: `.claude/package-manager.json`
3. **package.json**: `packageManager` field
4. **Lock file**: Presence of package-lock.json, yarn.lock, pnpm-lock.yaml, or bun.lockb
5. **Global config**: `~/.claude/package-manager.json`
6. **Fallback**: First available package manager (pnpm > bun > yarn > npm)

## Configuration Files

### Global Configuration
```json
// ~/.claude/package-manager.json
{
  "packageManager": "pnpm"
}
```

### Project Configuration
```json
// .claude/package-manager.json
{
  "packageManager": "bun"
}
```

### package.json
```json
{
  "packageManager": "pnpm@8.6.0"
}
```

## Environment Variable

Set `CLAUDE_PACKAGE_MANAGER` to override all other detection methods:

```bash
# Windows (PowerShell)
$env:CLAUDE_PACKAGE_MANAGER = "pnpm"

# macOS/Linux
export CLAUDE_PACKAGE_MANAGER=pnpm
```

## Run the Detection

To see current package manager detection results, run:

```bash
node scripts/setup-package-manager.js --detect
```
