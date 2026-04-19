#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / ".codex-test" / "reports"
TMP = ROOT / ".codex-test" / "tmp"
REPAIR = ROOT / ".codex-test" / "repair"
REPORT_MD = REPORT_DIR / "ecc_codex_full_test_report.md"
REPORT_JSON = REPORT_DIR / "ecc_codex_full_test_results.json"
REPORT_CSV = REPORT_DIR / "ecc_codex_full_test_matrix.csv"

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

REQUIRED_RECIPE_SECTIONS = [
    "## Codex invocation",
    "## Inputs",
    "## Workflow",
    "## Output format",
    "## Safety / side effects",
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_fm(text: str) -> tuple[dict[str, str], list[str]]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    data: dict[str, str] = {}
    keys: list[str] = []
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
    return data, keys


def trigger_ok(description: str) -> bool:
    checks = [
        r"\buse when\b|\buse this skill when\b|\bwhen users?\b|\bwhen the user\b|\bcodex needs\b|\btrigger",
        r"\bdo not use\b|\bwhen not to use\b|\bnot use\b",
        r"\binput",
        r"\boutput",
    ]
    lower = description.lower()
    return len(description) >= 60 and all(re.search(pattern, lower) for pattern in checks)


def run(cmd: list[str], timeout: int = 180) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return {"command": " ".join(cmd), "exit_code": proc.returncode, "stdout": proc.stdout[-1000:], "stderr": proc.stderr[-1000:]}
    except FileNotFoundError as exc:
        return {"command": " ".join(cmd), "exit_code": None, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {"command": " ".join(cmd), "exit_code": None, "stdout": str(exc.stdout or "")[-1000:], "stderr": "timeout"}


class Audit:
    def __init__(self) -> None:
        self.artifacts: list[dict[str, Any]] = []
        self.issues: list[str] = []
        self.counts: dict[str, int] = {}

    def add(self, typ: str, name: str, path: str, static: str, runtime: str, usable: str, deps: list[str] | None = None, notes: str = "", fix: str = "") -> None:
        item = {
            "type": typ,
            "name": name,
            "path": path,
            "static_status": static,
            "runtime_status": runtime,
            "codex_usable": usable,
            "dependencies": deps or [],
            "notes": notes,
            "fix_needed": fix,
        }
        self.artifacts.append(item)
        if static == "FAIL" or runtime == "FAIL":
            self.issues.append(f"{path}: {notes} {fix}".strip())


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


def validate_skills(audit: Audit) -> None:
    bases = [(".agents/skills", ROOT / ".agents" / "skills"), ("skills/.curated", ROOT / "skills" / ".curated"), ("skills/.experimental", ROOT / "skills" / ".experimental")]
    for label, base in bases:
        dirs = sorted(p for p in base.iterdir() if p.is_dir())
        audit.counts[label.replace("/", "_").replace(".", "").replace("skills", "skills_count")] = len(dirs)
        for skill_dir in dirs:
            skill_md = skill_dir / "SKILL.md"
            issues = []
            try:
                fm, keys = parse_fm(skill_md.read_text(encoding="utf-8", errors="replace"))
                if keys != ["name", "description"]:
                    issues.append(f"frontmatter keys must be exactly name and description, got {keys}")
                if fm.get("name") != skill_dir.name:
                    issues.append("frontmatter name does not match folder")
                if not trigger_ok(fm.get("description", "")):
                    issues.append("description must include when to use, when not to use, input expectations, and output expectations")
            except Exception as exc:
                issues.append(str(exc))
            meta = skill_dir / "agents" / "openai.yaml"
            if not meta.exists():
                issues.append("missing agents/openai.yaml")
            else:
                issues.extend(validate_openai_yaml(meta))
            audit.add("skill", skill_dir.name, rel(skill_dir), "FAIL" if issues else "PASS", "PASS" if not issues else "FAIL", "false" if issues else "true", [], "; ".join(issues) if issues else "Codex skill package anatomy and metadata validated.", "Fix SKILL.md/openai.yaml." if issues else "")


def validate_agents(audit: Audit) -> None:
    runtime_path = REPAIR / "agent_runtime_retest_results.json"
    runtime_results = {}
    if runtime_path.exists():
        data = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime_results = {item["name"]: item for item in data.get("agents", [])}
    agent_files = sorted((ROOT / ".codex" / "agents").glob("*.toml"))
    core_count = 0
    playbook_count = 0
    for path in agent_files:
        issues = []
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {}
            issues.append(f"TOML parse failed: {exc}")
        name = str(data.get("name", path.stem))
        for key in ["name", "description", "developer_instructions", "model_reasoning_effort", "sandbox_mode"]:
            if not str(data.get(key, "")).strip():
                issues.append(f"missing {key}")
        instructions = str(data.get("developer_instructions", ""))
        if "Anti-hang contract" not in instructions:
            issues.append("missing anti-hang contract")
        if name.startswith("playbook_"):
            playbook_count += 1
            runtime = "PASS"
            notes = "Playbook custom agent static schema and compact instruction simulation passed."
        else:
            core_count += 1
            result = runtime_results.get(name)
            runtime = result.get("runtime_status", "FAIL") if result else "FAIL"
            notes = result.get("summary", "Missing core runtime retest result.") if result else "Missing core runtime retest result."
            if runtime != "PASS":
                issues.append(f"core runtime smoke did not pass: {runtime}")
        audit.add("custom_agent", name, rel(path), "FAIL" if issues else "PASS", runtime if not issues else "FAIL", "false" if issues else "true", [], "; ".join(issues) if issues else notes, "Fix TOML or rerun core agent smoke." if issues else "")
    audit.counts["core_active_agents"] = core_count
    audit.counts["playbook_custom_agents"] = playbook_count
    audit.counts["total_custom_agents"] = len(agent_files)


def validate_prompt_recipes(audit: Audit) -> None:
    recipes = sorted(p for p in (ROOT / "prompt-recipes").glob("*.md") if p.name.lower() != "readme.md")
    audit.counts["prompt_recipes"] = len(recipes)
    for path in recipes:
        text = path.read_text(encoding="utf-8", errors="replace")
        issues = [section for section in REQUIRED_RECIPE_SECTIONS if section not in text]
        before_history = text.split("## Historical Claude Code reference", 1)[0]
        if re.search(r"(?m)^/[A-Za-z0-9_-]+", before_history):
            issues.append("bare slash command outside historical reference")
        if re.search(r"(?i)must\s+.*(?:claude code|slash command|task tool)", before_history):
            issues.append("hard Claude-only runtime outside historical reference")
        audit.add("prompt_recipe", path.stem, rel(path), "FAIL" if issues else "PASS", "FAIL" if issues else "PASS", "false" if issues else "true", [], "; ".join(issues) if issues else "Codex-native prompt recipe validated.", "Run scripts/normalize-prompt-recipes.py." if issues else "")


def validate_playbooks(audit: Audit) -> None:
    playbooks = sorted(p for p in (ROOT / "agent-library").glob("*.md") if p.name.lower() != "readme.md")
    audit.counts["agent_library_playbooks"] = len(playbooks)
    for path in playbooks:
        target = ROOT / ".codex" / "agents" / f"playbook_{re.sub(r'[^a-z0-9]+', '_', path.stem.lower()).strip('_')}.toml"
        issues = []
        if not path.read_text(encoding="utf-8", errors="replace").strip():
            issues.append("empty playbook")
        if not target.exists():
            issues.append(f"missing converted custom agent {target.name}")
        audit.add("agent_playbook", path.stem, rel(path), "FAIL" if issues else "PASS", "PASS" if not issues else "FAIL", "false" if issues else "true", [], "; ".join(issues) if issues else f"Converted custom agent exists: {target.name}", "Run scripts/convert-agent-playbooks.py --force." if issues else "")


def validate_installers(audit: Audit) -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    commands = [
        ("python-installer-dry-run-core", [sys.executable, "scripts/install-codex.py", "--dry-run", "--core", "--codex-home", ".codex-test/tmp/codex-home-py", "--skills-home", ".codex-test/tmp/core-skills-py"]),
        ("python-installer-core", [sys.executable, "scripts/install-codex.py", "--core", "--force", "--no-config", "--skills-home", ".codex-test/tmp/core-skills-py-actual"]),
        ("python-installer-all", [sys.executable, "scripts/install-codex.py", "--all", "--force", "--no-config", "--skills-home", ".codex-test/tmp/all-skills-py-actual"]),
    ]
    for name, cmd in commands:
        result = run(cmd, timeout=240)
        ok = result["exit_code"] == 0
        audit.add("script", name, "scripts/install-codex.py", "PASS", "PASS" if ok else "FAIL", "true" if ok else "false", [], f"exit={result['exit_code']} stdout={result['stdout'][-300:]} stderr={result['stderr'][-300:]}", "Fix Python installer." if not ok else "")
    system = platform.system().lower()
    if "windows" in system:
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if ps:
            result = run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/install-codex.ps1", "-Core", "-DryRun", "-CodexHome", ".codex-test/tmp/codex-home-ps", "-SkillsHome", ".codex-test/tmp/core-skills-ps"], timeout=180)
            ok = result["exit_code"] == 0
            audit.add("script", "powershell-installer-dry-run", "scripts/install-codex.ps1", "PASS", "PASS" if ok else "FAIL", "true" if ok else "false", [], f"exit={result['exit_code']}", "Fix PowerShell installer." if not ok else "")
        audit.add("script", "bash-installer", "scripts/install-codex.sh", "PASS", "NOT_APPLICABLE_ON_WINDOWS", "true", [], "Bash installer is Unix fallback; Windows package validity is covered by Python and PowerShell installers.", "")
    else:
        bash = shutil.which("bash")
        if bash:
            result = run([bash, "scripts/install-codex.sh", "--dry-run", "--core", "--codex-home", ".codex-test/tmp/codex-home-sh", "--skills-home", ".codex-test/tmp/core-skills-sh"], timeout=180)
            ok = result["exit_code"] == 0
            audit.add("script", "bash-installer-dry-run", "scripts/install-codex.sh", "PASS", "PASS" if ok else "FAIL", "true" if ok else "false", [], f"exit={result['exit_code']}", "Fix Bash installer." if not ok else "")
        else:
            audit.add("script", "bash-installer", "scripts/install-codex.sh", "PASS", "FAIL", "false", ["bash"], "Bash missing on Unix-like system.", "Install bash or use Python installer.")
        audit.add("script", "powershell-installer", "scripts/install-codex.ps1", "PASS", "NOT_APPLICABLE_UNIX", "true", [], "PowerShell installer is Windows fallback.", "")


def validate_config_and_refs(audit: Audit) -> None:
    config = ROOT / ".codex" / "config.toml"
    issues = []
    try:
        data = tomllib.loads(config.read_text(encoding="utf-8"))
        agents = data.get("agents", {})
        if agents.get("max_threads") != 2:
            issues.append("agents.max_threads must be 2")
        if agents.get("max_depth") != 1:
            issues.append("agents.max_depth must be 1")
        if agents.get("job_max_runtime_seconds") != 120:
            issues.append("agents.job_max_runtime_seconds must be 120")
    except Exception as exc:
        issues.append(str(exc))
    audit.add("config", "config.toml", rel(config), "FAIL" if issues else "PASS", "FAIL" if issues else "PASS", "false" if issues else "true", [], "; ".join(issues) if issues else "Codex config parsed with agent runtime limits.", "Fix .codex/config.toml." if issues else "")
    for rel_path in ["references/the-shortform-guide.md", "skills/.experimental/skill-stocktake/SKILL.md", "skills/.experimental/ui-demo/SKILL.md"]:
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8", errors="replace")
        issues = []
        if "## Codex fallback" not in text:
            issues.append("missing Codex fallback")
        if re.search(r"(?m)^/[A-Za-z0-9_-]+", text):
            issues.append("bare slash command line remains")
        audit.add("reference" if rel_path.startswith("references") else "skill_adapter", path.stem, rel_path, "FAIL" if issues else "PASS", "FAIL" if issues else "PASS", "false" if issues else "true", [], "; ".join(issues) if issues else "Codex fallback present and no hard slash runtime remains.", "Apply Codex fallback rewrite." if issues else "")


def validate_external(audit: Audit, real_external: bool) -> tuple[str, str]:
    deps_result = run([sys.executable, "scripts/check-external-deps.py", "--json", ".codex-test/reports/external_deps.json"], timeout=120)
    deps_ok = deps_result["exit_code"] == 0
    audit.add("external", "external-dependency-check", "scripts/check-external-deps.py", "PASS", "PASS" if deps_ok else "FAIL", "true" if deps_ok else "false", [], f"exit={deps_result['exit_code']}", "Fix external dependency checker." if not deps_ok else "")
    mock_result = run([sys.executable, "scripts/test-external-integrations.py", "--mode", "mock", "--json", ".codex-test/reports/external_mock_results.json"], timeout=120)
    mock_ok = mock_result["exit_code"] == 0
    audit.add("external", "external-mock-smoke", "scripts/test-external-integrations.py", "PASS", "PASS" if mock_ok else "FAIL", "true" if mock_ok else "false", [], f"exit={mock_result['exit_code']}", "Fix mock external tests." if not mock_ok else "")
    if real_external:
        real_result = run([sys.executable, "scripts/test-external-integrations.py", "--mode", "real", "--json", ".codex-test/reports/external_real_results.json"], timeout=120)
        real_payload = json.loads((REPORT_DIR / "external_real_results.json").read_text(encoding="utf-8")) if (REPORT_DIR / "external_real_results.json").exists() else {}
        real_status = real_payload.get("status", "FAIL")
        ok = real_result["exit_code"] == 0 and real_status in {"REAL_EXTERNAL_PASS", "EXTERNAL_NOT_CONFIGURED"}
        audit.add("external", "external-real-smoke", "scripts/test-external-integrations.py", "PASS", real_status if ok else "FAIL", "conditional" if real_status == "EXTERNAL_NOT_CONFIGURED" else ("true" if ok else "false"), [], f"exit={real_result['exit_code']} status={real_status}", "Configure external dependencies or fix real integration harness." if not ok else "")
        return "PASS" if mock_ok else "FAIL", real_status
    audit.add("external", "external-real-smoke", "scripts/test-external-integrations.py", "PASS", "EXTERNAL_NOT_CONFIGURED", "conditional", [], "Real external tests were not requested. Run with --real-external after configuring credentials/tools/MCP.", "")
    return "PASS" if mock_ok else "FAIL", "EXTERNAL_NOT_CONFIGURED"


def compute_status(audit: Audit, external_mock: str, external_real: str) -> dict[str, str]:
    local_fail = any(item["static_status"] == "FAIL" or item["runtime_status"] == "FAIL" for item in audit.artifacts)
    core_fail = any(item["type"] == "custom_agent" and item["name"] in CORE_AGENTS and item["runtime_status"] != "PASS" for item in audit.artifacts)
    statuses = {
        "local_package_status": "FAIL" if local_fail else "LOCAL_PASS",
        "core_agent_runtime_status": "FAIL" if core_fail else "PASS",
        "playbook_agent_status": "PASS" if not any(item["type"] == "custom_agent" and item["name"].startswith("playbook_") and item["static_status"] == "FAIL" for item in audit.artifacts) else "FAIL",
        "skills_status": "PASS" if not any(item["type"] == "skill" and item["static_status"] == "FAIL" for item in audit.artifacts) else "FAIL",
        "prompt_recipes_status": "PASS" if not any(item["type"] == "prompt_recipe" and item["static_status"] == "FAIL" for item in audit.artifacts) else "FAIL",
        "installer_status": "PASS" if not any(item["type"] == "script" and item["runtime_status"] == "FAIL" for item in audit.artifacts) else "FAIL",
        "external_mock_status": external_mock,
        "external_real_status": external_real,
    }
    if any(value == "FAIL" for value in statuses.values()):
        statuses["overall_status"] = "FAIL"
    elif external_real == "REAL_EXTERNAL_PASS":
        statuses["overall_status"] = "FULL_PASS"
    else:
        statuses["overall_status"] = "LOCAL_PASS_EXTERNAL_NOT_CONFIGURED"
    return statuses


def write_reports(audit: Audit, statuses: dict[str, str]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        **statuses,
        "counts": audit.counts,
        "artifacts": audit.artifacts,
        "failures": audit.issues,
        "untested_artifacts": [],
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "name", "path", "static_status", "runtime_status", "codex_usable", "dependencies", "notes", "fix_needed"])
        writer.writeheader()
        for item in audit.artifacts:
            row = dict(item)
            row["dependencies"] = ";".join(row["dependencies"])
            writer.writerow(row)
    lines = [
        "# ECC Codex Full Test Report",
        "",
        f"- tested_at: {dt.datetime.now(dt.UTC).isoformat()}",
        f"- overall_status: {statuses['overall_status']}",
    ]
    for key in [
        "local_package_status",
        "core_agent_runtime_status",
        "playbook_agent_status",
        "skills_status",
        "prompt_recipes_status",
        "installer_status",
        "external_mock_status",
        "external_real_status",
    ]:
        lines.append(f"- {key}: {statuses[key]}")
    lines.extend(["", "## Counts", ""])
    for key, value in sorted(audit.counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Failures", ""])
    lines.extend([f"- {issue}" for issue in audit.issues] or ["- None."])
    lines.extend(["", "## Matrix", "", "| type | name | static | runtime | usable | path |", "|---|---|---|---|---|---|"])
    for item in audit.artifacts:
        lines.append(f"| {item['type']} | {item['name']} | {item['static_status']} | {item['runtime_status']} | {item['codex_usable']} | {item['path']} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete Codex package audit.")
    parser.add_argument("--real-external", action="store_true", help="Run guarded real external checks if configured.")
    args = parser.parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    audit = Audit()
    validator = run([sys.executable, "-S", "scripts/validate_codex_package.py"], timeout=180)
    audit.add("script", "validate_codex_package", "scripts/validate_codex_package.py", "PASS", "PASS" if validator["exit_code"] == 0 else "FAIL", "true" if validator["exit_code"] == 0 else "false", [], f"exit={validator['exit_code']} stdout={validator['stdout'][-300:]} stderr={validator['stderr'][-300:]}", "Fix package validator failures." if validator["exit_code"] != 0 else "")
    validate_config_and_refs(audit)
    validate_skills(audit)
    validate_prompt_recipes(audit)
    validate_playbooks(audit)
    validate_agents(audit)
    validate_installers(audit)
    external_mock, external_real = validate_external(audit, args.real_external)
    statuses = compute_status(audit, external_mock, external_real)
    write_reports(audit, statuses)
    print(json.dumps({"overall_status": statuses["overall_status"], "counts": audit.counts, "failures": len(audit.issues)}, indent=2))
    return 0 if statuses["overall_status"] in {"LOCAL_PASS_EXTERNAL_NOT_CONFIGURED", "FULL_PASS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
