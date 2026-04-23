#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import stat
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN_MARKER = "<!-- everything-codex-deploy:start -->"
END_MARKER = "<!-- everything-codex-deploy:end -->"
GITATTR_BEGIN_MARKER = "# everything-codex-deploy:start"
GITATTR_END_MARKER = "# everything-codex-deploy:end"


AGENTS_BLOCK = """\
{begin}
# Everything Codex Code Operating Rules

This workspace has the Everything Codex Code capability pack installed.
Treat Codex as the runtime. Prefer Codex skills, custom agents, prompt recipes,
and project hooks over Claude-only commands or Claude-only hook formats.

## Default Agent Team Mode

- Use multi-subagent collaboration by default for non-trivial work when the
  runtime supports subagents.
- Classify the task first, then compose the smallest useful Agent Team:
  - Planning, architecture, or multi-step features: `planner` plus `explorer`.
  - Codebase investigation: `explorer`.
  - Library, framework, API, or setup questions: `docs_researcher`.
  - Feature work or bug fixes: `test_runner` first, then implementation, then
    `build_fixer` if checks fail, then `code_reviewer`.
  - Security-sensitive work involving auth, user input, secrets, file upload,
    APIs, payments, or permissions: add `security_reviewer`.
  - Cleanup or dead-code work: `refactor_cleaner`.
- Keep each subagent task bounded and give it a clear file or responsibility
  scope. Do not duplicate the same task across agents.
- If the current Codex surface cannot spawn subagents, execute the same roles
  sequentially in the main session and say which roles were applied.

## TDD Default For Code Changes

- Writing or changing production code must start with a red test whenever a
  relevant test harness can exist.
- First add or update the smallest targeted test that proves the desired
  behavior or reproduces the bug.
- Run the targeted test and capture the failing result before implementation.
- Only then write production code to make the test pass.
- Finish with the targeted test, then the relevant broader checks.
- If a red test is not feasible, state the concrete blocker before changing
  production code and use the smallest verifiable alternative.

## Skill And Recipe Usage

- Prefer installed skills from `.agents/skills` or the user skills directory
  over loading large prompt files.
- Use `prompt-recipes/` for command-style workflows when no matching skill is a
  better fit.
- Keep secrets out of files. Use environment variables or user-level Codex
  configuration for credentials.

## Verification Standard

- For every code change, report the exact checks run and their results.
- Distinguish dry-run/mock validation from real integration validation.
- Do not claim hooks, agents, skills, or MCP integrations are active unless they
  were actually loaded or tested in this environment.
{end}
""".format(begin=BEGIN_MARKER, end=END_MARKER)


GITATTRIBUTES_BLOCK = """\
{begin}
.codex/hooks.json text eol=lf
.codex/hooks/*.py text eol=lf
scripts/codex-git-hooks/* text eol=lf
{end}
""".format(begin=GITATTR_BEGIN_MARKER, end=GITATTR_END_MARKER)


