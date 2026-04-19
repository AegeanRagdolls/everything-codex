# C++ Review Prompt Recipe

## Codex invocation

Ask Codex to execute the `cpp-review` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# C++ Review Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `cpp-review` prompt recipe for <task>."

**Original command intent:** Comprehensive C++ code review for memory safety, modern C++ idioms, concurrency, and security. Invokes the cpp-reviewer agent. Use when Codex needs support for: Comprehensive C++ code review for memory safety, modern C++ idioms, concurrency, and security. Invokes the cpp-reviewer agent.

---

# C++ Code Review

This command invokes the **cpp-reviewer** agent for comprehensive C++-specific code review.

## What This Command Does

1. **Identify C++ Changes**: Find modified `.cpp`, `.hpp`, `.cc`, `.h` files via `git diff`
2. **Run Static Analysis**: Execute `clang-tidy` and `cppcheck`
3. **Memory Safety Scan**: Check for raw new/delete, buffer overflows, use-after-free
4. **Concurrency Review**: Analyze thread safety, mutex usage, data races
5. **Modern C++ Check**: Verify code follows C++17/20 conventions and best practices
6. **Generate Report**: Categorize issues by severity

## When to Use

use the Codex prompt recipe equivalent for `cpp-review` when:
- After writing or modifying C++ code
- Before committing C++ changes
- Reviewing pull requests with C++ code
- Onboarding to a new C++ codebase
- Checking for memory safety issues

## Review Categories

### CRITICAL (Must Fix)
- Raw `new`/`delete` without RAII
- Buffer overflows and use-after-free
- Data races without synchronization
- Command injection via `system()`
- Uninitialized variable reads
- Null pointer dereferences

### HIGH (Should Fix)
- Rule of Five violations
- Missing `std::lock_guard` / `std::scoped_lock`
- Detached threads without proper lifetime management
- C-style casts instead of `static_cast`/`dynamic_cast`
- Missing `const` correctness

### MEDIUM (Consider)
- Unnecessary copies (pass by value instead of `const&`)
- Missing `reserve()` on known-size containers
- `using namespace std;` in headers
- Missing `[[nodiscard]]` on important return values
- Overly complex template metaprogramming

## Automated Checks Run

```bash
# Static analysis
clang-tidy --checks='*,-llvmlibc-*' src/*.cpp -- -std=c++17

# Additional analysis
cppcheck --enable=all --suppress=missingIncludeSystem src/

# Build with warnings
cmake --build build -- -Wall -Wextra -Wpedantic
```

## Example Usage

```text
User: /cpp-review

Agent:
# C++ Code Review Report

## Files Reviewed
- src/handler/user.cpp (modified)
- src/service/auth.cpp (modified)

## Static Analysis Results
✓ clang-tidy: 2 warnings
✓ cppcheck: No issues

## Issues Found

[CRITICAL] Memory Leak
File: src/service/auth.cpp:45
Issue: Raw `new` without matching `delete`
```cpp
auto* session = new Session(userId);  // Memory leak!
cache[userId] = session;
```
Fix: Use `std::unique_ptr`
```cpp
auto session = std::make_unique<Session>(userId);
cache[userId] = std::move(session);
```

[HIGH] Missing const Reference
File: src/handler/user.cpp:28
Issue: Large object passed by value
```cpp
void processUser(User user) {  // Unnecessary copy
```
Fix: Pass by const reference
```cpp
void processUser(const User& user) {
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

- use the Codex prompt recipe equivalent for `cpp-test` first to ensure tests pass
- use the Codex prompt recipe equivalent for `cpp-build` if build errors occur
- use the Codex prompt recipe equivalent for `cpp-review` before committing
- use the Codex prompt recipe equivalent for `code-review` for non-C++ specific concerns

## Related

- Agent: `agents/cpp-reviewer.md`
- Skills: `skills/cpp-coding-standards/`, `skills/cpp-testing/`
