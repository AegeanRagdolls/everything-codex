# Rust Review Prompt Recipe

## Codex invocation

Ask Codex to execute the `rust-review` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Rust Review Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `rust-review` prompt recipe for <task>."

**Original command intent:** Comprehensive Rust code review for ownership, lifetimes, error handling, unsafe usage, and idiomatic patterns. Invokes the rust-reviewer agent. Use when Codex needs support for: Comprehensive Rust code review for ownership, lifetimes, error handling, unsafe usage, and idiomatic patterns. Invokes the rust-reviewer agent.

---

# Rust Code Review

This command invokes the **rust-reviewer** agent for comprehensive Rust-specific code review.

## What This Command Does

1. **Verify Automated Checks**: Run `cargo check`, `cargo clippy -- -D warnings`, `cargo fmt --check`, and `cargo test` — stop if any fail
2. **Identify Rust Changes**: Find modified `.rs` files via `git diff HEAD~1` (or `git diff main...HEAD` for PRs)
3. **Run Security Audit**: Execute `cargo audit` if available
4. **Security Scan**: Check for unsafe usage, command injection, hardcoded secrets
5. **Ownership Review**: Analyze unnecessary clones, lifetime issues, borrowing patterns
6. **Generate Report**: Categorize issues by severity

## When to Use

use the Codex prompt recipe equivalent for `rust-review` when:
- After writing or modifying Rust code
- Before committing Rust changes
- Reviewing pull requests with Rust code
- Onboarding to a new Rust codebase
- Learning idiomatic Rust patterns

## Review Categories

### CRITICAL (Must Fix)
- Unchecked `unwrap()`/`expect()` in production code paths
- `unsafe` without `// SAFETY:` comment documenting invariants
- SQL injection via string interpolation in queries
- Command injection via unvalidated input in `std::process::Command`
- Hardcoded credentials
- Use-after-free via raw pointers

### HIGH (Should Fix)
- Unnecessary `.clone()` to satisfy borrow checker
- `String` parameter where `&str` or `impl AsRef<str>` suffices
- Blocking in async context (`std::thread::sleep`, `std::fs`)
- Missing `Send`/`Sync` bounds on shared types
- Wildcard `_ =>` match on business-critical enums
- Large functions (>50 lines)

### MEDIUM (Consider)
- Unnecessary allocation in hot paths
- Missing `with_capacity` when size is known
- Suppressed clippy warnings without justification
- Public API without `///` documentation
- Consider `#[must_use]` on non-`must_use` return types where ignoring values is likely a bug

## Automated Checks Run

```bash
# Build gate (must pass before review)
cargo check

# Lints and suggestions
cargo clippy -- -D warnings

# Formatting
cargo fmt --check

# Tests
cargo test

# Security audit (if available)
if command -v cargo-audit >/dev/null; then cargo audit; else echo "cargo-audit not installed"; fi
```

## Example Usage

````text
User: /rust-review

Agent:
# Rust Code Review Report

## Files Reviewed
- src/service/user.rs (modified)
- src/handler/api.rs (modified)

## Static Analysis Results
- Build: Successful
- Clippy: No warnings
- Formatting: Passed
- Tests: All passing

## Issues Found

[CRITICAL] Unchecked unwrap in Production Path
File: src/service/user.rs:28
Issue: Using `.unwrap()` on database query result
```rust
let user = db.find_by_id(id).unwrap();  // Panics on missing user
```
Fix: Propagate error with context
```rust
let user = db.find_by_id(id)
    .context("failed to fetch user")?;
```

[HIGH] Unnecessary Clone
File: src/handler/api.rs:45
Issue: Cloning String to satisfy borrow checker
```rust
let name = user.name.clone();
process(&user, &name);
```
Fix: Restructure to avoid clone
```rust
let result = process_name(&user.name);
use_user(&user, result);
```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: Block merge until CRITICAL issue is fixed
````

## Approval Criteria

| Status | Condition |
|--------|-----------|
| Approve | No CRITICAL or HIGH issues |
| Warning | Only MEDIUM issues (merge with caution) |
| Block | CRITICAL or HIGH issues found |

## Integration with Other Commands

- use the Codex prompt recipe equivalent for `rust-test` first to ensure tests pass
- use the Codex prompt recipe equivalent for `rust-build` if build errors occur
- use the Codex prompt recipe equivalent for `rust-review` before committing
- use the Codex prompt recipe equivalent for `code-review` for non-Rust-specific concerns

## Related

- Agent: `agents/rust-reviewer.md`
- Skills: `skills/rust-patterns/`, `skills/rust-testing/`
