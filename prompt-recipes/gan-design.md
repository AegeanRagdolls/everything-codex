# GAN Design Prompt Recipe

## Codex invocation

Ask Codex to execute the `gan-design` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# GAN Design Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `gan-design` prompt recipe for <task>."

**Original command intent:** gan design. Use when Codex needs support for: gan design.

---

Parse the following from $ARGUMENTS:
1. `brief` — the user's description of the design to create
2. `--max-iterations N` — (optional, default 10) maximum design-evaluate cycles
3. `--pass-threshold N` — (optional, default 7.5) weighted score to pass (higher default for design)

## GAN-Style Design Harness

A two-agent loop (Generator + Evaluator) focused on frontend design quality. No planner — the brief IS the spec.

This is the same mode Anthropic used for their frontend design experiments, where they saw creative breakthroughs like the 3D Dutch art museum with CSS perspective and doorway navigation.

### Setup
1. Create `gan-harness/` directory
2. Write the brief directly as `gan-harness/spec.md`
3. Write a design-focused `gan-harness/eval-rubric.md` with extra weight on Design Quality and Originality

### Design-Specific Eval Rubric
```markdown
### Design Quality (weight: 0.35)
### Originality (weight: 0.30)
### Craft (weight: 0.25)
### Functionality (weight: 0.10)
```

Note: Originality weight is higher (0.30 vs 0.20) to push for creative breakthroughs. Functionality weight is lower since design mode focuses on visual quality.

### Loop
Same as `/project:gan-build` Phase 2, but:
- Skip the planner
- Use the design-focused rubric
- Generator prompt emphasizes visual quality over feature completeness
- Evaluator prompt emphasizes "would this win a design award?" over "do all features work?"

### Key Difference from gan-build
The Generator is told: "Your PRIMARY goal is visual excellence. A stunning half-finished app beats a functional ugly one. Push for creative leaps — unusual layouts, custom animations, distinctive color work."
