# C++ Build Prompt Recipe

## Codex invocation

Ask Codex to execute the `cpp-build` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# C++ Build Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `cpp-build` prompt recipe for <task>."

**Original command intent:** Fix C++ build errors, CMake issues, and linker problems incrementally. Invokes the cpp-build-resolver agent for minimal, surgical fixes. Use when Codex needs support for: Fix C++ build errors, CMake issues, and linker problems incrementally. Invokes the cpp-build-resolver agent for minimal, surgical fixes.

---

# C++ Build and Fix

This command invokes the **cpp-build-resolver** agent to incrementally fix C++ build errors with minimal changes.

## What This Command Does

1. **Run Diagnostics**: Execute `cmake --build`, `clang-tidy`, `cppcheck`
2. **Parse Errors**: Group by file and sort by severity
3. **Fix Incrementally**: One error at a time
4. **Verify Each Fix**: Re-run build after each change
5. **Report Summary**: Show what was fixed and what remains

## When to Use

use the Codex prompt recipe equivalent for `cpp-build` when:
- `cmake --build build` fails with errors
- Linker errors (undefined references, multiple definitions)
- Template instantiation failures
- Include/dependency issues
- After pulling changes that break the build

## Diagnostic Commands Run

```bash
# CMake configure
cmake -B build -S .

# Build
cmake --build build 2>&1 | head -100

# Static analysis (if available)
clang-tidy src/*.cpp -- -std=c++17
cppcheck --enable=all src/
```

## Example Session

```text
User: /cpp-build

Agent:
# C++ Build Resolution

## Initial Diagnostics

```bash
$ cmake --build build
src/service/user.cpp:25:15: error: use of undeclared identifier 'UserRepository'
src/handler/api.cpp:42:9: error: no matching function for call to 'process'
src/handler/api.cpp:58:1: error: non-void function does not return a value
```

Errors found: 3

## Fix 1: Undeclared Identifier

File: src/service/user.cpp:25
Error: use of undeclared identifier 'UserRepository'
Cause: Missing include

```cpp
// Added include
#include "repository/user_repository.hpp"
```

```bash
$ cmake --build build
# 2 errors remaining
```

## Fix 2: No Matching Function

File: src/handler/api.cpp:42
Error: no matching function for call to 'process'

```cpp
// Changed
process(params.get("count"));
// To
process(std::stoi(params.get("count")));
```

```bash
$ cmake --build build
# 1 error remaining
```

## Fix 3: Missing Return

File: src/handler/api.cpp:58
Error: non-void function does not return a value

```cpp
std::optional<User> getUser(const std::string& id) {
    if (id.empty()) {
        return std::nullopt;
    }
    auto user = findUser(id);
    // Added missing return
    return user;
}
```

```bash
$ cmake --build build
# Build successful!
```

## Final Verification

```bash
$ ctest --test-dir build --output-on-failure
Test project build
    1/5 Test #1: unit_tests ........   Passed    0.02 sec
    2/5 Test #2: integration_tests    Passed    0.15 sec
All tests passed.
```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Linker errors fixed | 0 |
| Files modified | 2 |
| Remaining issues | 0 |

Build Status: PASS: SUCCESS
```

## Common Errors Fixed

| Error | Typical Fix |
|-------|-------------|
| `undeclared identifier` | Add `#include` or fix typo |
| `no matching function` | Fix argument types or add overload |
| `undefined reference` | Link library or add implementation |
| `multiple definition` | Use `inline` or move to .cpp |
| `incomplete type` | Replace forward decl with `#include` |
| `no member named X` | Fix member name or include |
| `cannot convert X to Y` | Add appropriate cast |
| `CMake Error` | Fix CMakeLists.txt configuration |

## Fix Strategy

1. **Compilation errors first** - Code must compile
2. **Linker errors second** - Resolve undefined references
3. **Warnings third** - Fix with `-Wall -Wextra`
4. **One fix at a time** - Verify each change
5. **Minimal changes** - Don't refactor, just fix

## Stop Conditions

The agent will stop and report if:
- Same error persists after 3 attempts
- Fix introduces more errors
- Requires architectural changes
- Missing external dependencies

## Related Commands

- `/cpp-test` - Run tests after build succeeds
- `/cpp-review` - Review code quality
- `/verify` - Full verification loop

## Related

- Agent: `agents/cpp-build-resolver.md`
- Skill: `skills/cpp-coding-standards/`
