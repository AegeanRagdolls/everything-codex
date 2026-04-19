# Multi Backend Prompt Recipe

## Codex invocation

Ask Codex to execute the `multi-backend` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Multi Backend Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `multi-backend` prompt recipe for <task>."

**Original command intent:** multi backend. Use when Codex needs support for: multi backend.

---

# Backend - Backend-Focused Development

Backend-focused workflow (Research → Ideation → Plan → Execute → Optimize → Review), Codex-led.

## Usage

```bash
Codex prompt recipe equivalent: ask Codex to execute the `backend` workflow with arguments `<backend task description>`.
```

## Context

- Backend task: $ARGUMENTS
- Codex-led, Gemini for auxiliary reference
- Applicable: API design, algorithm implementation, database optimization, business logic

## Your Role

You are the **Backend Orchestrator**, coordinating multi-model collaboration for server-side tasks (Research → Ideation → Plan → Execute → Optimize → Review).

**Collaborative Models**:
- **Codex** – Backend logic, algorithms (**Backend authority, trustworthy**)
- **Gemini** – Frontend perspective (**Backend opinions for reference only**)
- **Claude (self)** – Orchestration, planning, execution, delivery

---

## Multi-Model Call Specification

**Call Syntax**:

```
# New session call
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend codex - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <enhanced requirement (or $ARGUMENTS if not enhanced)>
Context: <project context and analysis from previous phases>
</TASK>
OUTPUT: Expected output format
EOF",
  run_in_background: false,
  timeout: 3600000,
  description: "Brief description"
})

# Resume session call
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend codex resume <SESSION_ID> - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <enhanced requirement (or $ARGUMENTS if not enhanced)>
Context: <project context and analysis from previous phases>
</TASK>
OUTPUT: Expected output format
EOF",
  run_in_background: false,
  timeout: 3600000,
  description: "Brief description"
})
```

**Role Prompts**:

| Phase | Codex |
|-------|-------|
| Analysis | `~/.claude/.ccg/prompts/codex/analyzer.md` |
| Planning | `~/.claude/.ccg/prompts/codex/architect.md` |
| Review | `~/.claude/.ccg/prompts/codex/reviewer.md` |

**Session Reuse**: Each call returns `SESSION_ID: xxx`, use `resume xxx` for subsequent phases. Save `CODEX_SESSION` in Phase 2, use `resume` in Phases 3 and 5.

---

## Communication Guidelines

1. Start responses with mode label `[Mode: X]`, initial is `[Mode: Research]`
2. Follow strict sequence: `Research → Ideation → Plan → Execute → Optimize → Review`
3. Use `AskUserQuestion` tool for user interaction when needed (e.g., confirmation/selection/approval)

---

## Core Workflow

### Phase 0: Prompt Enhancement (Optional)

`[Mode: Prepare]` - If ace-tool MCP available, call `mcp__ace-tool__enhance_prompt`, **replace original $ARGUMENTS with enhanced result for subsequent Codex calls**. If unavailable, use `$ARGUMENTS` as-is.

### Phase 1: Research

`[Mode: Research]` - Understand requirements and gather context

1. **Code Retrieval** (if ace-tool MCP available): Call `mcp__ace-tool__search_context` to retrieve existing APIs, data models, service architecture. If unavailable, use built-in tools: `Glob` for file discovery, `Grep` for symbol/API search, `Read` for context gathering, `Task` (Explore agent) for deeper exploration.
2. Requirement completeness score (0-10): >=7 continue, <7 stop and supplement

### Phase 2: Ideation

`[Mode: Ideation]` - Codex-led analysis

**MUST call Codex** (follow call specification above):
- ROLE_FILE: `~/.claude/.ccg/prompts/codex/analyzer.md`
- Requirement: Enhanced requirement (or $ARGUMENTS if not enhanced)
- Context: Project context from Phase 1
- OUTPUT: Technical feasibility analysis, recommended solutions (at least 2), risk assessment

**Save SESSION_ID** (`CODEX_SESSION`) for subsequent phase reuse.

Output solutions (at least 2), wait for user selection.

### Phase 3: Planning

`[Mode: Plan]` - Codex-led planning

**MUST call Codex** (use `resume <CODEX_SESSION>` to reuse session):
- ROLE_FILE: `~/.claude/.ccg/prompts/codex/architect.md`
- Requirement: User's selected solution
- Context: Analysis results from Phase 2
- OUTPUT: File structure, function/class design, dependency relationships

Claude synthesizes plan, save to `.claudethe plan prompt recipe/task-name.md` after user approval.

### Phase 4: Implementation

`[Mode: Execute]` - Code development

- Strictly follow approved plan
- Follow existing project code standards
- Ensure error handling, security, performance optimization

### Phase 5: Optimization

`[Mode: Optimize]` - Codex-led review

**MUST call Codex** (follow call specification above):
- ROLE_FILE: `~/.claude/.ccg/prompts/codex/reviewer.md`
- Requirement: Review the following backend code changes
- Context: git diff or code content
- OUTPUT: Security, performance, error handling, API compliance issues list

Integrate review feedback, execute optimization after user confirmation.

### Phase 6: Quality Review

`[Mode: Review]` - Final evaluation

- Check completion against plan
- Run tests to verify functionality
- Report issues and recommendations

---

## Key Rules

1. **Codex backend opinions are trustworthy**
2. **Gemini backend opinions for reference only**
3. External models have **zero filesystem write access**
4. Claude handles all code writes and file operations
