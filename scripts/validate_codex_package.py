#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
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
PROMPT_SECTIONS = [
    "## Codex invocation",
    "## Inputs",
    "## Workflow",
    "## Output format",
    "## Safety / side effects",
]


def parse_fm(text: str) -> tuple[list[str], dict[str, str]]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    keys: list[str] = []
    data: dict[str, str] = {}
    current: str | None = None
    folded = False
    for line in normalized[4:end].splitlines():
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            current = key.strip()
            keys.append(current)
            value = value.strip()
            folded = value in {">", ">-", "|", "|-"}
            data[current] = "" if folded else value.strip("'\"")
        elif current and (folded or line.startswith((" ", "\t"))):
            data[current] = (data[current] + " " + line.strip()).strip()
    return keys, data


def trigger_ok(description: str) -> bool:
    lower = description.lower()
    return (
        len(description) >= 60
        and ("use when" in lower or "when the user" in lower or "codex needs" in lower or "trigger" in lower)
        and ("do not use" in lower or "unrelated" in lower or "when not" in lower)
        and "input" in lower
        and "output" in lower
    )


def validate_openai_yaml(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    for needle in [
        "interface:",
        "display_name:",
        "short_description:",
        "default_prompt:",
        "policy:",
        "allow_implicit_invocation:",
        "dependencies:",
        "tools:",
    ]:
        if needle not in text:
            issues.append(f"missing {needle}")
    return issues


def validate_skill_dir(skill_dir: Path, failures: list[str]) -> None:
    skill = skill_dir / "SKILL.md"
    if not skill.exists():
        failures.append(f"{skill_dir.relative_to(ROOT)} missing SKILL.md")
        return
    if skill.is_symlink():
        failures.append(f"{skill.relative_to(ROOT)} must not be a symlink")
    try:
        keys, data = parse_fm(skill.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        failures.append(f"{skill.relative_to(ROOT)}: {exc}")
        return
    if keys != ["name", "description"]:
        failures.append(f"{skill.relative_to(ROOT)} frontmatter keys must be exactly name+description, got {keys}")
    name = data.get("name", "").strip()
    if not NAME_RE.match(name):
        failures.append(f"{skill.relative_to(ROOT)} invalid skill name {name!r}")
    if name != skill_dir.name:
        failures.append(f"{skill.relative_to(ROOT)} name {name!r} does not match folder {skill_dir.name!r}")
    desc = data.get("description", "").strip()
    if not trigger_ok(desc):
        failures.append(f"{skill.relative_to(ROOT)} description lacks Codex trigger clarity, input, or output expectations")
    meta = skill_dir / "agents" / "openai.yaml"
    if not meta.exists():
        failures.append(f"{skill_dir.relative_to(ROOT)} missing agents/openai.yaml")
    else:
        for issue in validate_openai_yaml(meta):
            failures.append(f"{meta.relative_to(ROOT)} {issue}")


def main() -> int:
    failures: list[str] = []

    try:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        agents_config = config.get("agents", {})
        if agents_config.get("max_threads") != 4:
            failures.append(".codex/config.toml agents.max_threads must be 4")
        if agents_config.get("max_depth") != 1:
            failures.append(".codex/config.toml agents.max_depth must be 1")
        if agents_config.get("job_max_runtime_seconds") != 180:
            failures.append(".codex/config.toml agents.job_max_runtime_seconds must be 180")
    except Exception as exc:
        failures.append(f".codex/config.toml TOML parse failed: {exc}")

    agent_files = sorted((ROOT / ".codex" / "agents").glob("*.toml"))
    agent_names: set[str] = set()
    playbook_agents = 0
    for path in agent_files:
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)} TOML parse failed: {exc}")
            continue
        name = str(data.get("name", "")).strip()
        agent_names.add(name)
        if name.startswith("playbook_"):
            playbook_agents += 1
        for key in ["name", "description", "developer_instructions", "model_reasoning_effort", "sandbox_mode"]:
            if not str(data.get(key, "")).strip():
                failures.append(f"{path.relative_to(ROOT)} missing required custom-agent field: {key}")
        if "Anti-hang contract" not in str(data.get("developer_instructions", "")):
            failures.append(f"{path.relative_to(ROOT)} missing anti-hang contract")
    missing_core = sorted(CORE_AGENTS - agent_names)
    if missing_core:
        failures.append(f"missing core custom agents: {missing_core}")

    skill_dirs: list[Path] = []
    for bucket in [".curated", ".experimental"]:
        base = ROOT / "skills" / bucket
        if not base.exists():
            failures.append(f"missing skills/{bucket}")
            continue
        for directory in sorted(p for p in base.iterdir() if p.is_dir()):
            skill_dirs.append(directory)
            validate_skill_dir(directory, failures)

    repo_base = ROOT / ".agents" / "skills"
    repo_skill_dirs = sorted(p for p in repo_base.iterdir() if p.is_dir()) if repo_base.exists() else []
    curated_dirs = sorted(p for p in (ROOT / "skills" / ".curated").iterdir() if p.is_dir()) if (ROOT / "skills" / ".curated").exists() else []
    curated_names = {p.name for p in curated_dirs}
    repo_names = {p.name for p in repo_skill_dirs}
    if curated_names != repo_names:
        failures.append(f".agents/skills names do not match skills/.curated: missing={sorted(curated_names - repo_names)} extra={sorted(repo_names - curated_names)}")
    for directory in repo_skill_dirs:
        validate_skill_dir(directory, failures)

    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    expected = len(catalog.get("curated", [])) + len(catalog.get("experimental", []))
    if expected != len(skill_dirs):
        failures.append(f"catalog count {expected} != skill folder count {len(skill_dirs)}")

    recipes = sorted(p for p in (ROOT / "prompt-recipes").glob("*.md") if p.name.lower() != "readme.md")
    for recipe in recipes:
        text = recipe.read_text(encoding="utf-8", errors="replace")
        for section in PROMPT_SECTIONS:
            if section not in text:
                failures.append(f"{recipe.relative_to(ROOT)} missing {section}")
        before_history = text.split("## Historical Claude Code reference", 1)[0]
        if re.search(r"(?m)^/[A-Za-z0-9_-]+", before_history):
            failures.append(f"{recipe.relative_to(ROOT)} has bare slash command outside historical reference")

    installer = (ROOT / "scripts" / "install-codex.sh").read_text(encoding="utf-8")
    if "$HOME/.agents/skills" not in installer:
        failures.append("install-codex.sh must default to $HOME/.agents/skills for user skills")
    if "$CODEX_HOME/skills" in installer:
        failures.append("install-codex.sh must not install skills to $CODEX_HOME/skills")
    if not (ROOT / "scripts" / "install-codex.py").exists():
        failures.append("missing cross-platform scripts/install-codex.py")
    for required in ["check-external-deps.py", "test-external-integrations.py", "run-full-codex-audit.py", "normalize-openai-yaml.py", "normalize-prompt-recipes.py", "convert-agent-playbooks.py"]:
        if not (ROOT / "scripts" / required).exists():
            failures.append(f"missing scripts/{required}")

    if not (ROOT / "AGENTS.md").exists():
        failures.append("missing AGENTS.md")
    for fd in [".claude", ".claude-plugin"]:
        if (ROOT / fd).exists():
            failures.append(f"Codex package should not include Claude runtime dir {fd}")

    print(
        f"Validated {len(skill_dirs)} installable skills, {len(repo_skill_dirs)} repo-scoped curated skills, "
        f"{len(recipes)} prompt recipes, {len(agent_files)} Codex custom agents ({len(CORE_AGENTS)} core, {playbook_agents} playbook)."
    )
    if failures:
        print("\n".join(failures))
        return 1
    print("OK: Codex package structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
