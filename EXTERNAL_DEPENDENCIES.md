# External Dependencies

This package separates local Codex usability from real external integrations.

Local package validation and mock smoke tests must pass without credentials, network access, or optional MCP servers. Real provider tests run only when the required tools, environment variables, and MCP servers are configured.

## Status Model

- `LOCAL_PASS`: Repository structure, skills, agents, recipes, installers, and mock workflows are valid.
- `REAL_EXTERNAL_PASS`: Real external integrations were configured and tested.
- `EXTERNAL_NOT_CONFIGURED`: External dependencies are absent or disabled. This is not a local package failure.

## Side-Effect Policy

Mock tests never call external services. Real tests default to dry-run for posting, email, payment, social publishing, or other side effects. A test runner must require an explicit `--allow-side-effects` flag before any irreversible external action.

## External Skill Matrix

| Skill | Required tools | Required env vars | Optional MCP | Mock test | Real test | Expected safe behavior |
|---|---|---|---|---|---|---|
| `bun-runtime` | `bun` | none | none | `python scripts/test-external-integrations.py --mode mock` | `python scripts/test-external-integrations.py --mode real` | Report Bun setup steps when `bun` is missing. |
| `claude-api` | none | `ANTHROPIC_API_KEY` | none | mock request shape only | real mode only with key | Never call Anthropic in mock mode. |
| `crosspost` | none | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | none | draft-only crosspost plan | real mode defaults to dry-run | Do not publish unless `--allow-side-effects` is present. |
| `deep-research` | none | `EXA_API_KEY`, `FIRECRAWL_API_KEY` | `exa` | research plan only | real mode with keys and MCP | Report missing search/MCP setup instead of blocking. |
| `dmux-workflows` | `tmux` | none | none | orchestration plan only | real mode with tmux | Do not create panes in mock mode. |
| `documentation-lookup` | `npx` | none | `context7` | docs fallback plan | real mode with Context7 MCP enabled | Use local docs or setup instructions when MCP is disabled. |
| `e2e-testing` | `npx` and browser tooling | none | `playwright` | Playwright test-plan generation | real mode with Playwright tooling | Do not launch browsers in mock mode. |
| `exa-search` | none | `EXA_API_KEY` | `exa` | query construction only | real mode with Exa key/MCP | Never claim source verification without a real call. |
| `fal-ai-media` | none | `FAL_KEY` | none | prompt/safety validation only | real mode with key | Do not generate media in mock mode. |
| `video-editing` | `ffmpeg`, `npx` | `FAL_KEY` for AI media steps | none | edit plan and command shape | real mode with tools and key | Do not process or upload media in mock mode. |
| `x-api` | none | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | none | payload validation only | real mode defaults to dry-run | Do not post unless `--allow-side-effects` is present. |

## Commands

Check local dependency availability:

```bash
python scripts/check-external-deps.py --json .codex-test/reports/external_deps.json
```

Run safe mock smoke tests:

```bash
python scripts/test-external-integrations.py --mode mock --json .codex-test/reports/external_mock_results.json
```

Run guarded real integration checks:

```bash
python scripts/test-external-integrations.py --mode real --json .codex-test/reports/external_real_results.json
```

Real tests that can create side effects require an additional explicit flag:

```bash
python scripts/test-external-integrations.py --mode real --allow-side-effects
```
