# Jira Prompt Recipe

## Codex invocation

Ask Codex to execute the `jira` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Jira Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `jira` prompt recipe for <task>."

**Original command intent:** Retrieve a Jira ticket, analyze requirements, update status, or add comments. Uses the jira-integration skill and MCP or REST API. Use when Codex needs support for: Retrieve a Jira ticket, analyze requirements, update status, or add comments. Uses the jira-integration skill and MCP or REST API.

---

# Jira Command

Interact with Jira tickets directly from your workflow — fetch tickets, analyze requirements, add comments, and transition status.

## Usage

```
Codex prompt recipe equivalent: ask Codex to execute the `jira` workflow with arguments `get <TICKET-KEY>          # Fetch and analyze a ticket`.
Codex prompt recipe equivalent: ask Codex to execute the `jira` workflow with arguments `comment <TICKET-KEY>      # Add a progress comment`.
Codex prompt recipe equivalent: ask Codex to execute the `jira` workflow with arguments `transition <TICKET-KEY>   # Change ticket status`.
Codex prompt recipe equivalent: ask Codex to execute the `jira` workflow with arguments `search <JQL>              # Search issues with JQL`.
```

## What This Command Does

1. **Get & Analyze** — Fetch a Jira ticket and extract requirements, acceptance criteria, test scenarios, and dependencies
2. **Comment** — Add structured progress updates to a ticket
3. **Transition** — Move a ticket through workflow states (To Do → In Progress → Done)
4. **Search** — Find issues using JQL queries

## How It Works

### `/jira get <TICKET-KEY>`

1. Fetch the ticket from Jira (via MCP `jira_get_issue` or REST API)
2. Extract all fields: summary, description, acceptance criteria, priority, labels, linked issues
3. Optionally fetch comments for additional context
4. Produce a structured analysis:

```
Ticket: PROJ-1234
Summary: [title]
Status: [status]
Priority: [priority]
Type: [Story/Bug/Task]

Requirements:
1. [extracted requirement]
2. [extracted requirement]

Acceptance Criteria:
- [ ] [criterion from ticket]

Test Scenarios:
- Happy Path: [description]
- Error Case: [description]
- Edge Case: [description]

Dependencies:
- [linked issues, APIs, services]

Recommended Next Steps:
- the plan prompt recipe to create implementation plan
- the tdd-workflow skill to implement with tests first
```

### `/jira comment <TICKET-KEY>`

1. Summarize current session progress (what was built, tested, committed)
2. Format as a structured comment
3. Post to the Jira ticket

### `/jira transition <TICKET-KEY>`

1. Fetch available transitions for the ticket
2. Show options to user
3. Execute the selected transition

### `/jira search <JQL>`

1. Execute the JQL query against Jira
2. Return a summary table of matching issues

## Prerequisites

This command requires Jira credentials. Choose one:

**Option A — MCP Server (recommended):**
Add `jira` to your `mcpServers` config (see `mcp-configs/mcp-servers.json` for the template).

**Option B — Environment variables:**
```bash
export JIRA_URL="https://yourorg.atlassian.net"
export JIRA_EMAIL="your.email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

If credentials are missing, stop and direct the user to set them up.

## Integration with Other Commands

After analyzing a ticket:
- Use `the plan prompt recipe` to create an implementation plan from the requirements
- Use `the tdd-workflow skill` to implement with test-driven development
- use the Codex prompt recipe equivalent for `code-review` after implementation
- use the Codex prompt recipe equivalent for `jira` comment to post progress back to the ticket
- use the Codex prompt recipe equivalent for `jira` transition to move the ticket when work is complete

## Related

- **Skill:** `skills/jira-integration/`
- **MCP config:** `mcp-configs/mcp-servers.json` → `jira`
