#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_NAME="MulticaDaemonWSL"
DISTRO="${WSL_DISTRO_NAME:-Ubuntu}"
DRY_RUN=0
RUN_NOW=0
MODE="auto"

usage() {
  cat <<'EOF'
Usage: scripts/install-windows-wsl-multica-autostart.sh [options]

Install or update a Windows Task Scheduler entry that starts the WSL-hosted
Multica daemon at Windows logon.

Options:
  --task-name NAME   Windows scheduled task name. Default: MulticaDaemonWSL.
  --distro NAME      WSL distro name. Default: current WSL_DISTRO_NAME or Ubuntu.
  --mode MODE        Install mode: auto, startup, or task. Default: auto.
  --run-now          Trigger the launcher immediately after installation.
  --dry-run          Print the chosen install actions without mutating Windows startup settings.
  -h, --help         Show this help.
EOF
}

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

shell_quote() {
  printf '%q' "$1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task-name) TASK_NAME="$2"; shift 2 ;;
      --distro) DISTRO="$2"; shift 2 ;;
      --mode) MODE="$2"; shift 2 ;;
      --run-now) RUN_NOW=1; shift ;;
      --dry-run) DRY_RUN=1; shift ;;
      -h|--help) usage; exit 0 ;;
      --*) die "unknown option: $1" ;;
      *) die "unexpected argument: $1" ;;
    esac
  done
}

windows_startup_dir() {
  powershell.exe -NoProfile -Command "[Environment]::GetFolderPath('Startup')" | tr -d '\r'
}

create_startup_launcher() {
  local ps1_path startup_dir startup_dir_wsl launcher_path_wsl
  ps1_path="$(wslpath -w "$ROOT/scripts/start-multica-daemon-wsl.ps1")"
  startup_dir="$(windows_startup_dir)"
  [[ -n "$startup_dir" ]] || die "could not determine Windows Startup folder"
  startup_dir_wsl="$(wslpath -u "$startup_dir")"
  launcher_path_wsl="$startup_dir_wsl/${TASK_NAME}.cmd"

  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] write startup launcher: $launcher_path_wsl"
    log "[dry-run] launcher command: powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$ps1_path\" -Distro \"$DISTRO\""
    return
  fi

  mkdir -p "$startup_dir_wsl"
  python3 - <<'PY' "$launcher_path_wsl" "$ps1_path" "$DISTRO"
from pathlib import Path
import sys

launcher_path = Path(sys.argv[1])
ps1_path = sys.argv[2]
distro = sys.argv[3]
content = (
    "@echo off\r\n"
    f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{ps1_path}" -Distro "{distro}"\r\n'
)
launcher_path.write_text(content, encoding="ascii", newline="")
PY
  log "Installed Windows Startup launcher: $launcher_path_wsl"
}

create_schtask() {
  local ps1_path task_command
  ps1_path="$(wslpath -w "$ROOT/scripts/start-multica-daemon-wsl.ps1")"
  task_command="powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$ps1_path\" -Distro \"$DISTRO\""

  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] schtasks.exe /Create /TN \"$TASK_NAME\" /SC ONLOGON /TR \"$task_command\" /F"
    return
  fi

  schtasks.exe /Create /TN "$TASK_NAME" /SC ONLOGON /TR "$task_command" /F >/dev/null
  log "Installed Windows scheduled task: $TASK_NAME"
}

main() {
  parse_args "$@"

  require_command schtasks.exe
  require_command wslpath

  log "Windows autostart plan:"
  log "  task name: $TASK_NAME"
  log "  distro: $DISTRO"
  log "  mode: $MODE"
  log "  launcher: $(wslpath -w "$ROOT/scripts/start-multica-daemon-wsl.ps1")"

  case "$MODE" in
    startup)
      create_startup_launcher
      ;;
    task)
      create_schtask
      ;;
    auto)
      if create_schtask; then
        :
      else
        log "Scheduled task install failed; falling back to Windows Startup folder."
        create_startup_launcher
      fi
      ;;
    *)
      die "--mode must be one of: auto, startup, task"
      ;;
  esac

  if [[ "$RUN_NOW" == "1" ]]; then
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$ROOT/scripts/start-multica-daemon-wsl.ps1")" -Distro "$DISTRO" >/dev/null
    log "Triggered launcher immediately."
  fi
}

main "$@"
