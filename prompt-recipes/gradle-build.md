# Gradle Build Prompt Recipe

## Codex invocation

Ask Codex to execute the `gradle-build` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Gradle Build Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `gradle-build` prompt recipe for <task>."

**Original command intent:** Fix Gradle build errors for Android and KMP projects. Use when Codex needs support for: Fix Gradle build errors for Android and KMP projects.

---

# Gradle Build Fix

Incrementally fix Gradle build and compilation errors for Android and Kotlin Multiplatform projects.

## Step 1: Detect Build Configuration

Identify the project type and run the appropriate build:

| Indicator | Build Command |
|-----------|---------------|
| `build.gradle.kts` + `composeApp/` (KMP) | `./gradlew composeApp:compileKotlinMetadata 2>&1` |
| `build.gradle.kts` + `app/` (Android) | `./gradlew app:compileDebugKotlin 2>&1` |
| `settings.gradle.kts` with modules | `./gradlew assemble 2>&1` |
| Detekt configured | `./gradlew detekt 2>&1` |

Also check `gradle.properties` and `local.properties` for configuration.

## Step 2: Parse and Group Errors

1. Run the build command and capture output
2. Separate Kotlin compilation errors from Gradle configuration errors
3. Group by module and file path
4. Sort: configuration errors first, then compilation errors by dependency order

## Step 3: Fix Loop

For each error:

1. **Read the file** — Full context around the error line
2. **Diagnose** — Common categories:
   - Missing import or unresolved reference
   - Type mismatch or incompatible types
   - Missing dependency in `build.gradle.kts`
   - Expect/actual mismatch (KMP)
   - Compose compiler error
3. **Fix minimally** — Smallest change that resolves the error
4. **Re-run build** — Verify fix and check for new errors
5. **Continue** — Move to next error

## Step 4: Guardrails

Stop and ask the user if:
- Fix introduces more errors than it resolves
- Same error persists after 3 attempts
- Error requires adding new dependencies or changing module structure
- Gradle sync itself fails (configuration-phase error)
- Error is in generated code (Room, SQLDelight, KSP)

## Step 5: Summary

Report:
- Errors fixed (module, file, description)
- Errors remaining
- New errors introduced (should be zero)
- Suggested next steps

## Common Gradle/KMP Fixes

| Error | Fix |
|-------|-----|
| Unresolved reference in `commonMain` | Check if the dependency is in `commonMain.dependencies {}` |
| Expect declaration without actual | Add `actual` implementation in each platform source set |
| Compose compiler version mismatch | Align Kotlin and Compose compiler versions in `libs.versions.toml` |
| Duplicate class | Check for conflicting dependencies with `./gradlew dependencies` |
| KSP error | Run `./gradlew kspCommonMainKotlinMetadata` to regenerate |
| Configuration cache issue | Check for non-serializable task inputs |
