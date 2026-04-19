# E2E Prompt Recipe

## Codex invocation

Ask Codex to execute the `e2e` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# E2E Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `e2e` prompt recipe for <task>."

**Original command intent:** Legacy slash-entry shim for the e2e-testing skill. Prefer the skill directly. Use when Codex needs support for: Legacy slash-entry shim for the e2e-testing skill. Prefer the skill directly.

---

# E2E Command (Legacy Shim)

Use this only if you still invoke `/e2e`. The maintained workflow lives in `skills/e2e-testing/SKILL.md`.

## Canonical Surface

- Prefer the `e2e-testing` skill directly.
- Keep this file only as a compatibility entry point.

## Arguments

`$ARGUMENTS`

## Delegation

Apply the `e2e-testing` skill.
- Generate or update Playwright coverage for the requested user flow.
- Run only the relevant tests unless the user explicitly asked for the entire suite.
- Capture the usual artifacts and report failures, flake risk, and next fixes without duplicating the full skill body here.
    await marketsPage.searchMarkets('xyznonexistentmarket123456')

    // Verify empty state
    await expect(page.locator('[data-testid="no-results"]')).toBeVisible()
    await expect(page.locator('[data-testid="no-results"]')).toContainText(
Codex prompt recipe equivalent: ask Codex to execute the `no.*results|no.*markets/i` workflow.
    )

    const marketCount = await marketsPage.marketCards.count()
    expect(marketCount).toBe(0)
  })

  test('can clear search and see all markets again', async ({ page }) => {
    const marketsPage = new MarketsPage(page)
    await marketsPage.goto()

    // Initial market count
    const initialCount = await marketsPage.marketCards.count()

    // Perform search
    await marketsPage.searchMarkets('trump')
    await page.waitForLoadState('networkidle')

    // Verify filtered results
    const filteredCount = await marketsPage.marketCards.count()
    expect(filteredCount).toBeLessThan(initialCount)

    // Clear search
    await marketsPage.searchInput.clear()
    await page.waitForLoadState('networkidle')

    // Verify all markets shown again
    const finalCount = await marketsPage.marketCards.count()
    expect(finalCount).toBe(initialCount)
  })
})
```

## Running Tests

```bash
# Run the generated test
npx playwright test tests/e2e/markets/search-and-view.spec.ts

Running 3 tests using 3 workers

  ✓  [chromium] › search-and-view.spec.ts:5:3 › user can search markets and view details (4.2s)
  ✓  [chromium] › search-and-view.spec.ts:52:3 › search with no results shows empty state (1.8s)
  ✓  [chromium] › search-and-view.spec.ts:67:3 › can clear search and see all markets again (2.9s)

  3 passed (9.1s)

Artifacts generated:
- artifacts/search-results.png
- artifacts/market-details.png
- playwright-report/index.html
```

## Test Report

```
╔══════════════════════════════════════════════════════════════╗
║                    E2E Test Results                          ║
╠══════════════════════════════════════════════════════════════╣
║ Status:     PASS: ALL TESTS PASSED                              ║
║ Total:      3 tests                                          ║
║ Passed:     3 (100%)                                         ║
║ Failed:     0                                                ║
║ Flaky:      0                                                ║
║ Duration:   9.1s                                             ║
╚══════════════════════════════════════════════════════════════╝

Artifacts:
 Screenshots: 2 files
 Videos: 0 files (only on failure)
 Traces: 0 files (only on failure)
 HTML Report: playwright-report/index.html

View report: npx playwright show-report
```

PASS: E2E test suite ready for CI/CD integration!
```

## Test Artifacts

When tests run, the following artifacts are captured:

**On All Tests:**
- HTML Report with timeline and results
- JUnit XML for CI integration

**On Failure Only:**
- Screenshot of the failing state
- Video recording of the test
- Trace file for debugging (step-by-step replay)
- Network logs
- Console logs

## Viewing Artifacts

```bash
# View HTML report in browser
npx playwright show-report

# View specific trace file
npx playwright show-trace artifacts/trace-abc123.zip

# Screenshots are saved in artifacts/ directory
open artifacts/search-results.png
```

## Flaky Test Detection

If a test fails intermittently:

```
WARNING:  FLAKY TEST DETECTED: tests/e2e/markets/trade.spec.ts

Test passed 7/10 runs (70% pass rate)

Common failure:
"Timeout waiting for element '[data-testid="confirm-btn"]'"

Recommended fixes:
1. Add explicit wait: await page.waitForSelector('[data-testid="confirm-btn"]')
2. Increase timeout: { timeout: 10000 }
3. Check for race conditions in component
4. Verify element is not hidden by animation

Quarantine recommendation: Mark as test.fixme() until fixed
```

## Browser Configuration

Tests run on multiple browsers by default:
- PASS: Chromium (Desktop Chrome)
- PASS: Firefox (Desktop)
- PASS: WebKit (Desktop Safari)
- PASS: Mobile Chrome (optional)

Configure in `playwright.config.ts` to adjust browsers.

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/e2e.yml
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npx playwright test

- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## PMX-Specific Critical Flows

For PMX, prioritize these E2E tests:

**CRITICAL (Must Always Pass):**
1. User can connect wallet
2. User can browse markets
3. User can search markets (semantic search)
4. User can view market details
5. User can place trade (with test funds)
6. Market resolves correctly
7. User can withdraw funds

**IMPORTANT:**
1. Market creation flow
2. User profile updates
3. Real-time price updates
4. Chart rendering
5. Filter and sort markets
6. Mobile responsive layout

## Best Practices

**DO:**
- PASS: Use Page Object Model for maintainability
- PASS: Use data-testid attributes for selectors
- PASS: Wait for API responses, not arbitrary timeouts
- PASS: Test critical user journeys end-to-end
- PASS: Run tests before merging to main
- PASS: Review artifacts when tests fail

**DON'T:**
- FAIL: Use brittle selectors (CSS classes can change)
- FAIL: Test implementation details
- FAIL: Run tests against production
- FAIL: Ignore flaky tests
- FAIL: Skip artifact review on failures
- FAIL: Test every edge case with E2E (use unit tests)

## Important Notes

**CRITICAL for PMX:**
- E2E tests involving real money MUST run on testnet/staging only
- Never run trading tests against production
- Set `test.skip(process.env.NODE_ENV === 'production')` for financial tests
- Use test wallets with small test funds only

## Integration with Other Commands

- Use `the plan prompt recipe` to identify critical journeys to test
- Use `the tdd-workflow skill` for unit tests (faster, more granular)
- use the Codex prompt recipe equivalent for `e2e` for integration and user journey tests
- use the Codex prompt recipe equivalent for `code-review` to verify test quality

## Related Agents

This command invokes the `e2e-runner` agent provided by ECC.

For manual installs, the source file lives at:
`agents/e2e-runner.md`

## Quick Commands

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/markets/search.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Debug test
npx playwright test --debug

# Generate test code
npx playwright codegen http://localhost:3000

# View report
npx playwright show-report
```
