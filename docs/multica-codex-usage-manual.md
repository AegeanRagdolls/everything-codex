# Multica + Codex 使用手册

这份手册面向两类场景：

- 你要把 **Multica** 当成多 Agent 协作面板，把 **Codex** 当成执行引擎。
- 你要把这套环境做成可复制的，一台新电脑也能按脚本重新部署。

如果你只想看脚本参数，读 [docs/multica-codex-team-bootstrap.md](/mnt/c/Users/oream/Desktop/everything-codex-code/docs/multica-codex-team-bootstrap.md)。如果你想知道这套东西到底怎么工作、怎么排障、怎么日常使用，读这份手册。

## 这套架构到底是什么

先把四个概念分开：

- `Multica workspace`：任务面板和协作空间，不是本地文件夹。
- `本地项目目录`：Codex 实际读写代码的路径。
- `Codex runtime`：真正执行 Agent 任务的本地 CLI 运行时。
- `everything-codex-code`：给 Codex 提供 skills、agents、prompt recipes 和项目规则的能力包。

注意：`everything-codex-code` 是能力包，不是所有新需求的默认业务代码仓库。用户提出模糊新产品想法时，PM 应先澄清目标用户、平台、范围、验收标准和目标项目路径；在用户明确确认进入执行前，不应创建 Dev/Test/Review 子任务。

实际工作流是：

```text
你在 Multica 里提需求
-> ECC PM 负责澄清、拆任务、分配
-> ECC Dev / Tester / Reviewer 各自执行
-> Codex runtime 在本地项目目录里运行
-> 结果回写到 Multica issue
```

所以，`Multica` 不是直接“打开一个本地文件夹开始改代码”。它管理任务和 Agent。真正进入本地目录工作的，是被 Multica 调起的 `Codex runtime`。

## 当前推荐部署方式

当前这套配置的推荐形态是：

- `multica` 安装在 **Ubuntu on WSL2**
- `codex` 安装在 **Ubuntu on WSL2**
- Windows 登录后，自动拉起 WSL 里的 `multica daemon`

这样做的原因很直接：

- 本地 shell、Python、Git、脚本路径都更稳定
- 跟当前仓库的脚本和验证命令匹配
- Windows 只负责登录触发，真正执行还是在 Ubuntu 里完成

## 第一次部署

先确保下面这几个命令在 WSL Ubuntu 里可用：

```bash
python3 --version
git --version
codex --version
multica version
```

然后在 WSL 里执行：

```bash
cd /path/to/everything-codex-code
multica setup
python3 -S scripts/validate_codex_package.py
```

如果你要把 **当前仓库本身** 当成 Multica 的 smoke 项目，可以直接运行：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --install-windows-autostart \
  --create-smoke-issue \
  /path/to/everything-codex-code
```

如果你要把 **另一个现有项目** 接入 Multica，就把最后那个路径换成目标项目路径。

## 一键脚本会做什么

[scripts/bootstrap-multica-codex-team.sh](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/bootstrap-multica-codex-team.sh) 默认会做这些事：

1. 校验本地 `multica` / `codex` / `python3` 是否存在
2. 检查 Multica 登录状态
3. 检查本地 daemon 是否真的在 `running`
4. 安装当前仓库的 Codex skills 和 core agents
5. 在 Multica 中创建或更新以下对象：
   - `ECC PM`
   - `ECC Dev 1`
   - `ECC Dev 2`
   - `ECC Tester`
   - `ECC Reviewer`
   - `Codex Agent Team Orchestration`
6. 把目标项目路径写进这些 Agent 的 instructions
7. 可选创建一个 smoke project 和 smoke issue
8. 可选安装 Windows 登录自启动

## 默认团队规则

当前脚本已经把下面这些行为固化进 Agent instructions 和 Multica skill：

- 所有可审计的人类可读内容默认使用简体中文
- 模糊新产品需求先停在需求澄清阶段，不自动创建开发、测试、审查或集成子任务
- 只有用户明确确认范围并要求开始拆任务或开始开发后，PM 才能分配 Dev / Tester / Reviewer
- `everything-codex-code` 只作为 Codex 能力包，不能被自动推断为目标产品仓库
- 编码任务必须在独立 `git worktree` 中执行
- PM 负责拆任务、分配任务、汇总证据
- Tester 独立验证
- Reviewer 独立审查
- 当实现、测试、审查证据齐全且没有 blocker 时，任务默认自动推进到 `done`
- 只有等待人工审批、验证失败或存在未解决问题时，任务才停在 `in_review`

如果你确实想保留人工门禁，可以在 bootstrap 时显式开启：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --manual-review-gate \
  /path/to/project
```

## Windows 登录自启动

如果你的 `multica daemon` 跑在 WSL Ubuntu 里，推荐安装登录自启动：

```bash
scripts/install-windows-wsl-multica-autostart.sh --run-now
```

这个安装器会优先尝试 Windows Task Scheduler。如果当前会话没有注册计划任务的权限，就自动退回到当前用户的 Windows Startup 文件夹。

当前实际落地的是：

- 启动脚本：[scripts/start-multica-daemon-wsl.ps1](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/start-multica-daemon-wsl.ps1)
- WSL 内自检脚本：[scripts/ensure-multica-daemon.sh](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/ensure-multica-daemon.sh)
- Windows Startup launcher：`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MulticaDaemonWSL.cmd`

