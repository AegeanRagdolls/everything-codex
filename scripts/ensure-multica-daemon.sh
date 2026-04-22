#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '%s\n' "$*"
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

json_daemon_status() {
  python3 -c '
import json
import sys

data = json.load(sys.stdin)
print(data.get("status", ""))
'
}

daemon_status() {
  local status_json status plain
  status_json="$(multica daemon status --output json 2>/dev/null || true)"
  if [[ -n "$status_json" ]]; then
    status="$(printf '%s\n' "$status_json" | json_daemon_status 2>/dev/null || true)"
    if [[ -n "$status" ]]; then
      printf '%s\n' "$status"
      return 0
    fi
  fi

  plain="$(multica daemon status 2>/dev/null || true)"
  case "$plain" in
    *"Daemon:"*"running"*) printf 'running\n' ;;
    *"Daemon:"*"stopped"*) printf 'stopped\n' ;;
    *) printf 'unknown\n' ;;
  esac
}

main() {
  require_command python3
  require_command multica

  multica auth status >/dev/null 2>&1 || die "Multica auth is not ready. Run: multica setup"

  if [[ "$(daemon_status)" == "running" ]]; then
    log "Multica daemon already running."
    return
  fi

  log "Starting Multica daemon..."
  multica daemon start >/dev/null
  sleep 2

  if [[ "$(daemon_status)" != "running" ]]; then
    die "Multica daemon did not reach running state"
  fi

  log "Multica daemon is running."
}

main "$@"
