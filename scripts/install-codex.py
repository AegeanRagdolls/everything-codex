#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_dir(src: Path, dest: Path, *, dry_run: bool, force: bool) -> None:
    if dest.exists() and not force:
        print(f"skip existing skill: {dest.name} (use --force to replace)")
        return
    if dest.exists():
        if dry_run:
            print(f"[dry-run] remove {dest}")
        else:
            shutil.rmtree(dest)
    if dry_run:
        print(f"[dry-run] copy {src} -> {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)
    print(f"installed skill: {dest.name}")


def copy_file(src: Path, dest: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] copy {src} -> {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def install_bucket(bucket: str, skills_home: Path, *, dry_run: bool, force: bool) -> int:
    count = 0
    base = ROOT / "skills" / bucket
    for src in sorted(p for p in base.iterdir() if p.is_dir()):
        copy_dir(src, skills_home / src.name, dry_run=dry_run, force=force)
        count += 1
    return count


def install_agents(codex_home: Path, include_playbooks: bool, *, dry_run: bool, force: bool) -> int:
    count = 0
    dest_dir = codex_home / "agents"
    for src in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
        is_playbook = src.stem.startswith("playbook_")
        if is_playbook and not include_playbooks:
            continue
        dest = dest_dir / src.name
        if dest.exists() and not force:
            print(f"skip existing agent: {src.name} (use --force to replace)")
            continue
        if dry_run:
            print(f"[dry-run] copy agent {src} -> {dest}")
        else:
            copy_file(src, dest, dry_run=False)
            print(f"installed agent: {src.name}")
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform installer for Everything Codex Code.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--core", action="store_true", help="Install curated skills only (default).")
    mode.add_argument("--all", action="store_true", help="Install curated and experimental skills.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-config", action="store_true")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--skills-home", default=os.environ.get("CODEX_SKILLS_HOME", str(Path.home() / ".agents" / "skills")))
    parser.add_argument("--install-agents", action="store_true", help="Install core custom-agent TOML files into Codex home.")
    parser.add_argument("--install-playbook-agents", action="store_true", help="Also install playbook_* custom-agent TOML files.")
    args = parser.parse_args()

    codex_home = Path(args.codex_home).expanduser().resolve()
    skills_home = Path(args.skills_home).expanduser().resolve()
    mode_name = "all" if args.all else "core"
    print(f"Codex config home: {codex_home}")
    print(f"Codex skills home: {skills_home}")
    print(f"Mode: {mode_name}")
    if args.dry_run:
        print(f"[dry-run] create {codex_home}")
        print(f"[dry-run] create {skills_home}")
    else:
        codex_home.mkdir(parents=True, exist_ok=True)
        skills_home.mkdir(parents=True, exist_ok=True)

    installed = install_bucket(".curated", skills_home, dry_run=args.dry_run, force=args.force)
    if args.all:
        installed += install_bucket(".experimental", skills_home, dry_run=args.dry_run, force=args.force)

    agent_count = 0
    if args.install_agents or args.install_playbook_agents:
        agent_count = install_agents(codex_home, args.install_playbook_agents, dry_run=args.dry_run, force=args.force)

    if not args.no_config:
        config_src = ROOT / ".codex" / "config.toml"
        config_dest = codex_home / "config.toml"
        if not config_dest.exists():
            copy_file(config_src, config_dest, dry_run=args.dry_run)
            print("installed Codex config.toml")
        else:
            ref_dest = codex_home / "everything-codex-code" / "config.toml"
            copy_file(config_src, ref_dest, dry_run=args.dry_run)
            print(f"existing config.toml preserved; reference copied to {ref_dest}")

    print(f"installed_skill_count={installed}")
    print(f"installed_agent_count={agent_count}")
    print("Done. Restart Codex to pick up newly installed skills or agents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