BASE_CONFIG_TEXT = """\
# Everything Codex Code deployment config
# Keep model/model_provider unset so Codex uses the current supported default.

approval_policy = "on-request"
sandbox_mode = "workspace-write"
model_reasoning_effort = "medium"
model_reasoning_summary = "auto"
model_verbosity = "medium"
web_search = "live"

developer_instructions = \"\"\"
Default to multi-subagent collaboration for non-trivial tasks when the runtime
supports subagents. Classify the task and compose the smallest useful Agent Team:
planner/explorer for planning and architecture, explorer for codebase tracing,
docs_researcher for current docs, test_runner for code changes, build_fixer for
failing checks, code_reviewer after modifications, security_reviewer for
security-sensitive surfaces, and refactor_cleaner for cleanup. If subagents are
unavailable, execute these roles sequentially in the main session.

For code changes, use TDD by default: add or update the smallest targeted test,
run it and observe the red failure, then implement production code, then rerun
the targeted test and relevant broader checks. If a red test is not feasible,
state the concrete blocker before changing production code.
\"\"\"

[features]
child_agents_md = true
multi_agent = true
codex_hooks = true
skill_mcp_dependency_install = true
skill_env_var_dependency_prompt = true

[agents]
max_threads = 4
max_depth = 1
job_max_runtime_seconds = 180

[agents.planner]
description = "Planning specialist for complex features, architecture, sequencing, decomposition, and Agent Team design. Use first for multi-step implementation or refactoring."
config_file = "agents/planner.toml"

[agents.explorer]
description = "Read-only codebase explorer for tracing behavior, architecture, dependencies, and current implementation before edits."
config_file = "agents/explorer.toml"

[agents.docs_researcher]
description = "Documentation researcher for current library, framework, API, and setup questions."
config_file = "agents/docs_researcher.toml"

[agents.test_runner]
description = "TDD and verification specialist. Use first for code changes to create or identify the red failing test before implementation."
config_file = "agents/test_runner.toml"

[agents.build_fixer]
description = "Build and type-error fixer. Use after failing compile, lint, typecheck, or test output is available."
config_file = "agents/build_fixer.toml"

[agents.code_reviewer]
description = "Code review specialist. Use after modifications to check correctness, maintainability, regressions, and missing tests."
config_file = "agents/code_reviewer.toml"

[agents.security_reviewer]
description = "Security reviewer for auth, user input, APIs, secrets, file access, payments, permissions, injection, SSRF, and unsafe crypto."
config_file = "agents/security_reviewer.toml"

[agents.refactor_cleaner]
description = "Refactoring and cleanup specialist for duplicate logic, dead code, and low-risk maintainability improvements."
config_file = "agents/refactor_cleaner.toml"

# Optional MCP defaults. Disabled by default so first run does not depend on
# Node, network access, or API keys.
[mcp_servers.github]
enabled = false
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
startup_timeout_sec = 30

[mcp_servers.context7]
enabled = false
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]
startup_timeout_sec = 30

[mcp_servers.exa]
enabled = false
url = "https://mcp.exa.ai/mcp"

[mcp_servers.memory]
enabled = false
command = "npx"
args = ["-y", "@modelcontextprotocol/server-memory"]
startup_timeout_sec = 30

[mcp_servers.playwright]
enabled = false
command = "npx"
args = ["-y", "@playwright/mcp@latest", "--extension"]
startup_timeout_sec = 30

[mcp_servers.sequential-thinking]
enabled = false
command = "npx"
args = ["-y", "@modelcontextprotocol/server-sequential-thinking"]
startup_timeout_sec = 30

[profiles.readonly]
approval_policy = "untrusted"
sandbox_mode = "read-only"
model_reasoning_effort = "medium"

[profiles.autonomous]
approval_policy = "on-request"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"
"""


HOOKS_JSON = """\
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.codex/hooks/session_start.py\\"",
            "statusMessage": "Starting project Codex hooks",
            "timeout": 30
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.codex/hooks/pre_tool_use.py\\"",
            "statusMessage": "Checking shell command",
            "timeout": 30
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.codex/hooks/permission_request.py\\"",
            "statusMessage": "Checking approval request",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.codex/hooks/post_tool_use.py\\"",
            "statusMessage": "Recording shell result",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.codex/hooks/stop.py\\"",
            "statusMessage": "Finalizing project Codex hooks",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
"""


