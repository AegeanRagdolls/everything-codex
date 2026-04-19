#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORE_AGENTS = {
    "build_fixer",
    "code_reviewer",
    "docs_researcher",
    "explorer",
    "planner",
    "refactor_cleaner",
    "security_reviewer",
    "test_runner",
}

ANTI_HANG = """## Anti-hang contract

- Always finish the requested smoke task within 60 seconds when the task is small.
- Never scan the whole repository unless explicitly requested.
- Prefer targeted reads over broad scans.
- Do not spawn child agents.
- Do not wait for unavailable tools.
- If file/tool access is blocked, report the blocker immediately and finish.
- For smoke tests, return compact JSON or 3-5 bullets.
- Do not run shell commands unless the parent task explicitly asks.
- Do not edit files unless the agent role is explicitly a fixer and the parent task asks for edits.
"""

EXTERNAL_SKILLS = [
    "bun-runtime",
    "claude-api",
    "crosspost",
    "deep-research",
    "dmux-workflows",
    "documentation-lookup",
    "e2e-testing",
    "exa-search",
    "fal-ai-media",
    "video-editing",
    "x-api",
]

EXTERNAL_SECTION = """## Mock smoke test

Run `python scripts/test-external-integrations.py --mode mock` from the repository root. Mock mode must not call external services, open browsers, publish content, send messages, or process real media. It validates the Codex workflow, expected parameters, safety boundaries, and missing-dependency handling.

## Real integration test

Run `python scripts/test-external-integrations.py --mode real` only after the required tools, environment variables, and optional MCP servers are configured. Real mode must report `EXTERNAL_NOT_CONFIGURED` when dependencies are missing. Workflows with posting, messaging, payment, publishing, or other side effects remain dry-run unless the user explicitly enables side effects.

## Missing dependency behavior

If a required tool, environment variable, network path, browser, or MCP server is unavailable, return setup instructions and stop. Do not retry indefinitely, do not silently block, and do not mark real external behavior as passed.

## No silent blocking

For Codex use, finish with a compact status summary: `mock_status`, `real_status`, missing dependencies, and the next setup command. External integrations are usable in mock mode without credentials, but real provider success requires a configured environment.
"""

CODEX_FALLBACK = """## Codex fallback

When Claude Code slash commands, hooks, or Claude-only agents are unavailable:

1. Treat slash-command examples as prompt recipes, not runtime commands.
2. Read the relevant files directly.
3. Execute the workflow as normal Codex steps.
4. Use dry-run mode for external integrations.
5. Report missing tools or credentials instead of blocking silently.

Claude slash command examples are historical/reference only. In Codex, execute this as a normal prompt workflow. Do not require Claude Code hooks, Claude-only slash commands, or Claude-only agent runtime.
"""


def update_config() -> bool:
    path = ROOT / ".codex" / "config.toml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"max_threads\s*=\s*\d+", "max_threads = 2", text)
    text = re.sub(r"max_depth\s*=\s*\d+", "max_depth = 1", text)
    if "job_max_runtime_seconds" not in text:
        text = text.replace("[agents]\nmax_threads = 2\nmax_depth = 1\n", "[agents]\nmax_threads = 2\nmax_depth = 1\njob_max_runtime_seconds = 120\n")
    changed = text != path.read_text(encoding="utf-8")
    path.write_text(text, encoding="utf-8")
    return changed


def update_core_agents() -> int:
    changed = 0
    for path in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
        if path.stem not in CORE_AGENTS:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        if 'sandbox_mode = "read-only"' in text:
            text = text.replace('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')
        if "## Anti-hang contract" not in text:
            text = text.replace('developer_instructions = """\n', f'developer_instructions = """\n{ANTI_HANG}\n', 1)
        if path.stem == "explorer" and "Name collision note" not in text:
            text = text.replace(
                'developer_instructions = """\n',
                'developer_instructions = """\n## Name collision note\n\nThis repo keeps the `explorer` name because Codex exposes an explorer role and this TOML intentionally configures that role for ECC. The anti-hang contract and compact smoke behavior keep the role stable.\n\n',
                1,
            )
        if path.stem == "build_fixer" and "Do not edit files unless" not in text:
            text = text.replace("## Anti-hang contract", "## Anti-hang contract")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def add_section_once(path: Path, heading: str, section: str) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if heading in text:
        return False
    path.write_text(text.rstrip() + "\n\n" + section.rstrip() + "\n", encoding="utf-8")
    return True


def fix_adapter_targets() -> int:
    changed = 0
    for rel in ["skills/.experimental/skill-stocktake/SKILL.md", "skills/.experimental/ui-demo/SKILL.md", "references/the-shortform-guide.md"]:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        original = text
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if re.match(r"^/[A-Za-z0-9_-]+", stripped):
                command = stripped.split()[0].lstrip("/")
                lines.append(f"Codex prompt recipe equivalent: ask Codex to execute the `{command}` workflow as normal prompt steps.")
            else:
                lines.append(line)
        text = "\n".join(lines)
        if "## Codex fallback" not in text:
            text = text.rstrip() + "\n\n" + CODEX_FALLBACK
        if text != original:
            path.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
            changed += 1
    return changed


def update_external_skills() -> int:
    changed = 0
    for base in [ROOT / ".agents" / "skills", ROOT / "skills" / ".curated"]:
        for name in EXTERNAL_SKILLS:
            path = base / name / "SKILL.md"
            if path.exists() and add_section_once(path, "## Mock smoke test", EXTERNAL_SECTION):
                changed += 1
    return changed


def update_descriptions() -> int:
    replacements = {
        "skills/.experimental/cpp-testing/SKILL.md": """description: >-
  Use when writing, updating, fixing, or reviewing C++ tests with GoogleTest,
  GoogleMock, CTest, coverage, or sanitizers. Do not use for non-C++ feature
  work without test impact. Inputs should include target files, failing output,
  or coverage goals; output should be a focused test plan, patch guidance, and
  verification commands.""",
        "skills/.experimental/safety-guard/SKILL.md": """description: >-
  Use when preventing destructive operations during production, deployment,
  migration, autonomous-agent, or broad filesystem work. Do not use for ordinary
  read-only analysis. Inputs should include intended commands, paths, and risk
  scope; output should identify hazards, safer alternatives, and required
  confirmation gates.""",
    }
    changed = 0
    for rel, replacement in replacements.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"description:\s*>-\n(?:  .+\n)+", replacement + "\n", text, count=1)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def main() -> int:
    changes = {
        "config": int(update_config()),
        "core_agents": update_core_agents(),
        "adapter_targets": fix_adapter_targets(),
        "external_skills": update_external_skills(),
        "descriptions": update_descriptions(),
    }
    for key, value in changes.items():
        print(f"{key}_changed={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
