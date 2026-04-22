#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DRY_RUN=0
CREATE_SMOKE_ISSUE=0
SKIP_CODEX_INSTALL=0
INSTALL_WINDOWS_AUTOSTART=0
WORKSPACE_ID="${MULTICA_WORKSPACE_ID:-}"
PROJECT_PATH=""
BOUND_PROJECT_LABEL="未绑定"
CAPABILITY_PACK_SOURCE="${CODEX_CAPABILITY_PACK_SOURCE:-https://github.com/AegeanRagdolls/everything-codex}"
PM_AGENT_NAME="产品经理 / 项目调度"
DEV_AGENT_PREFIX="ECC Dev"
DEV_AGENT_COUNT=2
TESTER_AGENT_NAME="ECC Tester"
REVIEWER_AGENT_NAME="ECC Reviewer"
PROJECT_TITLE="Everything Codex Code Agent Team"
SMOKE_ISSUE_TITLE="验证 Multica Codex 智能协作团队"
AUDIT_LANGUAGE="简体中文"
MANUAL_REVIEW_GATE=0
SKILL_NAME="Codex Agent Team Orchestration"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_HOME="${CODEX_SKILLS_HOME:-$HOME/.agents/skills}"
LEGACY_SMOKE_ISSUE_TITLE="Verify Multica Codex agent team"

CORE_CODEX_AGENTS=(
  planner
  explorer
  code_reviewer
  security_reviewer
  docs_researcher
  test_runner
  build_fixer
  refactor_cleaner
)

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap-multica-codex-team.sh [options] [project-path]

Bootstrap a reproducible Multica + Codex agent team.

project-path is optional. Pass it only when this team should be bound to a
specific local business repository. The Codex capability pack can live at any
local clone path and is identified in Multica by source URL, not machine path.

Options:
  --dry-run                     Print the plan and commands without mutating Multica.
  --create-smoke-issue          Create or reuse a smoke project and issue for testing.
  --skip-codex-install          Skip installing this repo's Codex skills and core agents.
  --install-windows-autostart   Install a Windows logon task that starts the WSL-hosted Multica daemon.
  --workspace-id ID             Multica workspace ID. Defaults to MULTICA_WORKSPACE_ID or current CLI context.
  --pm-agent-name NAME          Product manager agent name. Default: 产品经理 / 项目调度.
  --dev-agent-prefix NAME       Prefix for coding workers. Default: ECC Dev.
  --dev-agent-count N           Number of coding workers. Default: 2.
  --tester-agent-name NAME      Tester agent name. Default: ECC Tester.
  --reviewer-agent-name NAME    Reviewer agent name. Default: ECC Reviewer.
  --project-title TITLE         Multica project title for smoke setup.
  --smoke-issue-title TITLE     Smoke issue title.
  --audit-language LANG         Human audit language. Default: 简体中文.
  --manual-review-gate          Keep completed work in review until a human closes it.
  --skill-name NAME             Multica orchestration skill name.
  --capability-pack-source URL  Capability pack source shown in Multica. Default: https://github.com/AegeanRagdolls/everything-codex.
  --codex-home PATH             Codex config home. Default: ~/.codex.
  --skills-home PATH            Codex user skills directory. Default: ~/.agents/skills.
  -h, --help                    Show this help.

The Multica workspace is a platform workspace, not a local folder. The project
path is written into agent instructions only when explicitly provided. New
product ideas still need a target path or Gitea repo before coding agents work.
USAGE
}

log() {
  printf '%s\n' "$*"
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

shell_quote() {
  printf '%q' "$1"
}

print_command() {
  local prefix="$1"
  shift
  printf '%s' "$prefix"
  local arg
  for arg in "$@"; do
    printf ' '
    shell_quote "$arg"
  done
  printf '\n'
}

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    print_command "[dry-run]" "$@"
  else
    "$@"
  fi
}

