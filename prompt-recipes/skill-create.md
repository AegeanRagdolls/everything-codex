# Skill Create Prompt Recipe

## Codex invocation

Ask Codex to execute the `skill-create` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

# Skill Create Prompt Recipe

This is a Codex prompt recipe, not a Claude slash command. In Codex, paste this file's body into the chat or ask: "Use the `skill-create` prompt recipe for <task>."

**Original command intent:** Analyze local git history to extract coding patterns and generate SKILL.md files. Local version of the Skill Creator GitHub App. Use when Codex needs support for: Analyze local git history to extract coding patterns and generate SKILL.md files. Local version of the Skill Creator GitHub App.

---

# /skill-create - Local Skill Generation

Analyze your repository's git history to extract coding patterns and generate SKILL.md files that teach Claude your team's practices.

## Usage

```bash
Codex prompt recipe equivalent: ask Codex to execute the `skill-create` workflow with arguments `# Analyze current repo`.
Codex prompt recipe equivalent: ask Codex to execute the `skill-create` workflow with arguments `--commits 100      # Analyze last 100 commits`.
Codex prompt recipe equivalent: ask Codex to execute the `skill-create` workflow with arguments `--output ./skills  # Custom output directory`.
Codex prompt recipe equivalent: ask Codex to execute the `skill-create` workflow with arguments `--instincts        # Also generate instincts for continuous-learning-v2`.
```

## What It Does

1. **Parses Git History** - Analyzes commits, file changes, and patterns
2. **Detects Patterns** - Identifies recurring workflows and conventions
3. **Generates SKILL.md** - Creates valid Claude Code skill files
4. **Optionally Creates Instincts** - For the continuous-learning-v2 system

## Analysis Steps

### Step 1: Gather Git Data

```bash
# Get recent commits with file changes
git log --oneline -n ${COMMITS:-200} --name-only --pretty=format:"%H|%s|%ad" --date=short

# Get commit frequency by file
git log --oneline -n 200 --name-only | grep -v "^$" | grep -v "^[a-f0-9]" | sort | uniq -c | sort -rn | head -20

# Get commit message patterns
git log --oneline -n 200 | cut -d' ' -f2- | head -50
```

### Step 2: Detect Patterns

Look for these pattern types:

| Pattern | Detection Method |
|---------|-----------------|
| **Commit conventions** | Regex on commit messages (feat:, fix:, chore:) |
| **File co-changes** | Files that always change together |
| **Workflow sequences** | Repeated file change patterns |
| **Architecture** | Folder structure and naming conventions |
| **Testing patterns** | Test file locations, naming, coverage |

### Step 3: Generate SKILL.md

Output format:

```markdown
---
name: {repo-name}-patterns
description: Coding patterns extracted from {repo-name}
version: 1.0.0
source: local-git-analysis
analyzed_commits: {count}
---

# {Repo Name} Patterns

## Commit Conventions
{detected commit message patterns}

## Code Architecture
{detected folder structure and organization}

## Workflows
{detected repeating file change patterns}

## Testing Patterns
{detected test conventions}
```

### Step 4: Generate Instincts (if --instincts)

For continuous-learning-v2 integration:

```yaml
---
id: {repo}-commit-convention
trigger: "when writing a commit message"
confidence: 0.8
domain: git
source: local-repo-analysis
---

# Use Conventional Commits

## Action
Prefix commits with: feat:, fix:, chore:, docs:, test:, refactor:

## Evidence
- Analyzed {n} commits
- {percentage}% follow conventional commit format
```

## Example Output

Running `/skill-create` on a TypeScript project might produce:

```markdown
---
name: my-app-patterns
description: Coding patterns from my-app repository
version: 1.0.0
source: local-git-analysis
analyzed_commits: 150
---

# My App Patterns

## Commit Conventions

This project uses **conventional commits**:
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks
- `docs:` - Documentation updates

## Code Architecture

```
src/
├── components/     # React components (PascalCase.tsx)
├── hooks/          # Custom hooks (use*.ts)
├── utils/          # Utility functions
├── types/          # TypeScript type definitions
└── services/       # API and external services
```

## Workflows

### Adding a New Component
1. Create `src/components/ComponentName.tsx`
2. Add tests in `src/components/__tests__/ComponentName.test.tsx`
3. Export from `src/components/index.ts`

### Database Migration
1. Modify `src/db/schema.ts`
2. Run `pnpm db:generate`
3. Run `pnpm db:migrate`

## Testing Patterns

- Test files: `__tests__/` directories or `.test.ts` suffix
- Coverage target: 80%+
- Framework: Vitest
```

## GitHub App Integration

For advanced features (10k+ commits, team sharing, auto-PRs), use the [Skill Creator GitHub App](https://github.com/apps/skill-creator):

- Install: [github.com/apps/skill-creator](https://github.com/apps/skill-creator)
- Comment `/skill-creator analyze` on any issue
- Receives PR with generated skills

## Related Commands

- `/instinct-import` - Import generated instincts
- `/instinct-status` - View learned instincts
- `/evolve` - Cluster instincts into skills/agents

---

*Part of [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)*
