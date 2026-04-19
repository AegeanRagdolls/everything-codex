# Resume Session Prompt Recipe

## Codex invocation

Ask Codex to execute the `resume-session` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Resume Session Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `resume-session` prompt recipe for <task>."

**Original command intent:** Load the most recent session file from ~/.claude/session-data/ and resume work with full context from where the last session ended. Use when Codex needs support for: Load the most recent session file from ~/.claude/session-data/ and resume work with full context from where the last session ended.

---

# Resume Session Command

Load the last saved session state and orient fully before doing any work.
This command is the counterpart to `/save-session`.

## When to Use

- Starting a new session to continue work from a previous day
- After starting a fresh session due to context limits
- When handing off a session file from another source (just provide the file path)
- Any time you have a session file and want Claude to fully absorb it before proceeding

## Usage

```
Codex prompt recipe equivalent: ask Codex to execute the `resume-session` workflow with arguments `# loads most recent file in ~/.claude/session-data/`.
Codex prompt recipe equivalent: ask Codex to execute the `resume-session` workflow with arguments `2024-01-15                                           # loads most recent session for that date`.
Codex prompt recipe equivalent: ask Codex to execute the `resume-session` workflow with arguments `~/.claude/session-data/2024-01-15-abc123de-session.tmp  # loads a current short-id session file`.
Codex prompt recipe equivalent: ask Codex to execute the `resume-session` workflow with arguments `~/.claude/sessions/2024-01-15-session.tmp               # loads a specific legacy-format file`.
```

## Process

### Step 1: Find the session file

If no argument provided:

1. Check `~/.claude/session-data/`
2. Pick the most recently modified `*-session.tmp` file
3. If the folder does not exist or has no matching files, tell the user:
   ```
   No session files found in ~/.claude/session-data/
   Run /save-session at the end of a session to create one.
   ```
   Then stop.

If an argument is provided:

- If it looks like a date (`YYYY-MM-DD`), search `~/.claude/session-data/` first, then the legacy
  `~/.claude/sessions/`, for files matching `YYYY-MM-DD-session.tmp` (legacy format) or
  `YYYY-MM-DD-<shortid>-session.tmp` (current format)
  and load the most recently modified variant for that date
- If it looks like a file path, read that file directly
- If not found, report clearly and stop

### Step 2: Read the entire session file

Read the complete file. Do not summarize yet.

### Step 3: Confirm understanding

Respond with a structured briefing in this exact format:

```
SESSION LOADED: [actual resolved path to the file]
════════════════════════════════════════════════

PROJECT: [project name / topic from file]

WHAT WE'RE BUILDING:
[2-3 sentence summary in your own words]

CURRENT STATE:
PASS: Working: [count] items confirmed
 In Progress: [list files that are in progress]
 Not Started: [list planned but untouched]

WHAT NOT TO RETRY:
[list every failed approach with its reason — this is critical]

OPEN QUESTIONS / BLOCKERS:
[list any blockers or unanswered questions]

NEXT STEP:
[exact next step if defined in the file]
[if not defined: "No next step defined — recommend reviewing 'What Has NOT Been Tried Yet' together before starting"]

════════════════════════════════════════════════
Ready to continue. What would you like to do?
```

### Step 4: Wait for the user

Do NOT start working automatically. Do NOT touch any files. Wait for the user to say what to do next.

If the next step is clearly defined in the session file and the user says "continue" or "yes" or similar — proceed with that exact next step.

If no next step is defined — ask the user where to start, and optionally suggest an approach from the "What Has NOT Been Tried Yet" section.

---

## Edge Cases

**Multiple sessions for the same date** (`2024-01-15-session.tmp`, `2024-01-15-abc123de-session.tmp`):
Load the most recently modified matching file for that date, regardless of whether it uses the legacy no-id format or the current short-id format.

**Session file references files that no longer exist:**
Note this during the briefing — "WARNING: `path/to/file.ts` referenced in session but not found on disk."

**Session file is from more than 7 days ago:**
Note the gap — "WARNING: This session is from N days ago (threshold: 7 days). Things may have changed." — then proceed normally.

**User provides a file path directly (e.g., forwarded from a teammate):**
Read it and follow the same briefing process — the format is the same regardless of source.

**Session file is empty or malformed:**
Report: "Session file found but appears empty or unreadable. You may need to create a new one with /save-session."

---

## Example Output

```
SESSION LOADED: /Users/you/.claude/session-data/2024-01-15-abc123de-session.tmp
════════════════════════════════════════════════

PROJECT: my-app — JWT Authentication

WHAT WE'RE BUILDING:
User authentication with JWT tokens stored in httpOnly cookies.
Register and login endpoints are partially done. Route protection
via middleware hasn't been started yet.

CURRENT STATE:
PASS: Working: 3 items (register endpoint, JWT generation, password hashing)
 In Progress: app/api/auth/login/route.ts (token works, cookie not set yet)
 Not Started: middleware.ts, app/login/page.tsx

WHAT NOT TO RETRY:
FAIL: Next-Auth — conflicts with custom Prisma adapter, threw adapter error on every request
FAIL: localStorage for JWT — causes SSR hydration mismatch, incompatible with Next.js

OPEN QUESTIONS / BLOCKERS:
- Does cookies().set() work inside a Route Handler or only Server Actions?

NEXT STEP:
In app/api/auth/login/route.ts — set the JWT as an httpOnly cookie using
cookies().set('token', jwt, { httpOnly: true, secure: true, sameSite: 'strict' })
then test with Postman for a Set-Cookie header in the response.

════════════════════════════════════════════════
Ready to continue. What would you like to do?
```

---

## Notes

- Never modify the session file when loading it — it's a read-only historical record
- The briefing format is fixed — do not skip sections even if they are empty
- "What Not To Retry" must always be shown, even if it just says "None" — it's too important to miss
- After resuming, the user may want to run `/save-session` again at the end of the new session to create a new dated file
