# Test Coverage Prompt Recipe

## Codex invocation

Ask Codex to execute the `test-coverage` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Test Coverage Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `test-coverage` prompt recipe for <task>."

**Original command intent:** test coverage. Use when Codex needs support for: test coverage.

---

# Test Coverage

Analyze test coverage, identify gaps, and generate missing tests to reach 80%+ coverage.

## Step 1: Detect Test Framework

| Indicator | Coverage Command |
|-----------|-----------------|
| `jest.config.*` or `package.json` jest | `npx jest --coverage --coverageReporters=json-summary` |
| `vitest.config.*` | `npx vitest run --coverage` |
| `pytest.ini` / `pyproject.toml` pytest | `pytest --cov=src --cov-report=json` |
| `Cargo.toml` | `cargo llvm-cov --json` |
| `pom.xml` with JaCoCo | `mvn test jacoco:report` |
| `go.mod` | `go test -coverprofile=coverage.out ./...` |

## Step 2: Analyze Coverage Report

1. Run the coverage command
2. Parse the output (JSON summary or terminal output)
3. List files **below 80% coverage**, sorted worst-first
4. For each under-covered file, identify:
   - Untested functions or methods
   - Missing branch coverage (if/else, switch, error paths)
   - Dead code that inflates the denominator

## Step 3: Generate Missing Tests

For each under-covered file, generate tests following this priority:

1. **Happy path** — Core functionality with valid inputs
2. **Error handling** — Invalid inputs, missing data, network failures
3. **Edge cases** — Empty arrays, null/undefined, boundary values (0, -1, MAX_INT)
4. **Branch coverage** — Each if/else, switch case, ternary

### Test Generation Rules

- Place tests adjacent to source: `foo.ts` → `foo.test.ts` (or project convention)
- Use existing test patterns from the project (import style, assertion library, mocking approach)
- Mock external dependencies (database, APIs, file system)
- Each test should be independent — no shared mutable state between tests
- Name tests descriptively: `test_create_user_with_duplicate_email_returns_409`

## Step 4: Verify

1. Run the full test suite — all tests must pass
2. Re-run coverage — verify improvement
3. If still below 80%, repeat Step 3 for remaining gaps

## Step 5: Report

Show before/after comparison:

```
Coverage Report
──────────────────────────────
File                   Before  After
src/services/auth.ts   45%     88%
src/utils/validation.ts 32%    82%
──────────────────────────────
Overall:               67%     84%  PASS:
```

## Focus Areas

- Functions with complex branching (high cyclomatic complexity)
- Error handlers and catch blocks
- Utility functions used across the codebase
- API endpoint handlers (request → response flow)
- Edge cases: null, undefined, empty string, empty array, zero, negative numbers
