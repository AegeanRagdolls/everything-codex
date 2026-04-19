#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_HOME="${CODEX_SKILLS_HOME:-$HOME/.agents/skills}"
MODE="core"
DRY_RUN=0
FORCE=0
INSTALL_CONFIG=1

usage() {
  cat <<'ECC_USAGE'
Usage: scripts/install-codex.sh [--core|--all] [--dry-run] [--force] [--no-config] [--codex-home PATH] [--skills-home PATH]

  --core          Install curated skills only (default)
  --all           Install curated + experimental skills
  --dry-run       Print actions without changing files
  --force         Replace existing installed skill folders
  --no-config     Do not install/copy .codex/config.toml
  --codex-home    Override Codex config home (default: ~/.codex)
  --skills-home   Override Codex user skills dir (default: ~/.agents/skills)

Codex scans user skills from $HOME/.agents/skills and repo skills from .agents/skills.
ECC_USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --core) MODE="core"; shift ;;
    --all) MODE="all"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --no-config) INSTALL_CONFIG=0; shift ;;
    --codex-home) CODEX_HOME="$2"; shift 2 ;;
    --skills-home) SKILLS_HOME="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '[dry-run]'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

install_skill_dir() {
  local src="$1"
  local name
  name="$(basename "$src")"
  local dest="$SKILLS_HOME/$name"
  if [[ -e "$dest" && "$FORCE" != "1" ]]; then
    echo "skip existing skill: $name (use --force to replace)"
    return 0
  fi
  if [[ -e "$dest" ]]; then
    run rm -rf "$dest"
  fi
  run mkdir -p "$SKILLS_HOME"
  run cp -R "$src" "$dest"
  echo "installed skill: $name"
}

install_bucket() {
  local bucket="$1"
  for src in "$ROOT"/skills/"$bucket"/*; do
    [[ -d "$src" ]] || continue
    install_skill_dir "$src"
  done
}

echo "Codex config home: $CODEX_HOME"
echo "Codex skills home: $SKILLS_HOME"
echo "Mode: $MODE"
run mkdir -p "$CODEX_HOME" "$SKILLS_HOME"

install_bucket ".curated"

if [[ "$MODE" == "all" ]]; then
  install_bucket ".experimental"
fi

if [[ "$INSTALL_CONFIG" == "1" ]]; then
  if [[ ! -f "$CODEX_HOME/config.toml" ]]; then
    run cp "$ROOT/.codex/config.toml" "$CODEX_HOME/config.toml"
    echo "installed Codex config.toml"
  else
    run mkdir -p "$CODEX_HOME/everything-codex-code"
    run cp "$ROOT/.codex/config.toml" "$CODEX_HOME/everything-codex-code/config.toml"
    echo "existing config.toml preserved; reference copied to $CODEX_HOME/everything-codex-code/config.toml"
  fi
fi

echo "Done. Restart Codex to pick up newly installed skills."