capture() {
  "$@"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

json_first_field() {
  local field="$1"
  python3 -c '
import json
import sys

field = sys.argv[1]
data = json.load(sys.stdin)
if isinstance(data, dict):
    print(data.get(field, ""))
elif isinstance(data, list) and data:
    print(data[0].get(field, ""))
' "$field"
}

json_find_id_by_name() {
  local name="$1"
  python3 -c '
import json
import sys

name = sys.argv[1]
data = json.load(sys.stdin)
items = data.get("items", data) if isinstance(data, dict) else data
for item in items or []:
    if item.get("name") == name and item.get("archived_at") is None:
        print(item.get("id", ""))
        break
' "$name"
}

json_find_project_id_by_title() {
  local title="$1"
  python3 -c '
import json
import sys

title = sys.argv[1]
data = json.load(sys.stdin)
items = data.get("items", data) if isinstance(data, dict) else data
for item in items or []:
    if item.get("title") == title:
        print(item.get("id", ""))
        break
' "$title"
}

json_find_issue_id_by_titles() {
  python3 -c '
import json
import sys

titles = set(sys.argv[1:])
data = json.load(sys.stdin)
issues = data.get("issues", data if isinstance(data, list) else [])
for item in issues or []:
    if item.get("title") in titles:
        print(item.get("id", ""))
        break
' "$@"
}

json_find_codex_runtime_id() {
  python3 -c '
import json
import sys

workspace_id = sys.argv[1]
data = json.load(sys.stdin)
items = data.get("items", data) if isinstance(data, dict) else data
fallback = ""
for item in items or []:
    if item.get("provider") != "codex":
        continue
    if workspace_id and item.get("workspace_id") != workspace_id:
        continue
    if not fallback:
        fallback = item.get("id", "")
    if item.get("status") == "online":
        print(item.get("id", ""))
        sys.exit(0)
print(fallback)
' "$WORKSPACE_ID"
}

json_existing_skill_ids_csv() {
  local new_skill_id="$1"
  python3 -c '
import json
import sys

new_skill_id = sys.argv[1]
data = json.load(sys.stdin)
items = data.get("items", data) if isinstance(data, dict) else data
ids = []
for item in items or []:
    sid = item.get("id") or item.get("skill_id")
    if sid and sid not in ids:
        ids.append(sid)
if new_skill_id and new_skill_id not in ids:
    ids.append(new_skill_id)
print(",".join(ids))
' "$new_skill_id"
}

json_daemon_status() {
  python3 -c '
import json
import sys

data = json.load(sys.stdin)
print(data.get("status", ""))
'
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) DRY_RUN=1; shift ;;
      --create-smoke-issue) CREATE_SMOKE_ISSUE=1; shift ;;
      --skip-codex-install) SKIP_CODEX_INSTALL=1; shift ;;
      --install-windows-autostart) INSTALL_WINDOWS_AUTOSTART=1; shift ;;
      --workspace-id) WORKSPACE_ID="$2"; shift 2 ;;
      --pm-agent-name) PM_AGENT_NAME="$2"; shift 2 ;;
      --dev-agent-prefix) DEV_AGENT_PREFIX="$2"; shift 2 ;;
      --dev-agent-count) DEV_AGENT_COUNT="$2"; shift 2 ;;
      --tester-agent-name) TESTER_AGENT_NAME="$2"; shift 2 ;;
      --reviewer-agent-name) REVIEWER_AGENT_NAME="$2"; shift 2 ;;
      --project-title) PROJECT_TITLE="$2"; shift 2 ;;
      --smoke-issue-title) SMOKE_ISSUE_TITLE="$2"; shift 2 ;;
      --audit-language) AUDIT_LANGUAGE="$2"; shift 2 ;;
      --manual-review-gate) MANUAL_REVIEW_GATE=1; shift ;;
      --skill-name) SKILL_NAME="$2"; shift 2 ;;
      --capability-pack-source) CAPABILITY_PACK_SOURCE="$2"; shift 2 ;;
      --codex-home) CODEX_HOME="$2"; shift 2 ;;
      --skills-home) SKILLS_HOME="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      --*) die "unknown option: $1" ;;
      *)
        if [[ -n "$PROJECT_PATH" ]]; then
          die "only one project path is supported"
        fi
        PROJECT_PATH="$1"
        shift
        ;;
    esac
  done
}

normalize_project_path() {
  if [[ -z "$PROJECT_PATH" ]]; then
    BOUND_PROJECT_LABEL="未绑定"
    return
  fi
  [[ -d "$PROJECT_PATH" ]] || die "project path does not exist: $PROJECT_PATH"
  PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
  BOUND_PROJECT_LABEL="$PROJECT_PATH"
}

