# Kotlin Review Prompt Recipe

## Codex invocation

Ask Codex to execute the `kotlin-review` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Kotlin Review Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `kotlin-review` prompt recipe for <task>."

**Original command intent:** Comprehensive Kotlin code review for idiomatic patterns, null safety, coroutine safety, and security. Invokes the kotlin-reviewer agent. Use when Codex needs support for: Comprehensive Kotlin code review for idiomatic patterns, null safety, coroutine safety, and security. Invokes the kotlin-reviewer agent.

---

# Kotlin Code Review

This command invokes the **kotlin-reviewer** agent for comprehensive Kotlin-specific code review.

## What This Command Does

1. **Identify Kotlin Changes**: Find modified `.kt` and `.kts` files via `git diff`
2. **Run Build & Static Analysis**: Execute `./gradlew build`, `detekt`, `ktlintCheck`
3. **Security Scan**: Check for SQL injection, command injection, hardcoded secrets
4. **Null Safety Review**: Analyze `!!` usage, platform type handling, unsafe casts
5. **Coroutine Review**: Check structured concurrency, dispatcher usage, cancellation
6. **Generate Report**: Categorize issues by severity

## When to Use

use the Codex prompt recipe equivalent for `kotlin-review` when:
- After writing or modifying Kotlin code
- Before committing Kotlin changes
- Reviewing pull requests with Kotlin code
- Onboarding to a new Kotlin codebase
- Learning idiomatic Kotlin patterns

## Review Categories

### CRITICAL (Must Fix)
- SQL/Command injection vulnerabilities
- Force-unwrap `!!` without justification
- Platform type null safety violations
- GlobalScope usage (structured concurrency violation)
- Hardcoded credentials
- Unsafe deserialization

### HIGH (Should Fix)
- Mutable state where immutable suffices
- Blocking calls inside coroutine context
- Missing cancellation checks in long loops
- Non-exhaustive `when` on sealed types
- Large functions (>50 lines)
- Deep nesting (>4 levels)

### MEDIUM (Consider)
- Non-idiomatic Kotlin (Java-style patterns)
- Missing trailing commas
- Scope function misuse or nesting
- Missing sequence for large collection chains
- Redundant explicit types

## Automated Checks Run

```bash
# Build check
./gradlew build

# Static analysis
./gradlew detekt

# Formatting check
./gradlew ktlintCheck

# Tests
./gradlew test
```

## Example Usage

````text
User: /kotlin-review

Agent:
# Kotlin Code Review Report

## Files Reviewed
- src/main/kotlin/com/example/service/UserService.kt (modified)
- src/main/kotlin/com/example/routes/UserRoutes.kt (modified)

## Static Analysis Results
✓ Build: Successful
✓ detekt: No issues
WARNING: ktlint: 2 formatting warnings

## Issues Found

[CRITICAL] Force-Unwrap Null Safety
File: src/main/kotlin/com/example/service/UserService.kt:28
Issue: Using !! on nullable repository result
```kotlin
val user = repository.findById(id)!!  // NPE risk
```
Fix: Use safe call with error handling
```kotlin
val user = repository.findById(id)
    ?: throw UserNotFoundException("User $id not found")
```

[HIGH] GlobalScope Usage
File: src/main/kotlin/com/example/routes/UserRoutes.kt:45
Issue: Using GlobalScope breaks structured concurrency
```kotlin
GlobalScope.launch {
    notificationService.sendWelcome(user)
}
```
Fix: Use the call's coroutine scope
```kotlin
launch {
    notificationService.sendWelcome(user)
}
```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: FAIL: Block merge until CRITICAL issue is fixed
````

## Approval Criteria

| Status | Condition |
|--------|-----------|
| PASS: Approve | No CRITICAL or HIGH issues |
| WARNING: Warning | Only MEDIUM issues (merge with caution) |
| FAIL: Block | CRITICAL or HIGH issues found |

## Integration with Other Commands

- use the Codex prompt recipe equivalent for `kotlin-test` first to ensure tests pass
- use the Codex prompt recipe equivalent for `kotlin-build` if build errors occur
- use the Codex prompt recipe equivalent for `kotlin-review` before committing
- use the Codex prompt recipe equivalent for `code-review` for non-Kotlin-specific concerns

## Related

- Agent: `agents/kotlin-reviewer.md`
- Skills: `skills/kotlin-patterns/`, `skills/kotlin-testing/`
