# Multica + Codex AgentTeam Bootstrap

这个工程提供一键脚本，把当前 Everything Codex Code 能力包接入 Multica，并创建一个 Codex-backed 异步 AgentTeam。

默认行为有两点：

- 所有可审计的人类可读内容默认使用简体中文。
- 模糊新产品需求先进入需求澄清；在用户明确确认范围和执行意图前，不创建 Dev/Test/Review/集成子 issue。
- `everything-codex-code` 是 Codex 能力包来源，不会被自动当成用户新产品的目标代码仓库。
- 能力包默认来源记录为 `https://github.com/AegeanRagdolls/everything-codex`；本地 clone 到哪里不写入 Multica 作为业务项目路径。
- 没有目标项目路径或 Gitea 仓库时，PM 只读取 Multica issue/comment，不做本地仓库探测。
- 用户追加复杂产品设想时，PM 先追问并更新 PRD/MVP/路线图，不把追问当作开发授权。
- 当实现、测试、审查证据齐全且没有 blocker 时，issue 自动推进到 `done`，不会长期停在 `in_review`。
- 在 WSL 环境下可以额外安装 Windows 登录任务，自动拉起 Ubuntu 里的 Multica daemon。

## 一键部署

```bash
git clone https://github.com/AegeanRagdolls/everything-codex.git
cd everything-codex

scripts/bootstrap-multica-codex-team.sh \
  --skip-codex-install
```

上面这条命令只创建或更新 Multica AgentTeam 和 orchestration skill，不绑定任何业务项目路径。等用户明确要对某个项目开发时，再在 issue 里给出目标项目路径或 Gitea 仓库。

新电脑上先确保 `codex`、`multica`、`python3` 可用，并运行过：

```bash
multica setup
```

如果你的 Multica daemon 跑在 WSL Ubuntu 里，并且希望 Windows 登录后自动拉起它：

```bash
scripts/install-windows-wsl-multica-autostart.sh --run-now
```

这个安装器会优先尝试 Windows 计划任务；如果当前会话没有注册计划任务的权限，就自动退回到当前用户的 Windows Startup 文件夹。

安全预览：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --dry-run \
  --skip-codex-install
```

如果要在 bootstrap 时顺手安装 Windows 登录自启动：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --install-windows-autostart \
  --create-smoke-issue \
  /path/to/project
```

## 创建的 Multica 对象

默认创建或更新：

- `产品经理 / 项目调度`：产品经理和调度 Agent。
- `ECC Dev 1`、`ECC Dev 2`：并行编码 worker。
- `ECC Tester`：独立验证 Agent。
- `ECC Reviewer`：独立代码审查 Agent。
- `Codex Agent Team Orchestration`：Multica skill，写入团队协作规则。
- `Everything Codex Code Agent Team`：smoke project。
- `验证 Multica Codex 智能协作团队`：smoke issue。

所有默认 Agent 都绑定当前 workspace 里的在线 Codex runtime。

## 工作模型

Multica workspace 是平台任务空间，不是本地文件夹。脚本只在你显式传入 `project-path` 时，把它作为“可选绑定项目路径”写入 Agent instructions；Codex worker 只有在用户确认任务确实面向该项目时才进入该路径工作。对“我想做一个 App”这类模糊需求，PM 应先回到用户沟通和需求冻结，不应因为能力包路径存在就启动团队并行执行。只要 issue 里没有目标项目路径或 Gitea 仓库，PM 不应运行 `pwd`、`rg --files`、`git status`、`ls` 等仓库探测命令。

如果 bootstrap 时不传 `project-path`，Agent instructions 会显示“可选绑定项目路径：未绑定”。这适合把能力包部署成可移植团队规则，让每个真实开发任务在 Multica issue 里显式声明目标项目。

编码任务必须异步且隔离：

```text
用户 -> 产品经理 / 项目调度 -> Multica issues -> ECC Dev/Test/Review agents -> Codex runtime -> git worktree
```

编码 worker 必须在独立 git worktree 中修改代码。Tester 和 Reviewer 独立验证后，PM 负责汇总并推进合并或收口状态。默认情况下，证据齐全的子任务会被关闭到 `done`；只有等待人工审批或存在未解决问题时才停在 `in_review`。

## Claude Code Skill 融入方式

`C:/Users/oream/Downloads/CLAUDE CODE SKILL` 中的 12 个 skill 没有被原样全量安装进 daily Codex surface。脚本把其中和当前目标强相关的原则写入 Multica orchestration skill：

- `multi-agent-orchestration`
- `agent-lifecycle-management`
- `behavior-institutionalization`
- `blast-radius-permission`
- `context-hygiene-system`
- `verification-agent`

其余如 MCP、hook、prompt cache、tool runtime 等主题更适合作为后续库化材料，不默认加载，避免 AgentTeam 初始上下文过重。

## 常用参数

```bash
scripts/bootstrap-multica-codex-team.sh \
  --pm-agent-name "PM" \
  --dev-agent-prefix "Dev" \
  --dev-agent-count 3 \
  --tester-agent-name "QA" \
  --reviewer-agent-name "Review" \
  --audit-language "简体中文" \
  --capability-pack-source "https://github.com/AegeanRagdolls/everything-codex" \
  --create-smoke-issue \
  /path/to/project
```

指定 workspace：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --workspace-id <workspace-id> \
  --create-smoke-issue \
  /path/to/project
```

如果你确实希望把完成任务留在 Review 列，显式打开人工门禁：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --manual-review-gate \
  --create-smoke-issue \
  /path/to/project
```

## 验证

```bash
bash -n scripts/bootstrap-multica-codex-team.sh
python3 -S scripts/test-multica-codex-bootstrap.py
python3 -S scripts/validate_codex_package.py
```