validate_inputs() {
  [[ "$DEV_AGENT_COUNT" =~ ^[0-9]+$ ]] || die "--dev-agent-count must be an integer"
  (( DEV_AGENT_COUNT >= 1 )) || die "--dev-agent-count must be at least 1"
  [[ -n "$AUDIT_LANGUAGE" ]] || die "--audit-language must not be empty"
  [[ -n "$CAPABILITY_PACK_SOURCE" ]] || die "--capability-pack-source must not be empty"
  if [[ "$CREATE_SMOKE_ISSUE" == "1" && -z "$PROJECT_PATH" ]]; then
    die "--create-smoke-issue requires an explicit project path"
  fi
}

workspace_flags() {
  if [[ -n "$WORKSPACE_ID" ]]; then
    printf '%s\n' "--workspace-id" "$WORKSPACE_ID"
  fi
}

multica_cmd() {
  local args=()
  if [[ -n "$WORKSPACE_ID" ]]; then
    args+=(--workspace-id "$WORKSPACE_ID")
  fi
  args+=("$@")
  run multica "${args[@]}"
}

multica_capture() {
  local args=()
  if [[ -n "$WORKSPACE_ID" ]]; then
    args+=(--workspace-id "$WORKSPACE_ID")
  fi
  args+=("$@")
  capture multica "${args[@]}"
}

daemon_status() {
  local status_json status plain
  status_json="$(multica_capture daemon status --output json 2>/dev/null || true)"
  if [[ -n "$status_json" ]]; then
    status="$(printf '%s\n' "$status_json" | json_daemon_status 2>/dev/null || true)"
    if [[ -n "$status" ]]; then
      printf '%s\n' "$status"
      return 0
    fi
  fi

  plain="$(multica_capture daemon status 2>/dev/null || true)"
  case "$plain" in
    *"Daemon:"*"running"*) printf 'running\n' ;;
    *"Daemon:"*"stopped"*) printf 'stopped\n' ;;
    *) printf 'unknown\n' ;;
  esac
}

ensure_daemon_running() {
  local status
  status="$(daemon_status)"
  if [[ "$status" == "running" ]]; then
    return 0
  fi
  log "Starting Multica daemon..."
  multica_cmd daemon start >/dev/null
  sleep 2
  status="$(daemon_status)"
  [[ "$status" == "running" ]] || die "Multica daemon did not reach running state"
}

print_team_plan() {
  log "Multica Codex team plan:"
  log "  workspace: ${WORKSPACE_ID:-current Multica workspace}"
  log "  optional bound project path: $BOUND_PROJECT_LABEL"
  log "  capability pack source: $CAPABILITY_PACK_SOURCE"
  log "  PM agent: $PM_AGENT_NAME"
  local i
  for (( i = 1; i <= DEV_AGENT_COUNT; i++ )); do
    log "  coding worker: ${DEV_AGENT_PREFIX} ${i}"
  done
  log "  tester agent: $TESTER_AGENT_NAME"
  log "  reviewer agent: $REVIEWER_AGENT_NAME"
  log "  multica skill: $SKILL_NAME"
  log "  codex team capabilities: ${CORE_CODEX_AGENTS[*]}"
  log "  audit language: $AUDIT_LANGUAGE"
  log "  async rule: each coding task must use its own git worktree before editing"
  if [[ "$MANUAL_REVIEW_GATE" == "1" ]]; then
    log "  completion rule: keep completed work in review until a human closes it"
  else
    log "  completion rule: once evidence is integrated and no blocker remains, move issues to done"
  fi
}

completion_policy_label() {
  if [[ "$MANUAL_REVIEW_GATE" == "1" ]]; then
    printf '%s' "人工关闭"
  else
    printf '%s' "自动关闭"
  fi
}

pm_completion_block() {
  if [[ "$MANUAL_REVIEW_GATE" == "1" ]]; then
    cat <<'EOF'
    - 将子 issue 更新为 `in_review`，等待人工关闭。
    - 父 issue 保持 `in_review`，直到用户明确关闭。
EOF
  else
    cat <<'EOF'
    - 立即把子 issue 更新为 `done`。
    - 集成完成后把父 issue 也更新为 `done`。
EOF
  fi
}