这意味着你下次重启电脑并登录 Windows 后，Ubuntu 里的 daemon 会被自动拉起。

## 日常使用方式

最直接的方式是在 Multica 面板里和 `ECC PM` 沟通。

例如：

```text
请给当前项目增加一个自定义 Agent 模板导出功能。
要求：
1. 默认使用中文汇报
2. 编码和测试分开执行
3. 最后给我一个可审计的变更总结
```

正常情况下，`ECC PM` 会：

1. 先澄清需求和验收标准
2. 创建父 issue
3. 拆出规划、实现、测试、审查、集成等子 issue
4. 把代码任务分配给 `ECC Dev`
5. 把验证任务分配给 `ECC Tester`
6. 把审查任务分配给 `ECC Reviewer`
7. 最后汇总证据并收口状态

## 状态怎么看

推荐你这样理解状态：

- `todo`：任务已经存在，但还没被 runtime 接单
- `in_progress`：任务已经开始跑
- `in_review`：有明确人工 gate，或者还有问题待确认
- `done`：证据齐全且已经收口
- `blocked`：缺权限、缺依赖、缺凭据、缺人类决策

如果你看到一张卡长时间停在 `todo`，先不要怀疑 PM 逻辑，先查本地 runtime。

## 最常见的排障命令

### 1. 看 daemon 是不是真的在跑

```bash
multica daemon status --output json
```

关键看：

- `status` 是否为 `running`
- `agents` 里是否有 `codex`

### 2. 看 Codex runtime 是否在线

```bash
multica runtime list --output json
```

关键看 `provider = codex` 的那条记录，`status` 是否为 `online`。

### 3. 看 Agent 有没有接到任务

先列出 Agent：

```bash
multica agent list --output json
```

再查看某个 Agent 的任务：

```bash
multica agent tasks <agent-id> --output json
```

如果某个 issue 明明分配给 Agent，但你怀疑它没跑，这个命令比看面板更直接。

### 4. 看 issue 有没有 execution history

```bash
multica issue runs <issue-id> --output json
```

如果这里已经有 `running` 或 `completed` 的 run，而看板状态还没刷新，优先相信 run history。

## 一个重要的现实细节

`multica daemon status` 在 daemon 停止时，CLI 仍然可能返回成功退出码，只是内容里显示 `Daemon: stopped`。所以不能只靠 shell 退出码判断 daemon 正常与否。

当前仓库里的 bootstrap 脚本已经处理了这个问题，会真正解析 daemon 状态文本和 JSON。

## Smoke 测试怎么做

如果你只想验证整条链路能不能跑通：

```bash
scripts/bootstrap-multica-codex-team.sh \
  --create-smoke-issue \
  /path/to/project
```

然后在 Multica 面板里观察 smoke 父任务是否从：

```text
todo -> in_progress -> done
```

并且子任务会拆成类似：

- 计划与验收确认
- 执行 validate 命令
- 独立验证命令结果
- 独立审查无需改文件
- 集成与收口

## 换电脑怎么复现

新电脑上按这个顺序做：

1. 安装 WSL2 Ubuntu
2. 在 Ubuntu 里安装 `git`、`python3`、`codex`、`multica`
3. 克隆本仓库
4. 运行：

```bash
cd /path/to/everything-codex-code
multica setup
scripts/install-windows-wsl-multica-autostart.sh --run-now
scripts/bootstrap-multica-codex-team.sh \
  --install-windows-autostart \
  --create-smoke-issue \
  /path/to/project
```

5. 验证：

```bash
multica daemon status --output json
multica runtime list --output json
python3 -S scripts/test-multica-codex-bootstrap.py
```

## 这个仓库里最相关的文件

- [AGENTS.md](/mnt/c/Users/oream/Desktop/everything-codex-code/AGENTS.md)：仓库级工作规则
- [README.md](/mnt/c/Users/oream/Desktop/everything-codex-code/README.md)：项目总览
- [README.zh-CN.md](/mnt/c/Users/oream/Desktop/everything-codex-code/README.zh-CN.md)：中文总览
- [docs/multica-codex-team-bootstrap.md](/mnt/c/Users/oream/Desktop/everything-codex-code/docs/multica-codex-team-bootstrap.md)：bootstrap 参数和对象说明
- [scripts/bootstrap-multica-codex-team.sh](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/bootstrap-multica-codex-team.sh)：一键接入脚本
- [scripts/ensure-multica-daemon.sh](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/ensure-multica-daemon.sh)：daemon 自检启动脚本
- [scripts/install-windows-wsl-multica-autostart.sh](/mnt/c/Users/oream/Desktop/everything-codex-code/scripts/install-windows-wsl-multica-autostart.sh)：Windows 登录自启动安装器

## 推荐的最短路径

如果你只记一组命令，记这组：

```bash
cd /path/to/everything-codex-code
multica setup
scripts/install-windows-wsl-multica-autostart.sh --run-now
scripts/bootstrap-multica-codex-team.sh \
  --install-windows-autostart \
  --create-smoke-issue \
  /path/to/project
```

然后去 Multica 里找 `ECC PM` 说需求。
