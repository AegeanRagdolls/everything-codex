#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_BASES = [ROOT / ".agents" / "skills", ROOT / "skills" / ".curated", ROOT / "skills" / ".experimental"]

DEPENDENCY_RULES = [
    ("node", "runtime", ["node", "npm", "npx", "javascript", "typescript", "playwright", "context7"]),
    ("bun", "runtime", ["bun"]),
    ("python", "runtime", ["python", "pytest", "fastapi", "pydantic"]),
    ("ffmpeg", "runtime", ["ffmpeg", "video"]),
    ("tmux", "runtime", ["tmux", "dmux"]),
    ("browser", "runtime", ["browser", "playwright", "screenshot", "e2e"]),
    ("exa", "mcp", ["exa"]),
    ("context7", "mcp", ["context7"]),
    ("firecrawl", "mcp", ["firecrawl"]),
    ("fal.ai", "api", ["fal.ai", "fal-ai"]),
    ("ANTHROPIC_API_KEY", "env", ["anthropic", "claude api"]),
    ("EXA_API_KEY", "env", ["exa"]),
    ("FIRECRAWL_API_KEY", "env", ["firecrawl"]),
    ("FAL_KEY", "env", ["fal.ai", "fal-ai"]),
    ("X_API_KEY", "env", ["twitter", "x api", "x/twitter"]),
    ("OPENAI_API_KEY", "env", ["openai"]),
    ("GITHUB_TOKEN", "env", ["github"]),
]


def parse_frontmatter(text: str) -> dict[str, str]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = normalized.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    data: dict[str, str] = {}
    current: str | None = None
    folded = False
    for line in normalized[4:end].splitlines():
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            current = key.strip()
            value = value.strip()
            folded = value in {">", ">-", "|", "|-"}
            data[current] = "" if folded else value.strip("'\"")
        elif current and (folded or line.startswith((" ", "\t"))):
            data[current] = (data[current] + " " + line.strip()).strip()
    return data


def sentence(text: str, fallback: str) -> str:
    clean = " ".join(text.split())
    if not clean:
        return fallback
    if len(clean) <= 150:
        return clean
    cut = clean[:147].rsplit(" ", 1)[0]
    return f"{cut}..."


def titleize(name: str) -> str:
    return " ".join(part.upper() if part in {"api", "mcp", "tdd", "e2e"} else part.capitalize() for part in name.split("-"))


def infer_dependencies(name: str, skill_text: str) -> list[tuple[str, str, str]]:
    haystack = f"{name}\n{skill_text}".lower()
    found: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for value, typ, triggers in DEPENDENCY_RULES:
        if any(trigger in haystack for trigger in triggers):
            key = (typ, value)
            if key in seen:
                continue
            seen.add(key)
            if typ == "env":
                description = f"Required only for real {value} integration tests; not used by mock smoke tests."
            elif typ == "mcp":
                description = f"Required only when running real {value} MCP-backed workflows."
            elif typ == "api":
                description = f"Required only for real {value} API-backed workflows."
            else:
                description = f"Required only for workflows that invoke local {value} tooling."
            found.append((typ, value, description))
    return found


def render_yaml(name: str, description: str, dependencies: list[tuple[str, str, str]]) -> str:
    lines = [
        "interface:",
        f'  display_name: "{titleize(name)}"',
        f'  short_description: "{sentence(description, f"Use the {name} skill.")}"',
        f'  default_prompt: "Use the {name} skill to handle this task. Inspect relevant local files first, use mock or dry-run mode for external integrations, and report missing dependencies explicitly."',
        "policy:",
        "  allow_implicit_invocation: true",
        "dependencies:",
        "  tools:",
    ]
    if not dependencies:
        lines.append("    []")
    else:
        for typ, value, dep_desc in dependencies:
            lines.extend(
                [
                    f'    - type: "{typ}"',
                    f'      value: "{value}"',
                    f'      description: "{dep_desc}"',
                ]
            )
    return "\n".join(lines) + "\n"


def normalize(dry_run: bool = False) -> tuple[int, int]:
    changed = 0
    warnings = 0
    for base in SKILL_BASES:
        if not base.exists():
            continue
        for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                warnings += 1
                continue
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
                fm = parse_frontmatter(text)
            except Exception:
                warnings += 1
                continue
            name = fm.get("name", skill_dir.name).strip() or skill_dir.name
            description = fm.get("description", "").strip()
            dependencies = infer_dependencies(name, text)
            target = skill_dir / "agents" / "openai.yaml"
            rendered = render_yaml(name, description, dependencies)
            old = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
            if old != rendered:
                changed += 1
                if not dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(rendered, encoding="utf-8")
    return changed, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Codex agents/openai.yaml metadata for all skills.")
    parser.add_argument("--check", action="store_true", help="Only check whether changes would be needed.")
    args = parser.parse_args()
    changed, warnings = normalize(dry_run=args.check)
    print(f"openai_yaml_changed={changed}")
    print(f"warnings={warnings}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