HOOK_COMMON = """\
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = REPO_ROOT / ".codex" / "hooks" / "logs"
LOG_FILE = LOG_DIR / "events.jsonl"


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw_stdin": raw[:4000]}
    return payload if isinstance(payload, dict) else {"_payload": payload}


def write_event(payload: dict[str, Any], extra: dict[str, Any] | None = None) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": payload.get("hook_event_name"),
            "cwd": payload.get("cwd"),
            "model": payload.get("model"),
            "tool_name": payload.get("tool_name"),
        }
        command = payload.get("tool_input", {}).get("command")
        if command:
            event["command"] = command[:2000]
        if extra:
            event.update(extra)
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True) + "\\n")
    except OSError:
        pass


def command_from(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    return ""


BLOCKED_COMMANDS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(^|\\s)rm\\s+-rf\\s+/(?:\\s|$)"), "Refusing to run rm -rf against filesystem root."),
    (re.compile(r"(^|\\s)rm\\s+-rf\\s+\\$HOME(?:\\s|/|$)"), "Refusing to delete the home directory."),
    (re.compile(r"(^|\\s)rm\\s+-rf\\s+~(?:\\s|/|$)"), "Refusing to delete the home directory."),
    (re.compile(r"(^|\\s)git\\s+reset\\s+--hard(?:\\s|$)"), "git reset --hard requires explicit manual confirmation outside hooks."),
    (re.compile(r"(^|\\s)git\\s+clean\\s+-[A-Za-z]*[fdx][A-Za-z]*\\b"), "git clean destructive cleanup requires explicit manual confirmation outside hooks."),
    (re.compile(r"(^|\\s)chmod\\s+-R\\s+777\\s+/(?:\\s|$)"), "Refusing recursive chmod 777 on filesystem root."),
)


def blocked_reason(command: str) -> str | None:
    for pattern, reason in BLOCKED_COMMANDS:
        if pattern.search(command):
            return reason
    return None


def deny_pre_tool_use(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def deny_permission_request(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "deny", "message": reason}}}))
"""


