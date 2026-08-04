# Codex 迁移执行指南（给公司电脑 Codex agent）

> 本文件给公司电脑上的 Codex agent 读了执行，把本机（zys31）的 Claude+Codex 配置体系迁过来。人读速查概览见 `SETUP.md`。
> 执行者：一字不差按步骤跑，前置检查不通过先补齐再继续，验证清单全过才算完成。

## 前置检查（不满足先装，别往下跑）
- Windows 11（本模板 Windows 专用；Mac 见末尾已知限制）
- PowerShell 5.1+：`$PSVersionTable.PSVersion`
- git：`git --version`
- GitHub CLI gh：`gh --version`（clone 私有仓库用）；未登录跑 `gh auth login` 选 GitHub.com -> HTTPS -> 浏览器认证
- Node.js 20+：`node --version`（playwright/context7 等 MCP 用 npx）
- Python 3.12：`python --version`（douyin MCP 用）
- pipx：`pipx --version`（装 douyin-mcp-server 用）；没有则用 pip 装 pipx

## 1. clone 仓库（私有，需 gh 认证）
```powershell
gh repo clone zys3198/claude-stack "$env:USERPROFILE\claude-stack"
cd "$env:USERPROFILE\claude-stack\codex"
```
若 gh 未认证：`gh auth login` 走浏览器流程，账号要能访问 zys3198/claude-stack。

## 2. 装 Codex app
从 OpenAI 官网下载 Codex desktop app，登录。装完 `~/.codex/`（即 `$env:USERPROFILE\.codex\`）自动生成，含 config.toml、runtime 目录、marketplaces。

## 3. 装 cc-switch
从 cc-switch 官方 release 装 GUI app（管 Claude/Codex 等 provider 切换 + skill 同步）。启动后在设置里确认：
- `skillStorageLocation: cc_switch`
- `skillSyncMethod: symlink`
- `preserveCodexOfficialAuthOnSwitch: true`
- `unifyCodexSessionHistory: true`

## 4. 导入 skill（手动拷贝，cc-switch 无云同步）
从本机整目录拷贝 `~/.cc-switch/skills/` 到公司电脑 `~/.cc-switch/skills/`，含全部 skill 真身（自研的 leader/code-change-workflow/cc-switch-setting-sync/expose-unknowns/guide-skill-auditor 等 + 外部拉的 ponytail/understand 等）。
- 传输方式：压缩成 zip 走 U盘/网盘，或 `tar -czf skills.tar.gz -C ~/.cc-switch skills` 传过去解压
- 拷完 cc-switch 会 symlink 同步到 `~/.codex/skills/` 和 `~/.claude/skills/`
- **Windows symlink 常失败**：若 cc-switch symlink 同步不出，改用 junction 或直接 copy（见故障排查）
- 验证：`Test-Path "$env:USERPROFILE\.cc-switch\skills\leader\SKILL.md"` 应为 True

## 5. 配 provider/auth（cc-switch UI，不能拷）
公司电脑 cc-switch UI 配 provider：custom，base_url=`http://127.0.0.1:15721/v1`，token 由 cc-switch 代理注入（别手填真值）。
Codex auth（codex_oauth_auth.json）需公司电脑重新登录 Codex--token 绑定机器，不能跨机拷贝。

## 6. 合并 config 模板
```powershell
cd "$env:USERPROFILE\claude-stack\codex"
.\setup.ps1 -CodexHome "$env:USERPROFILE\.codex"
```
setup.ps1 把 config.template.toml 的 `{{...}}` 变量回填，合并到 `~/.codex/config.toml`，不覆盖 marketplaces/notify/runtime/hooks.state/projects 字段。
- 合并后**手动去重**：打开 `~/.codex/config.toml`，保留 app 自动生成的 marketplaces/notify/runtime/hooks.state/projects 段，删迁移进来的重复段
- 变量回填值见 `SETUP.md` 的变量回填规则表；端口或路径不同则改 setup.ps1 里的 replacement

## 7. 复制 instructions.md（Codex 全局指令）
```powershell
Copy-Item "$env:USERPROFILE\claude-stack\codex\instructions.md" "$env:USERPROFILE\.codex\instructions.md" -Force
```
这是 Codex 的全局指令（对应 Claude Code 的 CLAUDE.md），含 lean-ctx 规则 + 适配后的代码改动/证据门槛/交互纪律等。

