# Go Review Prompt Recipe

## Codex invocation

Ask Codex to execute the `go-review` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Go Review Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `go-review` prompt recipe for <task>."

**Original command intent:** Comprehensive Go code review for idiomatic patterns, concurrency safety, error handling, and security. Invokes the go-reviewer agent. Use when Codex needs support for: Comprehensive Go code review for idiomatic patterns, concurrency safety, error handling, and security. Invokes the go-reviewer agent.

---

# Go Code Review

This command invokes the **go-reviewer** agent for comprehensive Go-specific code review.

## What This Command Does

1. **Identify Go Changes**: Find modified `.go` files via `git diff`
2. **Run Static Analysis**: Execute `go vet`, `staticcheck`, and `golangci-lint`
3. **Security Scan**: Check for SQL injection, command injection, race conditions
4. **Concurrency Review**: Analyze goroutine safety, channel usage, mutex patterns
5. **Idiomatic Go Check**: Verify code follows Go conventions and best practices
6. **Generate Report**: Categorize issues by severity

## When to Use

use the Codex prompt recipe equivalent for `go-review` when:
- After writing or modifying Go code
- Before committing Go changes
- Reviewing pull requests with Go code
- Onboarding to a new Go codebase
- Learning idiomatic Go patterns

## Review Categories

### CRITICAL (Must Fix)
- SQL/Command injection vulnerabilities
- Race conditions without synchronization
- Goroutine leaks
- Hardcoded credentials
- Unsafe pointer usage
- Ignored errors in critical paths

### HIGH (Should Fix)
- Missing error wrapping with context
- Panic instead of error returns
- Context not propagated
- Unbuffered channels causing deadlocks
- Interface not satisfied errors
- Missing mutex protection

### MEDIUM (Consider)
- Non-idiomatic code patterns
- Missing godoc comments on exports
- Inefficient string concatenation
- Slice not preallocated
- Table-driven tests not used

## Automated Checks Run

```bash
# Static analysis
go vet ./...

# Advanced checks (if installed)
staticcheck ./...
golangci-lint run

# Race detection
go build -race ./...

# Security vulnerabilities
govulncheck ./...
```

## Example Usage

```text
User: /go-review

Agent:
# Go Code Review Report

## Files Reviewed
- internal/handler/user.go (modified)
- internal/service/auth.go (modified)

## Static Analysis Results
✓ go vet: No issues
✓ staticcheck: No issues

## Issues Found

[CRITICAL] Race Condition
File: internal/service/auth.go:45
Issue: Shared map accessed without synchronization
```go
var cache = map[string]*Session{}  // Concurrent access!

func GetSession(id string) *Session {
    return cache[id]  // Race condition
}
```
Fix: Use sync.RWMutex or sync.Map
```go
var (
    cache   = map[string]*Session{}
    cacheMu sync.RWMutex
)

func GetSession(id string) *Session {
    cacheMu.RLock()
    defer cacheMu.RUnlock()
    return cache[id]
}
```

[HIGH] Missing Error Context
File: internal/handler/user.go:28
Issue: Error returned without context
```go
return err  // No context
```
Fix: Wrap with context
```go
return fmt.Errorf("get user %s: %w", userID, err)
```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: FAIL: Block merge until CRITICAL issue is fixed
```

## Approval Criteria

| Status | Condition |
|--------|-----------|
| PASS: Approve | No CRITICAL or HIGH issues |
| WARNING: Warning | Only MEDIUM issues (merge with caution) |
| FAIL: Block | CRITICAL or HIGH issues found |

## Integration with Other Commands

- use the Codex prompt recipe equivalent for `go-test` first to ensure tests pass
- use the Codex prompt recipe equivalent for `go-build` if build errors occur
- use the Codex prompt recipe equivalent for `go-review` before committing
- use the Codex prompt recipe equivalent for `code-review` for non-Go specific concerns

## Related

- Agent: `agents/go-reviewer.md`
- Skills: `skills/golang-patterns/`, `skills/golang-testing/`
