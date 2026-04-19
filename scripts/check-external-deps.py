#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXTERNAL_SKILLS = {
    "bun-runtime": {"tools": ["bun"], "env": [], "mcp": []},
    "claude-api": {"tools": [], "env": ["ANTHROPIC_API_KEY"], "mcp": []},
    "crosspost": {"tools": [], "env": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"], "mcp": []},
    "deep-research": {"tools": [], "env": ["EXA_API_KEY", "FIRECRAWL_API_KEY"], "mcp": ["exa"]},
    "dmux-workflows": {"tools": ["tmux"], "env": [], "mcp": []},
    "documentation-lookup": {"tools": ["npx"], "env": [], "mcp": ["context7"]},
    "e2e-testing": {"tools": ["npx"], "env": [], "mcp": ["playwright"]},
    "exa-search": {"tools": [], "env": ["EXA_API_KEY"], "mcp": ["exa"]},
    "fal-ai-media": {"tools": [], "env": ["FAL_KEY"], "mcp": []},
    "video-editing": {"tools": ["ffmpeg", "npx"], "env": ["FAL_KEY"], "mcp": []},
    "x-api": {"tools": [], "env": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"], "mcp": []},
}


def mcp_status() -> dict[str, dict[str, object]]:
    config = ROOT / ".codex" / "config.toml"
    if not config.exists():
        return {}
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    servers = data.get("mcp_servers", {})
    return {
        name: {
            "enabled": bool(value.get("enabled", False)),
            "command": value.get("command"),
            "url": value.get("url"),
            "required": bool(value.get("required", False)),
        }
        for name, value in sorted(servers.items())
    }


def check() -> dict[str, object]:
    mcp = mcp_status()
    skills = {}
    missing_tools: set[str] = set()
    missing_env: set[str] = set()
    missing_mcp: set[str] = set()
    for skill, req in EXTERNAL_SKILLS.items():
        tools = {tool: bool(shutil.which(tool)) for tool in req["tools"]}
        env = {name: bool(os.environ.get(name)) for name in req["env"]}
        mcps = {name: bool(mcp.get(name, {}).get("enabled")) for name in req["mcp"]}
        missing_tools.update(tool for tool, ok in tools.items() if not ok)
        missing_env.update(name for name, ok in env.items() if not ok)
        missing_mcp.update(name for name, ok in mcps.items() if not ok)
        skills[skill] = {
            "tools": tools,
            "env": env,
            "mcp": mcps,
            "can_run_real_tests": all(tools.values()) and all(env.values()) and all(mcps.values()),
        }
    can_run_real = all(item["can_run_real_tests"] for item in skills.values())
    return {
        "available": can_run_real,
        "missing_tools": sorted(missing_tools),
        "missing_env": sorted(missing_env),
        "missing_mcp": sorted(missing_mcp),
        "mcp_status": mcp,
        "skills": skills,
        "can_run_real_tests": can_run_real,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check external dependencies for Codex skills.")
    parser.add_argument("--json", dest="json_path", help="Write JSON result to this path.")
    args = parser.parse_args()
    result = check()
    payload = json.dumps(result, indent=2, ensure_ascii=True)
    if args.json_path:
        path = Path(args.json_path)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