## 8. 装 MCP servers
- playwright：`npx @playwright/mcp@latest`（Codex 首次调用自动装）
- context7：`npx -y @upstash/context7-mcp`
- douyin：用 pipx 装 douyin-mcp-server（命令见 SETUP.md）
- github-mcp：`setx GITHUB_PERSONAL_ACCESS_TOKEN "<你的token>"`（设环境变量后重启 Codex）
- code-spec-plugin：需先 clone Code-Spec-Plugin 项目到 `C:\ZYS\Code\Code-Spec-Plugin`；公司电脑没此项目则从 config.toml 删此 MCP 段
- cloudcli-browser：含真实 token，模板未含；公司电脑需要时重新获取 token 手动加

## 验证清单（全部通过才算迁移成功，逐项跑命令确认）
- [ ] `Test-Path "$env:USERPROFILE\.codex\config.toml"` 为 True，且 `Select-String -Path "$env:USERPROFILE\.codex\config.toml" -Pattern 'kimi-k3','danger-full-access'` 命中
- [ ] `Test-Path "$env:USERPROFILE\.codex\instructions.md"` 为 True，且含 "lean-ctx" 和 "证据门槛"
- [ ] `Test-Path "$env:USERPROFILE\.codex\skills\leader\SKILL.md"` 为 True（cc-switch symlink 同步成功）
- [ ] `Test-Path "$env:USERPROFILE\.cc-switch\skills\leader\SKILL.md"` 为 True（skill 真身在）
- [ ] Codex 启动能正常对话（provider/auth 配通，cc-switch 代理 127.0.0.1:15721 在跑）
- [ ] MCP servers 在 Codex 里可用：试调 playwright/context7
- [ ] hooks 生效：ponytail 等 plugin 的 session_start/user_prompt_submit hook 触发（Codex 设置里 hooks=true）

## 故障排查
- **cc-switch symlink 没同步 skill 到 ~/.codex/skills/**：检查 skillStorageLocation=cc_switch、skillSyncMethod=symlink；Windows symlink 常失败，改用 junction：`New-Item -ItemType Junction -Path "$env:USERPROFILE\.codex\skills" -Target "$env:USERPROFILE\.cc-switch\skills"`；或直接 `Copy-Item -Recurse`
- **config.toml 合并后 Codex 启动报 TOML 语法错**：重复段没去重干净。备份后用 app 生成的那份 marketplaces/notify/runtime/hooks.state/projects，只保留迁移进来的 model/provider/features/memories/plugins/mcp_servers/windows/desktop/env 段
- **MCP server 启动失败**：检查 npx/pipx 在 PATH；Node 20+、Python 3.12；douyin 的 python 路径对（setup.ps1 回填的 `{{PIPX_VENV_PYTHON}}`）
- **provider 连不上（Codex 对话报错）**：cc-switch 代理没运行（检查 127.0.0.1:15721）；或 auth 没登录（Codex app 重新登录）
- **runtime hash 路径不对（node_repl 等）**：这些是 Codex app 安装时自动生成的，别手填。删 config.toml 里手动加的 runtime 段，重启 Codex app 让它重建
- **gh clone 失败**：`gh auth status` 确认认证；账号要有 zys3198/claude-stack 访问权

## 已知限制
- **Mac 路径另写**：本模板 Windows 专用。Mac 的 Codex runtime 路径结构不同（cua_node/sky），需另写一套 config 模板和 setup 脚本。
- **自研 skill 迁移靠手动拷贝** `~/.cc-switch/skills/`，不在 git 仓库（仓库已 untrack skills/，全权交 cc-switch）。建议定期备份此目录。
- **auth token 绑定机器**：codex_oauth_auth.json 不能跨机拷贝，公司电脑重新登录。
- **cc-switch.db 不跨机拷**（含本机 token）：provider 配置跨机靠 cc-switch UI 重配。
- **三个 marketplace 是 gitlink/ignored**：`i-have-adhd`、`minimalist-entrepreneur`（历史 gitlink，clone 后空目录）、`better-harness`（本次 ignore）。公司电脑需要时单独 git clone 到 `~/.claude/plugins/marketplaces/` 下。
- **runtime hash 路径**：cua_node 的 hash（如 fb8898c05a62885e）每次 Codex app 安装不同，不进模板，由 app 自动生成。
