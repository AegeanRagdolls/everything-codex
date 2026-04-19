# Refactor Clean Prompt Recipe

## Codex invocation

Ask Codex to execute the `refactor-clean` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Refactor Clean Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `refactor-clean` prompt recipe for <task>."

**Original command intent:** refactor clean. Use when Codex needs support for: refactor clean.

---

# Refactor Clean

Safely identify and remove dead code with test verification at every step.

## Step 1: Detect Dead Code

Run analysis tools based on project type:

| Tool | What It Finds | Command |
|------|--------------|---------|
| knip | Unused exports, files, dependencies | `npx knip` |
| depcheck | Unused npm dependencies | `npx depcheck` |
| ts-prune | Unused TypeScript exports | `npx ts-prune` |
| vulture | Unused Python code | `vulture src/` |
| deadcode | Unused Go code | `deadcode ./...` |
| cargo-udeps | Unused Rust dependencies | `cargo +nightly udeps` |

If no tool is available, use Grep to find exports with zero imports:
```
# Find exports, then check if they're imported anywhere
```

## Step 2: Categorize Findings

Sort findings into safety tiers:

| Tier | Examples | Action |
|------|----------|--------|
| **SAFE** | Unused utilities, test helpers, internal functions | Delete with confidence |
| **CAUTION** | Components, API routes, middleware | Verify no dynamic imports or external consumers |
| **DANGER** | Config files, entry points, type definitions | Investigate before touching |

## Step 3: Safe Deletion Loop

For each SAFE item:

1. **Run full test suite** — Establish baseline (all green)
2. **Delete the dead code** — Use Edit tool for surgical removal
3. **Re-run test suite** — Verify nothing broke
4. **If tests fail** — Immediately revert with `git checkout -- <file>` and skip this item
5. **If tests pass** — Move to next item

## Step 4: Handle CAUTION Items

Before deleting CAUTION items:
- Search for dynamic imports: `import()`, `require()`, `__import__`
- Search for string references: route names, component names in configs
- Check if exported from a public package API
- Verify no external consumers (check dependents if published)

## Step 5: Consolidate Duplicates

After removing dead code, look for:
- Near-duplicate functions (>80% similar) — merge into one
- Redundant type definitions — consolidate
- Wrapper functions that add no value — inline them
- Re-exports that serve no purpose — remove indirection

## Step 6: Summary

Report results:

```
Dead Code Cleanup
──────────────────────────────
Deleted:   12 unused functions
           3 unused files
           5 unused dependencies
Skipped:   2 items (tests failed)
Saved:     ~450 lines removed
──────────────────────────────
All tests passing PASS:
```

## Rules

- **Never delete without running tests first**
- **One deletion at a time** — Atomic changes make rollback easy
- **Skip if uncertain** — Better to keep dead code than break production
- **Don't refactor while cleaning** — Separate concerns (clean first, refactor later)
