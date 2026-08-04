# 公司电脑 Codex 配置迁移指南

本指南把本机（zys31）的 Claude+Codex 配置体系迁到公司电脑 Windows。前提：公司电脑 Windows 11。

## 1. 装 Codex app
从 OpenAI 官网下载安装 Codex desktop app，登录。装完后 `~/.codex/` 自动生成（含 config.toml、runtime 目录、marketplaces）。

## 2. 装 cc-switch
cc-switch 是 GUI app（管 Claude/Codex 等 provider 切换 + skill 同步）。从 cc-switch 官方 release 装到公司电脑。
启动后在设置里确认：
- `skillStorageLocation: cc_switch`
- `skillSyncMethod: symlink`
- `preserveCodexOfficialAuthOnSwitch: true`
- `unifyCodexSessionHistory: true`

## 3. 导入 provider/auth + skill
cc-switch 没有 CLI、没有云同步。跨机迁移靠手动：

**provider/auth**：在公司电脑 cc-switch UI 重新配 provider（custom：base_url=http://127.0.0.1:15721/v1，token 由 cc-switch 代理注入）。auth（codex_oauth_auth.json）需公司电脑重新登录 Codex--token 绑定机器，不能直接拷。

**skill**：从本机整目录拷贝 `~/.cc-switch/skills/` 到公司电脑 `~/.cc-switch/skills/`。含全部 skill 真身（自研的 leader/code-change-workflow/cc-switch-setting-sync/expose-unknowns/guide-skill-auditor 等 + 外部拉的 ponytail/understand 等）。拷完 cc-switch 会 symlink 同步到 `~/.codex/skills/` 和 `~/.claude/skills/`。

> 自研 skill 靠这一步迁移，不在 git 仓库里（仓库已 untrack skills/）。建议定期备份 `~/.cc-switch/skills/`。

## 4. 合并 config 模板
```powershell
# 公司电脑，仓库 clone 后
cd <仓库路径>\codex
.\setup.ps1 -CodexHome "$env:USERPROFILE\.codex"
```
setup.ps1 把 config.template.toml 占位回填，合并到 `~/.codex/config.toml`（不覆盖已有 marketplaces/notify/runtime 字段）。

占位回填规则：
- `{{USERNAME}}` -> `$env:USERNAME`
- `{{CODEX_HOME}}` -> `$env:USERPROFILE\.codex`
- `{{PROXY_BASE_URL}}` -> `http://127.0.0.1:15721/v1`（cc-switch 代理，端口不同则改）
- `{{OPENAI_BASE_URL}}` -> `http://127.0.0.1:4444/v1`
- `{{PIPX_VENV_PYTHON}}` -> pipx 装的 douyin-mcp-server python 路径
- `{{CODE_SPEC_PLUGIN_PATH}}` -> Code-Spec-Plugin/src/cli.ts 路径（公司电脑没此项目则删此 MCP 段）

## 5. 复制 instructions.md
```powershell
Copy-Item .\codex\instructions.md "$env:USERPROFILE\.codex\instructions.md" -Force
```
这是 Codex 全局指令（对应 Claude Code 的 CLAUDE.md）。

## 6. 装 MCP servers
- playwright：`npx @playwright/mcp@latest`（首次自动装）
- context7：`npx -y @upstash/context7-mcp`
- douyin：`pipx install douyin-mcp-server`
- github-mcp：设环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN`
- code-spec-plugin：需先 clone Code-Spec-Plugin 项目（不需要则删）
- cloudcli-browser：含 token，公司电脑重新获取（模板未含）

## 7. 已知限制
- **Mac 路径另写**：本模板假设 Windows。Mac 的 Codex runtime 路径结构不同（cua_node/sky），需另写一套模板。
- **自研 skill 迁移靠手动拷贝** `~/.cc-switch/skills/`，不在 git 仓库。定期备份此目录。
- **runtime hash 路径**：cua_node 的 hash（如 fb8898c05a62885e）每次 Codex app 安装不同，不进模板，由 app 自动生成。
- **auth token 绑定机器**：codex_oauth_auth.json 不能跨机拷贝，公司电脑重新登录。
- **cc-switch.db**：provider 配置存 SQLite，跨机靠 UI 重配，不直接拷 db（含本机 token）。
