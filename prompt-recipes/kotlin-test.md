# Kotlin Test Prompt Recipe

## Codex invocation

Ask Codex to execute the `kotlin-test` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Kotlin Test Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `kotlin-test` prompt recipe for <task>."

**Original command intent:** Enforce TDD workflow for Kotlin. Write Kotest tests first, then implement. Verify 80%+ coverage with Kover. Use when Codex needs support for: Enforce TDD workflow for Kotlin. Write Kotest tests first, then implement. Verify 80%+ coverage with Kover.

---

# Kotlin TDD Command

This command enforces test-driven development methodology for Kotlin code using Kotest, MockK, and Kover.

## What This Command Does

1. **Define Types/Interfaces**: Scaffold function signatures first
2. **Write Kotest Tests**: Create comprehensive test specs (RED)
3. **Run Tests**: Verify tests fail for the right reason
4. **Implement Code**: Write minimal code to pass (GREEN)
5. **Refactor**: Improve while keeping tests green
6. **Check Coverage**: Ensure 80%+ coverage with Kover

## When to Use

use the Codex prompt recipe equivalent for `kotlin-test` when:
- Implementing new Kotlin functions or classes
- Adding test coverage to existing Kotlin code
- Fixing bugs (write failing test first)
- Building critical business logic
- Learning TDD workflow in Kotlin

## TDD Cycle

```
RED     -> Write failing Kotest test
GREEN   -> Implement minimal code to pass
REFACTOR -> Improve code, tests stay green
REPEAT  -> Next test case
```

## Example Session

````text
User: /kotlin-test I need a function to validate user registration requests

Agent:
# TDD Session: Registration Validator

## Step 1: Define Interface

```kotlin
// validator/RegistrationValidator.kt
package com.example.validator

data class RegistrationRequest(
    val name: String,
    val email: String,
    val password: String,
)

sealed class ValidationResult {
    data object Valid : ValidationResult()
    data class Invalid(val errors: List<String>) : ValidationResult()
}

fun validateRegistration(request: RegistrationRequest): ValidationResult {
    TODO("not implemented")
}
```

## Step 2: Write Kotest Tests (RED)

```kotlin
// validator/RegistrationValidatorTest.kt
package com.example.validator

import io.kotest.core.spec.style.FunSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.types.shouldBeInstanceOf

class RegistrationValidatorTest : FunSpec({
    test("valid registration returns Valid") {
        val request = RegistrationRequest(
            name = "Alice",
            email = "alice@example.com",
            password = "SecureP@ss1",
        )

        val result = validateRegistration(request)

        result.shouldBeInstanceOf<ValidationResult.Valid>()
    }

    test("blank name returns Invalid") {
        val request = RegistrationRequest(
            name = "",
            email = "alice@example.com",
            password = "SecureP@ss1",
        )

        val result = validateRegistration(request)

        val invalid = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("Name is required")
    }

    test("invalid email returns Invalid") {
        val request = RegistrationRequest(
            name = "Alice",
            email = "not-an-email",
            password = "SecureP@ss1",
        )

        val result = validateRegistration(request)

        val invalid = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("Invalid email format")
    }

    test("short password returns Invalid") {
        val request = RegistrationRequest(
            name = "Alice",
            email = "alice@example.com",
            password = "short",
        )

        val result = validateRegistration(request)

        val invalid = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("Password must be at least 8 characters")
    }

    test("multiple errors returns all errors") {
        val request = RegistrationRequest(
            name = "",
            email = "bad",
            password = "short",
        )

        val result = validateRegistration(request)

        val invalid = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors.size shouldBe 3
    }
})
```

## Step 3: Run Tests - Verify FAIL

```bash
$ ./gradlew test

RegistrationValidatorTest > valid registration returns Valid FAILED
  kotlin.NotImplementedError: An operation is not implemented

FAILED (5 tests, 0 passed, 5 failed)
```

✓ Tests fail as expected (NotImplementedError).

## Step 4: Implement Minimal Code (GREEN)

```kotlin
// validator/RegistrationValidator.kt
package com.example.validator

private val EMAIL_REGEX = Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
private const val MIN_PASSWORD_LENGTH = 8

fun validateRegistration(request: RegistrationRequest): ValidationResult {
    val errors = buildList {
        if (request.name.isBlank()) add("Name is required")
        if (!EMAIL_REGEX.matches(request.email)) add("Invalid email format")
        if (request.password.length < MIN_PASSWORD_LENGTH) add("Password must be at least $MIN_PASSWORD_LENGTH characters")
    }

    return if (errors.isEmpty()) ValidationResult.Valid
    else ValidationResult.Invalid(errors)
}
```

## Step 5: Run Tests - Verify PASS

```bash
$ ./gradlew test

RegistrationValidatorTest > valid registration returns Valid PASSED
RegistrationValidatorTest > blank name returns Invalid PASSED
RegistrationValidatorTest > invalid email returns Invalid PASSED
RegistrationValidatorTest > short password returns Invalid PASSED
RegistrationValidatorTest > multiple errors returns all errors PASSED

PASSED (5 tests, 5 passed, 0 failed)
```

✓ All tests passing!

## Step 6: Check Coverage

```bash
$ ./gradlew koverHtmlReport

Coverage: 100.0% of statements
```

✓ Coverage: 100%

## TDD Complete!
````

## Test Patterns

### StringSpec (Simplest)

```kotlin
class CalculatorTest : StringSpec({
    "add two positive numbers" {
        Calculator.add(2, 3) shouldBe 5
    }
})
```

### BehaviorSpec (BDD)

```kotlin
class OrderServiceTest : BehaviorSpec({
    Given("a valid order") {
        When("placed") {
            Then("should be confirmed") { /* ... */ }
        }
    }
})
```

### Data-Driven Tests

```kotlin
class ParserTest : FunSpec({
    context("valid inputs") {
        withData("2026-01-15", "2026-12-31", "2000-01-01") { input ->
            parseDate(input).shouldNotBeNull()
        }
    }
})
```

### Coroutine Testing

```kotlin
class AsyncServiceTest : FunSpec({
    test("concurrent fetch completes") {
        runTest {
            val result = service.fetchAll()
            result.shouldNotBeEmpty()
        }
    }
})
```

## Coverage Commands

```bash
# Run tests with coverage
./gradlew koverHtmlReport

# Verify coverage thresholds
./gradlew koverVerify

# XML report for CI
./gradlew koverXmlReport

# Open HTML report
open build/reports/kover/html/index.html

# Run specific test class
./gradlew test --tests "com.example.UserServiceTest"

# Run with verbose output
./gradlew test --info
```

## Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated code | Exclude |

## TDD Best Practices

**DO:**
- Write test FIRST, before any implementation
- Run tests after each change
- Use Kotest matchers for expressive assertions
- Use MockK's `coEvery`/`coVerify` for suspend functions
- Test behavior, not implementation details
- Include edge cases (empty, null, max values)

**DON'T:**
- Write implementation before tests
- Skip the RED phase
- Test private functions directly
- Use `Thread.sleep()` in coroutine tests
- Ignore flaky tests

## Related Commands

- `/kotlin-build` - Fix build errors
- `/kotlin-review` - Review code after implementation
- `/verify` - Run full verification loop

## Related

- Skill: `skills/kotlin-testing/`
- Skill: `skillsthe tdd-workflow skill-workflow/`
