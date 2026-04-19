# Aside Prompt Recipe

## Codex invocation

Ask Codex to execute the `aside` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Aside Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `aside` prompt recipe for <task>."

**Original command intent:** Answer a quick side question without interrupting or losing context from the current task. Resume work automatically after answering. Use when Codex needs support for: Answer a quick side question without interrupting or losing context from the current task. Resume work automatically after answering.

---

# Aside Command

Ask a question mid-task and get an immediate, focused answer — then continue right where you left off. The current task, files, and context are never modified.

## When to Use

- You're curious about something while Claude is working and don't want to lose momentum
- You need a quick explanation of code Claude is currently editing
- You want a second opinion or clarification on a decision without derailing the task
- You need to understand an error, concept, or pattern before Claude proceeds
- You want to ask something unrelated to the current task without starting a new session

## Usage

```
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `<your question>`.
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `what does this function actually return?`.
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `is this pattern thread-safe?`.
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `why are we using X instead of Y here?`.
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `what's the difference between foo() and bar()?`.
Codex prompt recipe equivalent: ask Codex to execute the `aside` workflow with arguments `should we be worried about the N+1 query we just added?`.
```

## Process

### Step 1: Freeze the current task state

Before answering anything, mentally note:
- What is the active task? (what file, feature, or problem was being worked on)
- What step was in progress at the moment `/aside` was invoked?
- What was about to happen next?

Do NOT touch, edit, create, or delete any files during the aside.

### Step 2: Answer the question directly

Answer the question in the most concise form that is still complete and useful.

- Lead with the answer, not the reasoning
- Keep it short — if a full explanation is needed, offer to go deeper after the task
- If the question is about the current file or code being worked on, reference it precisely (file path and line number if relevant)
- If answering requires reading a file, read it — but read only, never write

Format the response as:

```
ASIDE: [restate the question briefly]

[Your answer here]

— Back to task: [one-line description of what was being done]
```

### Step 3: Resume the main task

After delivering the answer, immediately continue the active task from the exact point it was paused. Do not ask for permission to resume unless the aside answer revealed a blocker or a reason to reconsider the current approach (see Edge Cases).

---

## Edge Cases

**No question provided (`/aside` with nothing after it):**
Respond:
```
ASIDE: no question provided

What would you like to know? (ask your question and I'll answer without losing the current task context)

— Back to task: [one-line description of what was being done]
```

**Question reveals a potential problem with the current task:**
Flag it clearly before resuming:
```
ASIDE: [answer]

WARNING: Note: This answer suggests [issue] with the current approach. Want to address this before continuing, or proceed as planned?
```
Wait for the user's decision before resuming.

**Question is actually a task redirect (not a side question):**
If the question implies changing what is being built (e.g., `/aside actually, let's use Redis instead`), clarify:
```
ASIDE: That sounds like a direction change, not just a side question.
Do you want to:
  (a) Answer this as information only and keep the current plan
  (b) Pause the current task and change approach
```
Wait for the user's answer — do not make assumptions.

**Question is about the currently open file or code:**
Answer from the live context. If the file was read earlier in the session, reference it directly. If not, read it now (read-only) and answer with a file:line reference.

**No active task (nothing in progress when `/aside` is invoked):**
Still use the standard wrapper so the response shape stays consistent:
```
ASIDE: [restate the question briefly]

[Your answer here]

— Back to task: no active task to resume
```

**Question requires a long answer:**
Give the essential answer concisely, then offer:
```
That's the short version. Want a deeper explanation after we finish [current task]?
```

**Multiple `/aside` questions in a row:**
Answer each one in sequence. After the last answer, resume the main task. Do not lose task state across a chain of asides.

**Aside answer implies a code change is needed:**
Note the change needed but do not make it during the aside:
```
ASIDE: [answer]

 Worth fixing: [what should be changed]. I'll flag this after the current task unless you want to address it now.
```

**Question is ambiguous or too vague:**
Ask one clarifying question — the shortest question that gets the information needed to answer. Do not ask multiple questions.

---

## Example Output

```
User: /aside what does fetchWithRetry() actually do?

ASIDE: what does fetchWithRetry() do?

fetchWithRetry() (src/api/retry.ts:12) attempts the request up to 3 times with
exponential backoff (250ms → 500ms → 1s). It only retries on 5xx responses and
network errors — 4xx errors are treated as final and not retried.

— Back to task: refactoring the auth middleware in src/middleware/auth.ts
```

```
User: /aside is the approach we're taking thread-safe?

ASIDE: is the current approach thread-safe?

No — the shared cache object in src/cache/store.ts:34 is mutated without locking.
Under concurrent requests this is a race condition. It's low risk in a single-process
Node.js server but would be a real problem with worker threads or clustering.

WARNING: Note: This could affect the feature we're building. Want to address this now or continue and fix it in a follow-up?
```

---

## Notes

- Never modify files during an aside — read-only access only
- The aside is a conversation pause, not a new task — the original task must always resume
- Keep answers focused: the goal is to unblock the user quickly, not to deliver a lecture
- If an aside sparks a larger discussion, finish the current task first unless the aside reveals a blocker
- Asides are not saved to session files unless explicitly relevant to the task outcome
