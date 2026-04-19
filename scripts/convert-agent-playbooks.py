#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agent-library"
TARGET = ROOT / ".codex" / "agents"

ANTI_HANG_CONTRACT = """## Anti-hang contract

- Always finish a small smoke task within 60 seconds.
- Never scan the whole repository unless explicitly requested.
- Prefer targeted reads over broad scans.
- Do not spawn child agents.
- Do not wait for unavailable tools.
- If file/tool access is blocked, report the blocker immediately and finish.
- For smoke tests, return compact JSON or 3-5 bullets.
- Do not run shell commands unless the parent task explicitly asks.
- Do not edit files unless the parent task explicitly asks for edits.
"""


def slugify(stem: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return f"playbook_{slug}"


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def summary(text: str, fallback: str) -> str:
    for block in re.split(r"\n\s*\n", text.strip()):
        cleaned = " ".join(line.strip("# ").strip() for line in block.splitlines()).strip()
        if cleaned:
            return cleaned[:220]
    return fallback


def render_agent(source: Path) -> str:
    text = source.read_text(encoding="utf-8", errors="replace").strip()
    name = slugify(source.stem)
    desc = summary(text, f"Codex playbook custom agent converted from {source.name}.")
    instructions = f"""# {source.stem.replace('-', ' ').title()} Playbook Agent

You are an optional Codex custom agent converted from `agent-library/{source.name}`.

Use this role only when the parent task asks for this specific playbook or when the playbook clearly matches the requested review, planning, testing, or analysis task.

{ANTI_HANG_CONTRACT}

## Playbook duties

{text}
"""
    instructions = instructions.replace("'''", "```")
    return f"""name = "{name}"
description = "{toml_escape(desc)}"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"

developer_instructions = '''
{instructions}
'''
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert agent-library playbooks to optional Codex custom-agent TOML files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated playbook agent TOML files.")
    parser.add_argument("--check", action="store_true", help="Only report how many files would be generated.")
    args = parser.parse_args()
    generated = 0
    skipped = 0
    TARGET.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob("*.md")):
        if source.name.lower() == "readme.md":
            continue
        target = TARGET / f"{slugify(source.stem)}.toml"
        if target.exists() and not args.force:
            skipped += 1
            continue
        generated += 1
        if not args.check:
            target.write_text(render_agent(source), encoding="utf-8")
    print(f"playbook_agents_generated={generated}")
    print(f"playbook_agents_skipped={skipped}")
    return 1 if args.check and generated else 0


if __name__ == "__main__":
    raise SystemExit(main())