HOOK_SCRIPTS = {
    "common.py": HOOK_COMMON,
    "session_start.py": """\
from common import read_payload, write_event


def main() -> int:
    write_event(read_payload(), {"status": "session_started"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
    "pre_tool_use.py": """\
from common import blocked_reason, command_from, deny_pre_tool_use, read_payload, write_event


def main() -> int:
    payload = read_payload()
    reason = blocked_reason(command_from(payload))
    write_event(payload, {"status": "denied" if reason else "allowed"})
    if reason:
        deny_pre_tool_use(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
    "permission_request.py": """\
from common import blocked_reason, command_from, deny_permission_request, read_payload, write_event


def main() -> int:
    payload = read_payload()
    reason = blocked_reason(command_from(payload))
    write_event(payload, {"status": "denied" if reason else "no_decision"})
    if reason:
        deny_permission_request(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
    "post_tool_use.py": """\
from common import read_payload, write_event


def main() -> int:
    payload = read_payload()
    response = payload.get("tool_response")
    extra = {"status": "recorded"}
    if response is not None:
        extra["response_preview"] = str(response)[:2000]
    write_event(payload, extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
    "stop.py": """\
from common import read_payload, write_event


def main() -> int:
    write_event(read_payload(), {"status": "session_stopped"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
}


def make_hooks_payload(*, command_home: Path | None) -> dict:
    payload = json.loads(HOOKS_JSON)
    for entries in payload.get("hooks", {}).values():
        for entry in entries:
            for hook in entry.get("hooks", []):
                command = hook.get("command", "")
                if command_home is not None and "/.codex/hooks/" in command:
                    script_name = command.split("/.codex/hooks/", 1)[1].rsplit('"', 1)[0]
                    hook["command"] = f"python3 {shlex.quote(str((command_home / 'hooks' / script_name).resolve()))}"
                status = hook.get("statusMessage", "Codex hook")
                if not status.startswith("Everything Codex:"):
                    hook["statusMessage"] = f"Everything Codex: {status}"
    return payload


def make_hooks_json(*, command_home: Path | None) -> str:
    return json.dumps(make_hooks_payload(command_home=command_home), indent=2) + "\n"


def is_everything_codex_hook_entry(entry: object) -> bool:
    try:
        text = json.dumps(entry, sort_keys=True)
    except TypeError:
        return False
    return "Everything Codex:" in text or (
        "Codex hooks" in text and ("/.codex/hooks/" in text or "/hooks/session_start.py" in text)
    )


def merge_hooks_json(existing_text: str, incoming_text: str) -> str:
    existing = json.loads(existing_text) if existing_text.strip() else {}
    incoming = json.loads(incoming_text)
    if not isinstance(existing, dict):
        existing = {}
    existing_hooks = existing.setdefault("hooks", {})
    if not isinstance(existing_hooks, dict):
        existing["hooks"] = {}
        existing_hooks = existing["hooks"]
    for event_name, incoming_entries in incoming.get("hooks", {}).items():
        current_entries = existing_hooks.get(event_name, [])
        if not isinstance(current_entries, list):
            current_entries = []
        current_entries = [
            entry for entry in current_entries if not is_everything_codex_hook_entry(entry)
        ]
        existing_hooks[event_name] = current_entries + incoming_entries
    return json.dumps(existing, indent=2) + "\n"


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def run_action(message: str, *, dry_run: bool) -> None:
    print(f"[dry-run] {message}" if dry_run else message)


def backup_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.bak-{timestamp()}")


def copy_dir(src: Path, dest: Path, *, dry_run: bool, force: bool) -> None:
    if dest.exists():
        if not force:
            run_action(f"skip existing directory: {dest}", dry_run=dry_run)
            return
        run_action(f"replace directory: {dest}", dry_run=dry_run)
        if not dry_run:
            shutil.rmtree(dest)
    else:
        run_action(f"copy directory: {src} -> {dest}", dry_run=dry_run)
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest)


def copy_file(src: Path, dest: Path, *, dry_run: bool, force: bool = True) -> None:
    if dest.exists() and not force:
        run_action(f"skip existing file: {dest}", dry_run=dry_run)
        return
    run_action(f"copy file: {src} -> {dest}", dry_run=dry_run)
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def write_text(path: Path, text: str, *, dry_run: bool, backup_existing: bool = False) -> None:
    run_action(f"write file: {path}", dry_run=dry_run)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup_existing and path.exists():
        shutil.copy2(path, backup_path(path))
    path.write_text(text, encoding="utf-8", newline="\n")


def chmod_executable(path: Path, *, dry_run: bool) -> None:
    run_action(f"chmod +x: {path}", dry_run=dry_run)
    if not dry_run and path.exists():
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def skill_sources(mode: str) -> list[Path]:
    buckets = [ROOT / "skills" / ".curated"]
    if mode == "all":
        buckets.append(ROOT / "skills" / ".experimental")
    sources: list[Path] = []
    for bucket in buckets:
        sources.extend(sorted(path for path in bucket.iterdir() if path.is_dir()))
    return sources


def install_skills(dest: Path, *, mode: str, dry_run: bool, force: bool) -> int:
    count = 0
    for src in skill_sources(mode):
        copy_dir(src, dest / src.name, dry_run=dry_run, force=force)
        count += 1
    return count


def install_agents(codex_home: Path, *, include_playbooks: bool, dry_run: bool, force: bool) -> int:
    count = 0
    for src in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
        if src.stem.startswith("playbook_") and not include_playbooks:
            continue
        copy_file(src, codex_home / "agents" / src.name, dry_run=dry_run, force=force)
        count += 1
    return count


def config_text(*, include_playbooks: bool) -> str:
    if not include_playbooks:
        return BASE_CONFIG_TEXT
    entries: list[str] = []
    for src in sorted((ROOT / ".codex" / "agents").glob("playbook_*.toml")):
        role = src.stem.removeprefix("playbook_").replace("_", " ")
        entries.append(
            "\n"
            f"[agents.{src.stem}]\n"
            f'description = "Optional playbook-derived agent for {role}. Use only when this specific role matches the task."\n'
            f'config_file = "agents/{src.name}"\n'
        )
    return BASE_CONFIG_TEXT.rstrip() + "\n" + "\n".join(entries) + "\n"


def install_prompt_recipes(target: Path, *, dry_run: bool, force: bool) -> None:
    copy_dir(ROOT / "prompt-recipes", target / "prompt-recipes", dry_run=dry_run, force=force)


def install_git_hook_samples(target: Path, *, dry_run: bool, force: bool) -> None:
    copy_dir(ROOT / "hooks", target / "hooks", dry_run=dry_run, force=force)
    copy_dir(ROOT / "scripts" / "codex-git-hooks", target / "scripts" / "codex-git-hooks", dry_run=dry_run, force=force)
    for name in ("pre-commit", "pre-push"):
        hook = target / "scripts" / "codex-git-hooks" / name
        if hook.exists() or dry_run:
            chmod_executable(hook, dry_run=dry_run)


def install_native_hooks(codex_home: Path, *, command_home: Path | None, dry_run: bool, force: bool) -> None:
    hooks_json = codex_home / "hooks.json"
    incoming_text = make_hooks_json(command_home=command_home)
    if hooks_json.exists() and not force:
        try:
            merged_text = merge_hooks_json(hooks_json.read_text(encoding="utf-8"), incoming_text)
        except (OSError, json.JSONDecodeError):
            copy_file(hooks_json, backup_path(hooks_json), dry_run=dry_run, force=True)
            write_text(hooks_json, incoming_text, dry_run=dry_run)
        else:
            write_text(hooks_json, merged_text, dry_run=dry_run, backup_existing=True)
    else:
        write_text(hooks_json, incoming_text, dry_run=dry_run, backup_existing=hooks_json.exists())
    hooks_dir = codex_home / "hooks"
    for name, text in HOOK_SCRIPTS.items():
        write_text(hooks_dir / name, text, dry_run=dry_run)


def merge_agents_md(path: Path, *, dry_run: bool, force: bool) -> None:
    if not path.exists() or force:
        write_text(path, AGENTS_BLOCK + "\n", dry_run=dry_run, backup_existing=path.exists())
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if BEGIN_MARKER in text and END_MARKER in text:
        before = text.split(BEGIN_MARKER, 1)[0]
        after = text.split(END_MARKER, 1)[1]
        new_text = before.rstrip() + "\n\n" + AGENTS_BLOCK + "\n" + after.lstrip()
    else:
        new_text = AGENTS_BLOCK + "\n" + text
    write_text(path, new_text, dry_run=dry_run, backup_existing=True)


def merge_gitattributes(path: Path, *, dry_run: bool) -> None:
    if not path.exists():
        write_text(path, GITATTRIBUTES_BLOCK + "\n", dry_run=dry_run)
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if GITATTR_BEGIN_MARKER in text and GITATTR_END_MARKER in text:
        before = text.split(GITATTR_BEGIN_MARKER, 1)[0]
        after = text.split(GITATTR_END_MARKER, 1)[1]
        new_text = before.rstrip() + "\n\n" + GITATTRIBUTES_BLOCK + "\n" + after.lstrip()
    else:
        separator = "" if text.endswith("\n") else "\n"
        new_text = text + separator + "\n" + GITATTRIBUTES_BLOCK + "\n"
    write_text(path, new_text, dry_run=dry_run, backup_existing=True)


def write_config(codex_home: Path, *, text: str, dry_run: bool, force: bool, preserve_config: bool) -> None:
    config_path = codex_home / "config.toml"
    if preserve_config and config_path.exists() and not force:
        ref = codex_home / "everything-codex-code" / "config.toml"
        write_text(ref, text, dry_run=dry_run)
        print(f"existing config preserved; deployment config written to {ref}")
        print("warning: global agents and hooks are copied but not activated until this config is merged or --no-preserve-config/--force-config is used.")
        return
    write_text(config_path, text, dry_run=dry_run, backup_existing=config_path.exists())


def deploy_project(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    codex_home = target / ".codex"
    skills_home = target / ".agents" / "skills"
    print(f"Project target: {target}")
    print(f"Mode: {args.mode}")
    skill_count = install_skills(skills_home, mode=args.mode, dry_run=args.dry_run, force=args.force)
    agent_count = install_agents(codex_home, include_playbooks=args.playbook_agents, dry_run=args.dry_run, force=args.force)
    write_config(codex_home, text=config_text(include_playbooks=args.playbook_agents), dry_run=args.dry_run, force=True, preserve_config=False)
    if not args.no_hooks:
        install_native_hooks(codex_home, command_home=None, dry_run=args.dry_run, force=args.force)
    if not args.no_prompt_recipes:
        install_prompt_recipes(target, dry_run=args.dry_run, force=args.force)
    if not args.no_git_hook_samples:
        install_git_hook_samples(target, dry_run=args.dry_run, force=args.force)
    if not args.no_gitattributes:
        merge_gitattributes(target / ".gitattributes", dry_run=args.dry_run)
    if not args.no_agents_md:
        merge_agents_md(target / "AGENTS.md", dry_run=args.dry_run, force=args.force_agents_md)
    print(f"installed_skill_count={skill_count}")
    print(f"installed_agent_count={agent_count}")
    print("Project deployment complete. Restart Codex from the target workspace.")


def deploy_global(args: argparse.Namespace) -> None:
    codex_home = Path(args.codex_home or os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()
    skills_home = Path(args.skills_home or os.environ.get("CODEX_SKILLS_HOME", Path.home() / ".agents" / "skills")).expanduser().resolve()
    print(f"Global Codex home: {codex_home}")
    print(f"Global skills home: {skills_home}")
    print(f"Mode: {args.mode}")
    skill_count = install_skills(skills_home, mode=args.mode, dry_run=args.dry_run, force=args.force)
    agent_count = install_agents(codex_home, include_playbooks=args.playbook_agents, dry_run=args.dry_run, force=args.force)
    write_config(codex_home, text=config_text(include_playbooks=args.playbook_agents), dry_run=args.dry_run, force=args.force_config, preserve_config=args.preserve_config)
    if not args.no_hooks:
        install_native_hooks(codex_home, command_home=codex_home, dry_run=args.dry_run, force=args.force)
    if not args.no_agents_md:
        merge_agents_md(codex_home / "AGENTS.md", dry_run=args.dry_run, force=args.force_agents_md)
    print(f"installed_skill_count={skill_count}")
    print(f"installed_agent_count={agent_count}")
    print("Global deployment complete. Restart Codex.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy Everything Codex Code globally or into the current project."
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--global", dest="scope", action="store_const", const="global", help="Deploy to user-level Codex directories.")
    scope.add_argument("--project", dest="scope", action="store_const", const="project", help="Deploy into a project workspace.")
    parser.set_defaults(scope="project")

    parser.add_argument("--target", default=".", help="Project target directory for --project. Default: current directory.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--core", dest="mode", action="store_const", const="core", help="Install curated skills only.")
    mode.add_argument("--all", dest="mode", action="store_const", const="all", help="Install curated and experimental skills.")
    parser.set_defaults(mode="all")

    parser.add_argument("--codex-home", help="Override global Codex home for --global.")
    parser.add_argument("--skills-home", help="Override global skills home for --global.")
    parser.add_argument("--core-agents-only", dest="playbook_agents", action="store_false", help="Install only the 8 core custom agents.")
    parser.set_defaults(playbook_agents=True)

    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing files.")
    parser.add_argument("--force", action="store_true", help="Replace existing deployed directories/files where applicable.")
    parser.add_argument("--force-config", action="store_true", help="For --global, replace existing config.toml after backing it up.")
    parser.add_argument("--preserve-config", action="store_true", help="For --global, preserve existing config.toml and write a reference config instead of activating it.")
    parser.add_argument("--no-preserve-config", dest="preserve_config", action="store_false", help="For --global, write active config.toml, backing up any existing file. This is the default.")
    parser.set_defaults(preserve_config=False)
    parser.add_argument("--force-agents-md", action="store_true", help="Replace AGENTS.md instead of merging the managed block.")
    parser.add_argument("--no-agents-md", action="store_true", help="Do not generate or update AGENTS.md.")
    parser.add_argument("--no-hooks", action="store_true", help="Do not deploy native Codex hooks.")
    parser.add_argument("--no-prompt-recipes", action="store_true", help="Do not deploy prompt-recipes for project installs.")
    parser.add_argument("--no-git-hook-samples", action="store_true", help="Do not deploy scripts/codex-git-hooks for project installs.")
    parser.add_argument("--no-gitattributes", action="store_true", help="Do not add project .gitattributes rules for deployed hook line endings.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.scope == "global":
        deploy_global(args)
    else:
        deploy_project(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