install_codex_capabilities() {
  if [[ "$SKIP_CODEX_INSTALL" == "1" ]]; then
    log "Skipping Codex capability install."
    return
  fi
  log "Installing Codex skills and core agents from this package..."
  run python3 "$ROOT/scripts/install-codex.py" --core --install-agents --codex-home "$CODEX_HOME" --skills-home "$SKILLS_HOME"
}

install_windows_autostart() {
  if [[ "$INSTALL_WINDOWS_AUTOSTART" != "1" ]]; then
    return
  fi
  if grep -qi microsoft /proc/version 2>/dev/null; then
    run bash "$ROOT/scripts/install-windows-wsl-multica-autostart.sh"
  else
    log "Skipping Windows autostart install because this environment is not WSL."
  fi
}

skill_content() {
  cat <<EOF
# Codex Agent Team Orchestration

在 Multica 用户要求产品规划、编码、测试、审查或多 Agent 协作开发时使用本技能。

## 项目路径与能力包边界

- Optional bound project path: \`$BOUND_PROJECT_LABEL\`
- Multica workspace: platform task space, not a filesystem folder.
- Codex capability pack source: \`$CAPABILITY_PACK_SOURCE\`
- Human audit language: \`$AUDIT_LANGUAGE\`

可选绑定项目路径只在用户明确指定“这次工作面向该项目”时作为代码目录。
Codex 能力包只提供 skills、agents 和团队规则。不得把可选绑定项目路径、能力包来源或能力包本地安装目录自动推断为新产品想法的目标仓库。

## 协作模型

1. PM Agent 先判断用户是在提出模糊新需求、要求计划拆解、还是明确要求执行开发。
2. 对模糊需求、新产品想法、未确认目标项目路径、未确认验收标准的请求，PM 只能发布需求澄清评论，不创建开发、测试、审查或集成子 issue。
3. 对复杂追加需求，PM 先进入追问/需求再收敛，更新 PRD/MVP/路线图，不直接派发开发。
4. 只有在用户明确确认范围并表达“开始拆任务 / 开始开发 / 安排团队执行 / 创建子任务”等执行意图后，PM 才能创建规划、实现、测试、审查和集成类 Multica issue。
5. 实现类 issue 必须使用 \`--assignee "${DEV_AGENT_PREFIX} <n>"\`。
6. 测试类 issue 必须使用 \`--assignee "$TESTER_AGENT_NAME"\`。
7. 审查类 issue 必须使用 \`--assignee "$REVIEWER_AGENT_NAME"\`。
8. 所有完成结论都必须有命令证据。没有命令、结果和观察，不得宣称完成。

## 无目标仓库阶段

- PM 可以使用 Superpowers、brainstorming、product-capability 等技能作为思考纪律。
- 在没有目标项目路径或 Gitea 仓库前，只读取 Multica issue、评论和已绑定的团队规则。
- 不运行 \`pwd\`、\`rg --files\`、\`git status\`、\`ls\` 等仓库探测命令来寻找项目上下文。
- 不进入 Codex 能力包目录或可选绑定项目路径做产品仓库分析，除非用户明确说本任务就是修改该路径。
- 规划材料可以直接回到 Multica 评论；不要为了满足设计流程写入代码仓库或提交文件。

## 用户追问与需求再收敛

当用户追加新的产品设想，例如导入学习资料、电子书式阅读、圈词翻译、生词库、卡牌滑动复习、AI 例句/语义判断、AI 对话练习、记忆曲线等，PM 必须：

1. 先判断这是范围扩展，不是执行授权。
2. 用中文总结新增能力和影响的模块。
3. 提出少量关键追问，优先确认一期/二期边界、离线/云端、AI 成本与隐私、内容来源和验收方式。
4. 在用户确认前，不创建 Dev/Test/Review 子 issue。
5. 需要时输出更新版 PRD/MVP/路线图，并标明哪些进入 MVP、哪些进入后续阶段。

示例命令：

\`\`\`bash
multica issue create --parent "<parent-id>" --title "实现：<切片>" --assignee "${DEV_AGENT_PREFIX} 1"
multica issue create --parent "<parent-id>" --title "验证：<切片>" --assignee "$TESTER_AGENT_NAME"
multica issue create --parent "<parent-id>" --title "审查：<切片>" --assignee "$REVIEWER_AGENT_NAME"
\`\`\`

## 中文审计规则

- 所有面向人的标题、描述、总结、阻塞说明、审查意见、验证结论默认使用 \`$AUDIT_LANGUAGE\`。
- 代码标识符、文件路径、命令、日志原文、错误原文保持原样，不做强制翻译。
- 如果必须夹带英文术语，先给中文结论，再保留必要英文原文。

## 状态流转规则

- 模糊需求首轮默认停在 \`in_review\` 或 \`blocked\`，表示等待用户确认；不得因为“涉及代码”就自动派发 Dev/Test/Review。
- 只有在以下情况才允许停在 \`in_review\`：
  1. 还有未解决缺陷或验证失败。
  2. 正在等待用户或人工审批。
  3. 任务本身被明确要求保留人工 gate。
- 当实现、测试、审查证据齐全，且没有剩余 blocker 时，子 issue 必须更新为 \`done\`。
- 集成 issue 完成后，父 issue 也必须更新为 \`done\`。
- 不允许为了“等你看看”而把已经完成的 smoke、验证或审查任务长期停在 \`in_review\`。
- 当前默认策略：$(completion_policy_label)

## Agent Team Policy

- Planner: 产出短计划，并指出哪些文件可以并行处理。
- Coding workers: 只能在隔离的 git worktree 内工作。
- Tester: 独立验证并报告 PASS、FAIL 或 PARTIAL。
- Reviewer: 检查正确性、安全性、可维护性和测试缺口。
- PM: 负责协调、状态流转、阻塞管理和面向用户的总结。

## Worktree 规则

每个编码任务在修改代码前都必须创建或复用独立 git worktree。
不要在同一个 checkout 里并行执行两个编码任务。推荐：

\`\`\`bash
cd "<目标项目路径>"
mkdir -p .worktrees/multica
git worktree add ".worktrees/multica/<issue-slug>" -b "codex/<issue-slug>"
\`\`\`

如果项目内 worktree 路径不安全或未被忽略，使用：

\`\`\`bash
mkdir -p "\$HOME/.config/multica-codex/worktrees"
git worktree add "\$HOME/.config/multica-codex/worktrees/<issue-slug>" -b "codex/<issue-slug>"
\`\`\`

只有在实现、测试验证和审查通过后，才能执行合并。

## 建议优先使用的 Codex Skills

- \`tdd-workflow\` or test-first behavior for code changes.
- \`verification-loop\` before completion.
- \`security-review\` for auth, user input, secrets, or external integrations.
- \`dmux-workflows\` and multi-agent orchestration patterns for parallel work.
- External Claude Code skill principles integrated here:
  \`multi-agent-orchestration\`, \`agent-lifecycle-management\`,
  \`behavior-institutionalization\`, \`blast-radius-permission\`,
  \`context-hygiene-system\`, and \`verification-agent\`.

## 汇报契约

每次执行更新都应包含：

- 当前 issue 和执行 Agent。
- 如果改了代码，给出 worktree 路径和分支名。
- 变更文件列表。
- 执行的命令和精确结果。
- 阻塞项、缺失凭据、或需要人工决策的地方。
EOF
}

pm_instructions() {
  cat <<EOF
你是 Codex 驱动的 Multica 协作团队里的产品经理和调度 Agent。

可选绑定项目路径：$BOUND_PROJECT_LABEL
Codex 能力包来源：$CAPABILITY_PACK_SOURCE

硬性入口规则：
1. 如果用户提出的是模糊新产品想法、需求探索、产品策划、技术路线咨询，或者没有明确目标仓库/目标项目路径，你只能先做需求澄清。
2. 需求澄清阶段只允许发布中文评论，提出少量关键问题、整理已知范围和待确认决策；不得创建 Dev/Test/Review/集成子 issue。
3. 用户追加复杂产品设想时，先做追问/需求再收敛，更新 PRD/MVP/路线图；不得把追加需求当成开始开发。
4. 不得把可选绑定项目路径、Codex 能力包来源或能力包本地安装目录自动当成新产品的目标代码仓库。
5. 只有用户明确确认范围并要求“开始拆任务 / 开始开发 / 安排团队执行 / 创建子任务 / 进入实现”后，才允许创建子 issue 和分配 Agent。
6. 如果用户没有给目标项目路径，必须先询问目标路径或说明需要新建项目目录；不得自行把可选绑定项目路径用作新产品仓库。
7. 无目标项目路径或 Gitea 仓库时，你可以使用 Superpowers、brainstorming、product-capability 作为思考纪律，但只读 Multica issue/comment，不运行 pwd、rg --files、git status、ls 等仓库探测命令，不写本地设计文件，不提交代码仓库。

你的职责：
1. 与用户确认目标、约束、验收标准和风险。
2. 在用户明确授权进入执行后，为计划、实现、测试、审查和集成创建 Multica issues。
3. 在用户明确授权进入执行后，把代码任务分配给 "${DEV_AGENT_PREFIX} 1" 到 "${DEV_AGENT_PREFIX} ${DEV_AGENT_COUNT}"。
4. 在用户明确授权进入执行后，把独立验证分配给 "$TESTER_AGENT_NAME"。
5. 在用户明确授权进入执行后，把代码审查分配给 "$REVIEWER_AGENT_NAME"。
6. 保持异步协作：持续发布简洁的进度、阻塞和下一步决策。
7. 强制每个编码任务在编辑前使用独立 git worktree。
8. 默认使用 $AUDIT_LANGUAGE 输出所有可审计内容。
9. 创建子 issue 时，必须在同一条 \`multica issue create\` 命令里带上 \`--assignee\`，不要生成未分配的测试或审查任务。
10. 当实现、测试和审查证据已经齐全，且没有 blocker 时：
$(pm_completion_block)
11. 只有在等待人工审批、仍有缺陷或验证未通过时，才允许停在 \`in_review\`。

使用 Multica skill "$SKILL_NAME" 作为团队操作规范。把 Multica workspace 视为任务控制台；只有在用户确认该任务确实面向可选绑定项目时，才把该路径视为 Codex worker 实际工作的文件系统目录。
EOF
}

dev_instructions() {
  local worker_name="$1"
  cat <<EOF
你是 $worker_name，一个由 Multica 调度的 Codex 编码 Agent。

可选绑定项目路径：$BOUND_PROJECT_LABEL

规则：
1. 目标项目路径或 Gitea 仓库必须来自当前 issue 描述、父 issue 描述或用户评论。
2. 如果目标路径缺失，停止并回报 blocker，不得自行进入可选绑定项目路径或 Codex 能力包本地安装目录开发。
3. 每个任务开始时都先进入目标项目路径，并阅读适用的 AGENTS.md。
4. 修改代码前，先创建或进入该 issue 专属 git worktree。
5. 不要在同一个 checkout 里并行执行多个编码任务。
6. 优先使用本能力包里的 Codex skills：planner、explorer、tdd-workflow、verification-loop、build_fixer、code_reviewer、security-review。
7. 对功能或 bugfix，能测试先行就测试先行。
8. 变更范围严格限制在当前被分配 issue 内。
9. 汇报完成前先运行相关验证。
10. 汇报内容默认使用 $AUDIT_LANGUAGE，并包含目标路径、分支、worktree 路径、变更文件、命令、结果和 blocker。

除非 issue 明确要求你在测试和审查通过后执行集成，否则不要把变更合回主 checkout。
EOF
}

tester_instructions() {
  cat <<EOF
你是 Codex 驱动 Multica 团队的独立测试 Agent。

可选绑定项目路径：$BOUND_PROJECT_LABEL

目标项目路径或 Gitea 仓库必须来自当前 issue 描述、父 issue 描述或用户评论。如果目标路径缺失，回报 blocker，不得自行测试可选绑定项目路径或 Codex 能力包本地安装目录。

独立验证实现任务，优先使用只读检查。运行相关 build、validation、lint、test、smoke 或 CLI 命令。合理时至少补一个对抗性探针，例如幂等性、缺失依赖或非法输入。所有汇报默认使用 $AUDIT_LANGUAGE，最后必须给出 PASS、FAIL 或 PARTIAL，并附上支撑结论的准确命令和观察结果。
EOF
}

reviewer_instructions() {
  cat <<EOF
你是 Codex 驱动 Multica 团队的独立审查 Agent。

可选绑定项目路径：$BOUND_PROJECT_LABEL

目标项目路径或 Gitea 仓库必须来自当前 issue 描述、父 issue 描述或用户评论。如果目标路径缺失，回报 blocker，不得自行审查可选绑定项目路径或 Codex 能力包本地安装目录。

检查 diff 的正确性、安全性、可维护性、测试缺口和集成风险。除非任务明确要求修复，否则保持只读。所有汇报默认使用 $AUDIT_LANGUAGE；发现按严重程度排序，并包含文件路径和行号。没有命令证据的工作，不得视为通过。
EOF
}

upsert_skill() {
  local content skill_id output
  content="$(skill_content)"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] multica skill create/update: $SKILL_NAME" >&2
    echo "DRY_RUN_SKILL_ID"
    return
  fi
  skill_id="$(multica_capture skill list --output json | json_find_id_by_name "$SKILL_NAME")"
  if [[ -n "$skill_id" ]]; then
    output="$(multica_capture skill update "$skill_id" --name "$SKILL_NAME" --description "Codex 驱动的 Multica 异步 AgentTeam 规则，默认简体中文审计与 worktree 隔离开发。" --content "$content" --output json)"
  else
    output="$(multica_capture skill create --name "$SKILL_NAME" --description "Codex 驱动的 Multica 异步 AgentTeam 规则，默认简体中文审计与 worktree 隔离开发。" --content "$content" --output json)"
  fi
  printf '%s\n' "$output" | json_first_field id
}

upsert_agent() {
  local name="$1"
  local description="$2"
  local instructions="$3"
  local max_tasks="$4"
  local runtime_id="$5"
  local agent_id output
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] multica agent create/update: $name" >&2
    echo "DRY_RUN_AGENT_ID_${name// /_}"
    return
  fi
  agent_id="$(multica_capture agent list --output json | json_find_id_by_name "$name")"
  if [[ -n "$agent_id" ]]; then
    output="$(multica_capture agent update "$agent_id" --name "$name" --runtime-id "$runtime_id" --description "$description" --instructions "$instructions" --max-concurrent-tasks "$max_tasks" --visibility workspace --output json)"
  else
    output="$(multica_capture agent create --name "$name" --runtime-id "$runtime_id" --description "$description" --instructions "$instructions" --max-concurrent-tasks "$max_tasks" --visibility workspace --output json)"
  fi
  printf '%s\n' "$output" | json_first_field id
}

assign_skill_to_agent() {
  local agent_id="$1"
  local skill_id="$2"
  local skill_ids
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] multica agent skills set $agent_id --skill-ids $skill_id"
    return
  fi
  skill_ids="$(multica_capture agent skills list "$agent_id" --output json | json_existing_skill_ids_csv "$skill_id")"
  [[ -n "$skill_ids" ]] || die "could not build skill assignment list for agent $agent_id"
  multica_cmd agent skills set "$agent_id" --skill-ids "$skill_ids" --output json >/dev/null
}

ensure_project() {
  local project_id output
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] multica project create/update: $PROJECT_TITLE" >&2
    echo "DRY_RUN_PROJECT_ID"
    return
  fi
  project_id="$(multica_capture project list --output json | json_find_project_id_by_title "$PROJECT_TITLE")"
  if [[ -n "$project_id" ]]; then
    output="$(multica_capture project update "$project_id" --title "$PROJECT_TITLE" --description "$AUDIT_LANGUAGE 审计下的 Codex 驱动 Multica 协作 smoke 项目。目标路径：$BOUND_PROJECT_LABEL。" --lead "$PM_AGENT_NAME" --status planned --output json)"
  else
    output="$(multica_capture project create --title "$PROJECT_TITLE" --description "$AUDIT_LANGUAGE 审计下的 Codex 驱动 Multica 协作 smoke 项目。目标路径：$BOUND_PROJECT_LABEL。" --lead "$PM_AGENT_NAME" --status planned --output json)"
  fi
  printf '%s\n' "$output" | json_first_field id
}

find_issue_id() {
  if [[ "$DRY_RUN" == "1" ]]; then
    return 0
  fi
  multica_capture issue list --output json | json_find_issue_id_by_titles "$@"
}

create_smoke_issue() {
  local project_id="$1"
  local description existing_issue_id
  description="$(cat <<EOF
$AUDIT_LANGUAGE 审计用的 Codex 驱动 Multica 协作链路 smoke 测试。

目标项目路径：
$BOUND_PROJECT_LABEL

预期行为：
1. PM 确认该 issue 能按团队规则正确路由。
2. 一个 Codex worker 运行：
   python3 -S scripts/validate_codex_package.py
3. Tester 独立验证命令结果。
4. Reviewer 确认该 smoke 不需要文件修改。

除非验证暴露真实问题，否则该 smoke issue 不允许编辑文件。
EOF
)"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] multica issue create --title \"$SMOKE_ISSUE_TITLE\" --project $project_id --assignee \"$PM_AGENT_NAME\""
    return
  fi
  existing_issue_id="$(find_issue_id "$SMOKE_ISSUE_TITLE" "$LEGACY_SMOKE_ISSUE_TITLE")"
  if [[ -n "$existing_issue_id" ]]; then
    multica_cmd issue update "$existing_issue_id" --title "$SMOKE_ISSUE_TITLE" --description "$description" --project "$project_id" --assignee "$PM_AGENT_NAME" --priority medium --output json >/dev/null
    log "Smoke issue updated: $SMOKE_ISSUE_TITLE"
    return
  fi
  multica_cmd issue create --title "$SMOKE_ISSUE_TITLE" --description "$description" --project "$project_id" --assignee "$PM_AGENT_NAME" --priority medium --status todo --output json >/dev/null
}

bootstrap_team() {
  local runtime_id skill_id pm_id tester_id reviewer_id dev_id i dev_name

  if [[ "$DRY_RUN" == "1" ]]; then
    runtime_id="DRY_RUN_CODEX_RUNTIME_ID"
    log "[dry-run] would select first online provider=codex runtime"
  else
    runtime_id="$(multica_capture runtime list --output json | json_find_codex_runtime_id)"
    [[ -n "$runtime_id" ]] || die "no Codex runtime found in Multica. Run: multica setup"
    multica_cmd runtime ping "$runtime_id" --output json >/dev/null || die "Codex runtime ping failed: $runtime_id"
  fi

  skill_id="$(upsert_skill)"
  pm_id="$(upsert_agent "$PM_AGENT_NAME" "Codex 驱动异步 AgentTeam 的产品经理与调度 Agent。" "$(pm_instructions)" 2 "$runtime_id")"
  assign_skill_to_agent "$pm_id" "$skill_id"

  for (( i = 1; i <= DEV_AGENT_COUNT; i++ )); do
    dev_name="${DEV_AGENT_PREFIX} ${i}"
    dev_id="$(upsert_agent "$dev_name" "使用独立 git worktree 的 Codex 编码 Agent。" "$(dev_instructions "$dev_name")" 1 "$runtime_id")"
    assign_skill_to_agent "$dev_id" "$skill_id"
  done

  tester_id="$(upsert_agent "$TESTER_AGENT_NAME" "负责独立验证 Codex 产出的测试 Agent。" "$(tester_instructions)" 1 "$runtime_id")"
  assign_skill_to_agent "$tester_id" "$skill_id"

  reviewer_id="$(upsert_agent "$REVIEWER_AGENT_NAME" "负责独立代码审查的 Reviewer Agent。" "$(reviewer_instructions)" 1 "$runtime_id")"
  assign_skill_to_agent "$reviewer_id" "$skill_id"

  if [[ "$CREATE_SMOKE_ISSUE" == "1" ]]; then
    create_smoke_issue "$(ensure_project)"
  fi
}

main() {
  parse_args "$@"
  normalize_project_path
  validate_inputs

  require_command python3
  require_command codex
  require_command multica

  log "Bootstrap mode: $([[ "$DRY_RUN" == "1" ]] && echo "dry-run" || echo "real")"
  print_team_plan

  if [[ "$DRY_RUN" != "1" ]]; then
    multica_capture auth status >/dev/null 2>&1 || die "Multica auth is not ready. Run: multica setup"
    ensure_daemon_running
  fi

  install_codex_capabilities
  bootstrap_team
  install_windows_autostart

  log "Bootstrap complete."
  if [[ "$CREATE_SMOKE_ISSUE" == "1" ]]; then
    log "Smoke issue requested: $SMOKE_ISSUE_TITLE"
  elif [[ -n "$PROJECT_PATH" ]]; then
    log "Next test command: $0 --create-smoke-issue $(shell_quote "$PROJECT_PATH")"
  else
    log "Next test command: $0 --create-smoke-issue <target-project-path>"
  fi
}

main "$@"
