# Everything Codex Code

这是把 `everything-claude-code` 转成 **Codex-first** 使用方式后的版本。重点不是把 Claude 文件原样塞给 Codex，而是按 Codex 的设计重新组织：

- 根目录 `AGENTS.md`：给 Codex 的仓库工作准则
- `.agents/skills`：仓库级核心 Codex Skills，可在本目录直接被 Codex 发现，共 34 个
- `skills/.curated`：建议安装到用户目录的核心 Codex Skills，共 34 个
- `skills/.experimental`：完整技能库的其余技能，共 150 个
- 每个 Skill 都只有 Codex 需要的 frontmatter：`name` 和 `description`
- 每个 Skill 都补了 `agents/openai.yaml`
- `.codex/config.toml`：Codex 的 sandbox、approval、MCP、features、多 agent role 配置
- `prompt-recipes`：把原来的 slash commands 改成 Codex 可直接粘贴/调用的 prompt recipe

## 推荐安装

```bash
git clone https://github.com/AegeanRagdolls/everything-codex.git
cd everything-codex
python3 -S scripts/validate_codex_package.py
./scripts/install-codex.sh --core
```

安装后重启 Codex。脚本会把 skills 安装到官方用户级目录 `$HOME/.agents/skills`，把配置放到 `~/.codex/config.toml` 或参考目录。

不要一上来安装全部 184 个技能；Codex skill 的 metadata 会进入可发现上下文，太多会变吵。需要完整库时再运行：

```bash
./scripts/install-codex.sh --all
```

## 使用方式

```text
Use the tdd-workflow skill to implement this feature with RED -> GREEN -> REFACTOR.
Use the security-review skill on my current git diff.
Use the verification-loop skill and run the repo checks before summarizing.
```

老的 `/code-review`、`/build-fix`、`/plan` 这类 Claude slash command 已转成 `prompt-recipes/*.md`，在 Codex 里直接说：

```text
Use the code-review prompt recipe on my current changes.
```

## Multica + Codex 使用入口

如果你要把这个仓库当成 **Multica 多 Agent 协作团队的 Codex 能力层**，直接从这两份文档开始：

- 完整中文使用手册：[docs/multica-codex-usage-manual.md](docs/multica-codex-usage-manual.md)
- Bootstrap 参数说明：[docs/multica-codex-team-bootstrap.md](docs/multica-codex-team-bootstrap.md)

当前推荐部署方式是：在 **WSL2 Ubuntu** 里运行 `multica` 和 `codex`，由 Windows 登录自动拉起 WSL 内的 `multica daemon`。

## 直接测试，不安装到全局

如果只是想确认 Codex 能不能看到仓库级技能：

```bash
cd everything-codex
codex
```

然后在 Codex 里输入：

```text
/skills
```

应该能看到 `.agents/skills` 下的核心技能。也可以直接测试：

```text
Use the verification-loop skill to inspect this package and run its validation script.
```

## 注意

`.codex/config.toml` 里的 MCP server 默认是 `enabled = false`，避免首次启动因为 Node、网络或 API key 不完整而失败。需要 GitHub、Context7、Playwright、Exa 等 MCP 时再手动开启。
