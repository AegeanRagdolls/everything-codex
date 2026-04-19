# Prp Commit Prompt Recipe

## Codex invocation

Ask Codex to execute the `prp-commit` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Prp Commit Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `prp-commit` prompt recipe for <task>."

**Original command intent:** Quick commit with natural language file targeting — describe what to commit in plain English. Use when Codex needs support for: Quick commit with natural language file targeting — describe what to commit in plain English.

---

# Smart Commit

> Adapted from PRPs-agentic-eng by Wirasm. Part of the PRP workflow series.

**Input**: $ARGUMENTS

---

## Phase 1 — ASSESS

```bash
git status --short
```

If output is empty → stop: "Nothing to commit."

Show the user a summary of what's changed (added, modified, deleted, untracked).

---

## Phase 2 — INTERPRET & STAGE

Interpret `$ARGUMENTS` to determine what to stage:

| Input | Interpretation | Git Command |
|---|---|---|
| *(blank / empty)* | Stage everything | `git add -A` |
| `staged` | Use whatever is already staged | *(no git add)* |
| `*.ts` or `*.py` etc. | Stage matching glob | `git add '*.ts'` |
| `except tests` | Stage all, then unstage tests | `git add -A && git reset -- '**/*.test.*' '**/*.spec.*' '**/test_*' 2>/dev/null \|\| true` |
| `only new files` | Stage untracked files only | `git ls-files --others --exclude-standard \| grep . && git ls-files --others --exclude-standard \| xargs git add` |
| `the auth changes` | Interpret from status/diff — find auth-related files | `git add <matched files>` |
| Specific filenames | Stage those files | `git add <files>` |

For natural language inputs (like "the auth changes"), cross-reference the `git status` output and `git diff` to identify relevant files. Show the user which files you're staging and why.

```bash
git add <determined files>
```

After staging, verify:
```bash
git diff --cached --stat
```

If nothing staged, stop: "No files matched your description."

---

## Phase 3 — COMMIT

Craft a single-line commit message in imperative mood:

```
{type}: {description}
```

Types:
- `feat` — New feature or capability
- `fix` — Bug fix
- `refactor` — Code restructuring without behavior change
- `docs` — Documentation changes
- `test` — Adding or updating tests
- `chore` — Build, config, dependencies
- `perf` — Performance improvement
- `ci` — CI/CD changes

Rules:
- Imperative mood ("add feature" not "added feature")
- Lowercase after the type prefix
- No period at the end
- Under 72 characters
- Describe WHAT changed, not HOW

```bash
git commit -m "{type}: {description}"
```

---

## Phase 4 — OUTPUT

Report to user:

```
Committed: {hash_short}
Message:   {type}: {description}
Files:     {count} file(s) changed

Next steps:
  - git push           → push to remote
  - /prp-pr            → create a pull request
  - /code-review       → review before pushing
```

---

## Examples

| You say | What happens |
|---|---|
| `/prp-commit` | Stages all, auto-generates message |
| `/prp-commit staged` | Commits only what's already staged |
| `/prp-commit *.ts` | Stages all TypeScript files, commits |
| `/prp-commit except tests` | Stages everything except test files |
| `/prp-commit the database migration` | Finds DB migration files from status, stages them |
| `/prp-commit only new files` | Stages untracked files only |
