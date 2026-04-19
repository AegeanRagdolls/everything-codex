# Feature Dev Prompt Recipe

## Codex invocation

Ask Codex to execute the `feature-dev` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Feature Dev Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `feature-dev` prompt recipe for <task>."

**Original command intent:** Guided feature development with codebase understanding and architecture focus. Use when Codex needs support for: Guided feature development with codebase understanding and architecture focus.

---

A structured feature-development workflow that emphasizes understanding existing code before writing new code.

## Phases

### 1. Discovery

- read the feature request carefully
- identify requirements, constraints, and acceptance criteria
- ask clarifying questions if the request is ambiguous

### 2. Codebase Exploration

- use `code-explorer` to analyze the relevant existing code
- trace execution paths and architecture layers
- understand integration points and conventions

### 3. Clarifying Questions

- present findings from exploration
- ask targeted design and edge-case questions
- wait for user response before proceeding

### 4. Architecture Design

- use `code-architect` to design the feature
- provide the implementation blueprint
- wait for approval before implementing

### 5. Implementation

- implement the feature following the approved design
- prefer TDD where appropriate
- keep commits small and focused

### 6. Quality Review

- use `code-reviewer` to review the implementation
- address critical and important issues
- verify test coverage

### 7. Summary

- summarize what was built
- list follow-up items or limitations
- provide testing instructions
