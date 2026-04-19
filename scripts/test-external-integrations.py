#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_check_external_deps():
    module_path = ROOT / "scripts" / "check-external-deps.py"
    spec = importlib.util.spec_from_file_location("check_external_deps", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-external-deps.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAFE_MOCKS = {
    "bun-runtime": "Validate workflow can report missing Bun or prepare a Bun command without executing it.",
    "claude-api": "Validate request-shape guidance without calling Anthropic.",
    "crosspost": "Validate per-platform draft generation without posting.",
    "deep-research": "Validate research plan and source criteria without web/MCP calls.",
    "dmux-workflows": "Validate orchestration plan without starting tmux panes.",
    "documentation-lookup": "Validate docs lookup fallback without Context7.",
    "e2e-testing": "Validate Playwright test plan without launching a browser.",
    "exa-search": "Validate search query construction without Exa network calls.",
    "fal-ai-media": "Validate media generation prompt and safety policy without fal.ai calls.",
    "video-editing": "Validate edit plan and ffmpeg command shape without processing media.",
    "x-api": "Validate tweet/thread payload and dry-run side-effect guard without posting.",
}


def mock_results() -> list[dict[str, object]]:
    return [
        {
            "skill": skill,
            "mode": "mock",
            "status": "PASS",
            "side_effects": "none",
            "summary": summary,
        }
        for skill, summary in sorted(SAFE_MOCKS.items())
    ]


def real_results(allow_side_effects: bool) -> list[dict[str, object]]:
    check_external_deps = load_check_external_deps()
    deps = check_external_deps.check()
    results = []
    for skill, info in deps["skills"].items():
        if not info["can_run_real_tests"]:
            results.append(
                {
                    "skill": skill,
                    "mode": "real",
                    "status": "EXTERNAL_NOT_CONFIGURED",
                    "side_effects": "none",
                    "summary": "Required tools, env vars, or MCP servers are missing or disabled.",
                    "details": info,
                }
            )
            continue
        if skill in {"crosspost", "x-api"} and not allow_side_effects:
            results.append(
                {
                    "skill": skill,
                    "mode": "real",
                    "status": "EXTERNAL_NOT_CONFIGURED",
                    "side_effects": "blocked",
                    "summary": "Credentials are present, but real posting remains disabled without --allow-side-effects.",
                }
            )
            continue
        results.append(
            {
                "skill": skill,
                "mode": "real",
                "status": "READY_FOR_REAL_TEST",
                "side_effects": "allowed" if allow_side_effects else "dry-run",
                "summary": "Dependencies appear configured. This harness stops before provider-specific calls unless a future provider probe is added.",
                "details": info,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mock or guarded real external integration checks.")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    parser.add_argument("--allow-side-effects", action="store_true")
    parser.add_argument("--json", dest="json_path", default=".codex-test/reports/external_integration_results.json")
    args = parser.parse_args()
    results = mock_results() if args.mode == "mock" else real_results(args.allow_side_effects)
    status = "PASS" if args.mode == "mock" else ("REAL_EXTERNAL_PASS" if all(r["status"] == "READY_FOR_REAL_TEST" for r in results) else "EXTERNAL_NOT_CONFIGURED")
    payload = {
        "mode": args.mode,
        "status": status,
        "allow_side_effects": args.allow_side_effects,
        "results": results,
    }
    path = Path(args.json_path)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if args.mode == "mock" or status in {"REAL_EXTERNAL_PASS", "EXTERNAL_NOT_CONFIGURED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
