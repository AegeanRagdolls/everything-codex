# Everything Codex

A Codex-first conversion of **Everything Claude Code**. This package keeps the useful ECC workflows, but exposes them in the way Codex expects:

- `AGENTS.md` for repository guidance
- `skills/.curated/*/SKILL.md` and `skills/.experimental/*/SKILL.md` for Codex skills
- `agents/openai.yaml` UI metadata for every skill
- `.codex/config.toml` for sandbox, approval, MCP, feature flags, and role config
- `.codex/agents/*.toml` for core Codex agents and optional playbook-derived agents
- `prompt-recipes/*.md` instead of Claude slash commands

## What changed from the original repo

The original repo mixes Claude Code agents, commands, hooks, rules, and several harness surfaces. Codex does not use Claude hooks or Claude slash command files as its primary interface, so this package does **not** pretend those are native. It converts them into Codex skills, role configs, and prompt recipes.

## Install

Install only the curated set first. It is intentionally smaller because Codex skill metadata is discoverable context and too many skills can create noise.

Windows recommended path:

```powershell
python -S scripts\validate_codex_package.py
python scripts\install-codex.py --core
```

macOS/Linux recommended path:

```bash
unzip everything-codex-code-v2.zip
cd everything-codex-code
python3 -S scripts/validate_codex_package.py
python3 scripts/install-codex.py --core
```

Then restart Codex.

To install everything:

```bash
python3 scripts/install-codex.py --all
```

To install into a temporary or custom Codex home:

```bash
python3 scripts/install-codex.py --core --codex-home /tmp/codex-home --no-config
```

The Bash installer remains available on Unix-like systems, and the PowerShell installer remains available as a Windows-native fallback. Windows validation treats missing Bash/WSL as not applicable when the Python and PowerShell installers pass.

To install custom agents as well as skills:

```bash
python3 scripts/install-codex.py --core --install-agents
python3 scripts/install-codex.py --core --install-agents --install-playbook-agents
```

## Use

Ask Codex directly for a skill:

```text
Use the tdd-workflow skill to implement this feature with RED -> GREEN -> REFACTOR.
Use the security-review skill on my current git diff.
Use the verification-loop skill and run the repo's checks before summarizing.
```

Use prompt recipes when you want an old command workflow:

```text
Use the code-review prompt recipe on my current local changes.
Use the build-fix prompt recipe and fix one error at a time.
```

## Multica

If you want to use this package as the Codex capability layer behind a Multica agent team, start here:

- Chinese operator manual: [docs/multica-codex-usage-manual.md](/mnt/c/Users/oream/Desktop/everything-codex-code/docs/multica-codex-usage-manual.md)
- Bootstrap reference: [docs/multica-codex-team-bootstrap.md](/mnt/c/Users/oream/Desktop/everything-codex-code/docs/multica-codex-team-bootstrap.md)

The current recommended deployment is `multica` + `codex` inside Ubuntu on WSL2, with Windows login auto-starting the WSL-hosted Multica daemon.

## Contents

- Curated skills: **34**
- Experimental/library skills: **150**
- Total migrated skills: **184**
- Prompt recipes: **79**
- Core active Codex custom agents: **8**
- Playbook-derived optional custom agents: **48**
- Total Codex custom agent TOMLs: **56**
- Reference agent playbooks: **48**

Core agents are the small runtime set intended for normal Codex use: `build_fixer`, `code_reviewer`, `docs_researcher`, `explorer`, `planner`, `refactor_cleaner`, `security_reviewer`, and `test_runner`.

Playbook agents are generated from `agent-library/*.md` as `playbook_<slug>` TOML files. They make the playbooks spawnable in Codex-compatible surfaces, but enabling all of them can add selector noise and token cost. Install only core agents for daily use; install playbook agents when you need the larger library of specialized roles.

## Safety defaults

The included config uses `approval_policy = "on-request"` and `sandbox_mode = "workspace-write"`. It does not pin a model, so your installed Codex version can use its current supported default.

## Validate

```bash
python -S scripts/validate_codex_package.py
python scripts/install-codex.py --dry-run --all --codex-home .codex-test/tmp/ecc-codex-home
python scripts/run-full-codex-audit.py
```

## Direct local test without installing

Launch Codex from this folder and run `/skills`; the curated skills in `.agents/skills` should appear. For global use, run `python scripts/install-codex.py --core`, which installs to the official user skill directory under the user's home `.agents/skills` path.

Optional MCP servers in `.codex/config.toml` are disabled by default to avoid first-run startup failures. Enable only the servers you use.

## External integrations

External skills are tested in two modes:

- Mock/dry-run smoke tests validate Codex workflow, parameter handling, missing-dependency behavior, and side-effect boundaries without calling real services.
- Real integration tests run only when the required env vars, tools, MCP servers, and explicit test mode are available.

Without credentials or local tools, external integrations report `EXTERNAL_NOT_CONFIGURED`, not real PASS. See `EXTERNAL_DEPENDENCIES.md` and `.env.external.example` for setup.
