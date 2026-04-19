#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASES = [ROOT / ".agents" / "skills", ROOT / "skills" / ".curated", ROOT / "skills" / ".experimental"]


def parse_description(text: str) -> str:
    lines = text.replace("\r\n", "\n").splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value in {">-", ">", "|", "|-"}:
            collected = []
            for next_line in lines[index + 1 :]:
                if next_line == "---" or (next_line and not next_line.startswith((" ", "\t"))):
                    break
                if next_line.strip():
                    collected.append(next_line.strip())
            return " ".join(collected)
        return value.strip().strip('"')
    return ""


def normalize_description(name: str, description: str) -> str:
    desc = " ".join(description.split())
    lower = desc.lower()
    additions = []
    if "use when" not in lower and "when the user" not in lower and "codex needs" not in lower and "trigger" not in lower:
        additions.append(f"Use when the user needs the {name} workflow.")
    if "do not use" not in lower and "when not" not in lower and "unrelated" not in lower:
        additions.append("Do not use for unrelated tasks.")
    if "input" not in lower:
        additions.append("Inputs should include relevant files, constraints, and available tools.")
    if "output" not in lower:
        additions.append("Output should be a concise plan, result, or verification summary.")
    if additions:
        desc = f"{desc} {' '.join(additions)}"
    return desc


def replace_description(text: str, description: str) -> str:
    text = repair_corrupted_frontmatter(text)
    wrapped = textwrap.wrap(description, width=86)
    block = "description: >-\n" + "\n".join(f"  {line}" for line in wrapped) + "\n"
    lines = text.replace("\r\n", "\n").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        end = index + 1
        if line.split(":", 1)[1].strip() in {">-", ">", "|", "|-"}:
            while end < len(lines):
                stripped = lines[end].rstrip("\n")
                if stripped == "---" or (stripped and not stripped.startswith((" ", "\t"))):
                    break
                end += 1
        lines[index:end] = [block]
        return "".join(lines)
    return re.sub(r"(?m)^description:\s*.+$", lambda _m: block.rstrip(), text, count=1)


def repair_corrupted_frontmatter(text: str) -> str:
    if "\n---\n" in text[4:]:
        return text
    if not text.startswith("---\nname:"):
        return text
    match = re.search(r"(?ms)\A---\nname:\s*(?P<name>[^\n]+)\ndescription:\s*>-\n(?P<folded>.*)\Z", text)
    if not match:
        return text
    folded = " ".join(line.strip() for line in match.group("folded").splitlines()).strip()
    marker = " --- "
    if marker not in folded:
        return text
    description, body = folded.split(marker, 1)
    body = body.strip()
    if body.startswith("#"):
        body = body
    else:
        body = "# " + body
    wrapped = textwrap.wrap(description, width=86)
    desc_block = "\n".join(f"  {line}" for line in wrapped)
    return f"---\nname: {match.group('name').strip()}\ndescription: >-\n{desc_block}\n---\n\n{body}\n"


def normalize(check: bool) -> int:
    changed = 0
    for base in BASES:
        if not base.exists():
            continue
        for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            path = skill_dir / "SKILL.md"
            if not path.exists():
                continue
            text = repair_corrupted_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            desc = parse_description(text)
            normalized = normalize_description(skill_dir.name, desc)
            if normalized != desc or text != path.read_text(encoding="utf-8", errors="replace"):
                changed += 1
                if not check:
                    path.write_text(replace_description(text, normalized), encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize skill descriptions for Codex trigger clarity.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = normalize(args.check)
    print(f"skill_descriptions_changed={changed}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
