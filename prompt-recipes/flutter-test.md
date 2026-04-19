# Flutter Test Prompt Recipe

## Codex invocation

Ask Codex to execute the `flutter-test` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Flutter Test Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `flutter-test` prompt recipe for <task>."

**Original command intent:** Run Flutter/Dart tests, report failures, and incrementally fix test issues. Covers unit, widget, golden, and integration tests. Use when Codex needs support for: Run Flutter/Dart tests, report failures, and incrementally fix test issues. Covers unit, widget, golden, and integration tests.

---

# Flutter Test

This command runs the Flutter test suite and reports results. When failures occur, it diagnoses and fixes issues incrementally.

## What This Command Does

1. **Run Tests**: Execute `flutter test` (or scope to changed files)
2. **Parse Failures**: Identify failing tests by type and cause
3. **Fix Incrementally**: One failure at a time where possible
4. **Verify**: Re-run after each fix
5. **Report**: Show coverage summary and remaining failures

## When to Use

use the Codex prompt recipe equivalent for `flutter-test` when:
- After implementing a feature to verify nothing broke
- After running `/flutter-build` to ensure tests pass
- To check test coverage on new code
- When a specific test file is failing
- Before submitting a PR

## Commands Run

```bash
# Run all tests
flutter test 2>&1

# Run with coverage
flutter test --coverage 2>&1

# Run specific test file
flutter test test/unit/domain/usecases/get_user_test.dart 2>&1

# Run tests matching a name pattern
flutter test --name "CartBloc" 2>&1

# Run integration tests (requires device/emulator)
flutter test integration_test/ 2>&1

# Update golden files when intentional visual changes are made
flutter test --update-goldens 2>&1
```

## Example Session

````text
User: /flutter-test

Agent:
# Flutter Test Run

## Test Execution

```
$ flutter test
00:05 +42 -2: Some tests failed.

FAILED: test/unit/data/user_repository_test.dart
  UserRepository getById
    returns null when user not found
    Expected: null
    Actual: User(id: 'test-id', name: 'Test User')

FAILED: test/widget/cart_page_test.dart
  CartPage
    shows empty state when cart is empty
    Expected: exactly one widget with text 'Your cart is empty'
    Found: no widget with text 'Your cart is empty'
```

## Fix 1: Repository Test

File: test/unit/data/user_repository_test.dart
Failure: `getById` returns a user when it should return null for missing ID

Root cause: Test setup adds a user with ID 'test-id' but queries with 'missing-id'.
Fix: Updated test to query with 'missing-id' — setup was correct, query was wrong.

```
$ flutter test test/unit/data/user_repository_test.dart
1 test passed.
```

## Fix 2: Widget Test

File: test/widget/cart_page_test.dart
Failure: Empty state text widget not found

Root cause: Empty state message was renamed from 'Your cart is empty' to 'Cart is empty' in the widget.
Fix: Updated test string to match current widget copy.

```
$ flutter test test/widget/cart_page_test.dart
1 test passed.
```

## Final Run

```
$ flutter test --coverage
All 44 tests passed.
Coverage: 84.2% (target: 80%)
```

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 44 |
| Passed | 44 |
| Failed | 0 |
| Coverage | 84.2% |

Test Status: PASS ✓
````

## Common Test Failures

| Failure | Typical Fix |
|---------|-------------|
| `Expected: <X> Actual: <Y>` | Update assertion or fix implementation |
| `Widget not found` | Fix finder selector or update test after widget rename |
| `Golden file not found` | Run `flutter test --update-goldens` to generate |
| `Golden mismatch` | Inspect diff; run `--update-goldens` if change was intentional |
| `MissingPluginException` | Mock platform channel in test setup |
| `LateInitializationError` | Initialize `late` fields in `setUp()` |
| `pumpAndSettle timed out` | Replace with explicit `pump(Duration)` calls |

## Related Commands

- `/flutter-build` — Fix build errors before running tests
- `/flutter-review` — Review code after tests pass
- `the tdd-workflow skill` — Test-driven development workflow

## Related

- Agent: `agents/flutter-reviewer.md`
- Agent: `agents/dart-build-resolver.md`
- Skill: `skills/flutter-dart-code-review/`
- Rules: `rules/dart/testing.md`
