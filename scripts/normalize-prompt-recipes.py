#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "prompt-recipes"


def title_from_name(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().removesuffix(" Prompt Recipe")
    return path.stem.replace("-", " ").title()


def sanitize_historical(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.replace("\r\n", "\n").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if stripped.startswith("/") and re.match(r"^/[A-Za-z0-9_-]+", stripped):
            command = stripped.split()[0].lstrip("/")
            rest = stripped[len(command) + 1 :].strip()
            suffix = f" with arguments `{rest}`" if rest else ""
            lines.append(f"Codex prompt recipe equivalent: ask Codex to execute the `{command}` workflow{suffix}.")
            continue
        line = re.sub(r"\bRun\s+`/([A-Za-z0-9_-]+)([^`]*)`", r"Use the Codex prompt recipe equivalent for `\1`\2", line)
        line = re.sub(r"\buse\s+`/([A-Za-z0-9_-]+)([^`]*)`", r"use the Codex prompt recipe equivalent for `\1`\2", line, flags=re.I)
        lines.append(line)
    return "\n".join(lines).strip()


def normalize_recipe(path: Path, dry_run: bool = False) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace")
    if all(section in original for section in ["## Codex invocation", "## Inputs", "## Workflow", "## Output format", "## Safety / side effects", "## Historical Claude Code reference"]):
        return False
    title = title_from_name(path, original)
    if "## Historical Claude Code reference" in original:
        historical = original.split("## Historical Claude Code reference", 1)[1].strip()
        historical = historical.removeprefix("\n").strip()
    else:
        historical = original
    historical = sanitize_historical(historical)
    body = f"""# {title} Prompt Recipe

## Codex invocation

Ask Codex to execute the `{path.stem}` workflow as a normal prompt. Provide the target files, repository context, constraints, and whether edits are allowed.

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

{historical}
"""
    changed = body != original
    if changed and not dry_run:
        path.write_text(body, encoding="utf-8")
    return changed


def check_recipe(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    for section in ["## Codex invocation", "## Inputs", "## Workflow", "## Output format", "## Safety / side effects"]:
        if section not in text:
            issues.append(f"missing {section}")
    before_historical = text.split("## Historical Claude Code reference", 1)[0]
    if re.search(r"(?m)^/[A-Za-z0-9_-]+", before_historical):
        issues.append("bare slash command outside historical reference")
    if re.search(r"(?i)must\s+(?:run|execute|use)\s+/?[A-Za-z0-9_-]*\s*(?:slash command|claude code|task tool)", before_historical):
        issues.append("hard Claude-only runtime statement outside historical reference")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize prompt recipes into Codex-native prompt workflows.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = 0
    issues: list[str] = []
    for path in sorted(RECIPES.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        if normalize_recipe(path, dry_run=args.check):
            changed += 1
        issues.extend(f"{path.relative_to(ROOT)}: {issue}" for issue in check_recipe(path))
    print(f"prompt_recipes_changed={changed}")
    print(f"issues={len(issues)}")
    for issue in issues[:50]:
        print(f"WARN: {issue}")
    return 1 if issues or (args.check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
