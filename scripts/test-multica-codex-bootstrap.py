#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap-multica-codex-team.sh"

CORE_AGENTS = [
    "planner",
    "explorer",
    "code_reviewer",
    "security_reviewer",
    "docs_researcher",
    "test_runner",
    "build_fixer",
    "refactor_cleaner",
]

MUTATING_MULTICA_PREFIXES = (
    "agent add",
    "agent create",
    "agent delete",
    "agent remove",
    "agent rm",
    "agent update",
    "apply",
    "bootstrap",
    "create",
    "delete",
    "init",
    "install",
    "issue create",
    "issue delete",
    "issue update",
    "remove",
    "rm",
    "run",
    "team add",
    "team create",
    "team delete",
    "team remove",
    "team rm",
    "team update",
    "update",
    "write",
)


class MulticaCodexBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.sandbox = Path(self.temp_dir.name)
        self.project = self.sandbox / "project"
        self.project.mkdir()
        self.bin_dir = self.sandbox / "bin"
        self.bin_dir.mkdir()
        self.command_log = self.sandbox / "commands.log"
        self._write_fake_commands()

    def test_help_works(self) -> None:
        result = self.run_bootstrap("--help")

        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertOutputContainsAll(
            result,
            "Usage:",
            "--dry-run",
            "--create-smoke-issue",
            "--audit-language",
            "--manual-review-gate",
            "--install-windows-autostart",
        )

    def test_missing_project_path_fails(self) -> None:
        result = self.run_bootstrap("--dry-run")

        self.assertNotEqual(result.returncode, 0, self.combined_output(result))
        self.assertOutputContainsAll(result, "project", "path")

    def test_dry_run_prints_install_command_and_agent_team_plan(self) -> None:
        result = self.run_bootstrap("--dry-run", str(self.project))

        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertOutputContainsAll(
            result,
            "dry-run",
            "install-codex.py",
            "--core",
            "multica",
            "team",
            "简体中文",
            "move issues to done",
            *CORE_AGENTS,
        )

    def test_dry_run_is_repeatable_and_does_not_invoke_mutating_multica_commands(self) -> None:
        first = self.run_bootstrap("--dry-run", str(self.project))
        second = self.run_bootstrap("--dry-run", str(self.project))

        self.assertEqual(first.returncode, 0, self.combined_output(first))
        self.assertEqual(second.returncode, 0, self.combined_output(second))
        self.assertOutputContainsAll(second, "dry-run", "install-codex.py", *CORE_AGENTS)
        self.assertNoMutatingMulticaCommands()

    def test_create_smoke_issue_dry_run_includes_issue_create_plan(self) -> None:
        result = self.run_bootstrap("--dry-run", "--create-smoke-issue", str(self.project))

        self.assertEqual(result.returncode, 0, self.combined_output(result))
        self.assertOutputContainsAll(result, "dry-run", "issue", "create", "smoke")
        self.assertNoMutatingMulticaCommands()

    def test_bootstrap_contract_blocks_vague_requests_before_dispatch(self) -> None:
        script = BOOTSTRAP.read_text(encoding="utf-8")

        self.assertIn("对模糊需求、新产品想法", script)
        self.assertIn("只能发布需求澄清评论", script)
        self.assertIn("不创建开发、测试、审查或集成子 issue", script)
        self.assertIn("不得把默认绑定项目路径或 Codex 能力包路径自动当成新产品的目标代码仓库", script)
        self.assertIn("只有用户明确确认范围并要求", script)

    def run_bootstrap(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["FAKE_COMMAND_LOG"] = str(self.command_log)
        env["REAL_PYTHON3"] = sys.executable
        return subprocess.run(
            ["bash", str(BOOTSTRAP), *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

    def assertOutputContainsAll(self, result: subprocess.CompletedProcess[str], *needles: str) -> None:
        output = self.combined_output(result).lower()
        missing = [needle for needle in needles if needle.lower() not in output]
        if missing:
            self.fail(f"missing output text {missing!r}\n--- output ---\n{self.combined_output(result)}")

    def combined_output(self, result: subprocess.CompletedProcess[str]) -> str:
        return (result.stdout or "") + (result.stderr or "")

    def assertNoMutatingMulticaCommands(self) -> None:
        for command in self.logged_commands("multica"):
            normalized = " ".join(command.split())
            for prefix in MUTATING_MULTICA_PREFIXES:
                if normalized == prefix or normalized.startswith(prefix + " "):
                    self.fail(f"dry-run invoked mutating multica command: multica {command}")

    def logged_commands(self, tool: str) -> list[str]:
        if not self.command_log.exists():
            return []
        prefix = f"{tool}\t"
        return [
            line[len(prefix) :].strip()
            for line in self.command_log.read_text(encoding="utf-8").splitlines()
            if line.startswith(prefix)
        ]

    def _write_fake_commands(self) -> None:
        self._write_executable(
            "multica",
            """
            #!/bin/sh
            printf 'multica\\t%s\\n' "$*" >> "$FAKE_COMMAND_LOG"
            case "$1" in
              --version|version)
                echo "multica fake 0.0.0"
                ;;
              *)
                echo "fake multica $*"
                ;;
            esac
            """,
        )
        self._write_executable(
            "codex",
            """
            #!/bin/sh
            printf 'codex\\t%s\\n' "$*" >> "$FAKE_COMMAND_LOG"
            case "$1" in
              --version|version)
                echo "codex fake 0.0.0"
                ;;
              *)
                echo "fake codex $*"
                ;;
            esac
            """,
        )
        self._write_executable(
            "python3",
            """
            #!/bin/sh
            printf 'python3\\t%s\\n' "$*" >> "$FAKE_COMMAND_LOG"
            for arg in "$@"; do
              case "$arg" in
                */scripts/install-codex.py|scripts/install-codex.py)
                  echo "fake python3 $*"
                  exit 0
                  ;;
              esac
            done
            exec "$REAL_PYTHON3" "$@"
            """,
        )

    def _write_executable(self, name: str, body: str) -> None:
        path = self.bin_dir / name
        script = textwrap.dedent(body).lstrip() + "\n"
        path.write_text(script, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
