# Codex 迁移执行指南（给公司电脑 Codex agent）

> 本文件给公司电脑上的 Codex agent 读了执行，把本机（zys31）的 Codex 配置迁过来。公司电脑不用 cc-switch，配置直接放 ~/.codex/ 目录。人读速查见 SETUP.md。
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

## 2. 装 Codex app（已装跳过）
从 OpenAI 官网下载 Codex desktop app。登录--provider/auth/model 由 Codex app 登录配置，不走 cc-switch。装完 `~/.codex/`（即 `$env:USERPROFILE\.codex\`）自动生成。

## 3. 放 instructions.md（Codex 全局指令）
```powershell
Copy-Item "$env:USERPROFILE\claude-stack\codex\instructions.md" "$env:USERPROFILE\.codex\instructions.md" -Force
```
这是 Codex 的全局指令（对应 Claude Code 的 CLAUDE.md），含 lean-ctx 规则 + 适配后的代码改动/证据门槛/交互纪律等。

## 4. 放 skills（只迁开发相关，非开发不迁）
公司电脑 Codex 只需开发相关 skill，与开发无关的（营销/设计/内容/Office/动画/图片等）不用迁。
- 从本机 `~/.cc-switch/skills/` 挑开发相关 skill，打包传到公司电脑，解压到 `~/.codex/skills/`（真身 copy，不用 symlink）
- **推荐迁**：ai-coding-guide、code-change-workflow、code-review、code-review-and-quality、debugging-and-error-recovery、diagnosing-bugs、tdd、test-driven-development、implement、git-workflow-and-versioning、git-guardrails-claude-code、caveman、caveman-commit、caveman-review、api-and-interface-design、domain-modeling、codebase-design、code-simplification、simplify、spec-driven-development、source-driven-development、expose-unknowns、logic-triple-check、full-output-enforcement、ruthless-review、grill-me、neat-freak、lean-ctx、context-engineering、codemap、understand、understand-diff、understand-domain、learning-guide、tech-learning-roadmap、teach、leader、planning-and-task-breakdown、handoff、to-prd、to-spec、triage、frontend-guide、shadcn-vue-guide、cc-switch-setting-sync、skill-creator、guide-skill-auditor、security-and-hardening、performance-optimization、ci-cd-and-automation、documentation-and-adrs
- **不迁**：marketing-*、article-*、bili-note、douyin-*、ppt-master、pptx、docx、xlsx、pdf、brand-*、design-*、animation-*、image-*、canvas-design、apple-design、interview-*、founder-*、grow-sustainably、organizational-refresh、content-to-note 等
- 本机 `~/.codex/skills/` 也有 drawio-chart 等 Codex skill，可一并拷
- 验证：`Test-Path "$env:USERPROFILE\.codex\skills\ai-coding-guide\SKILL.md"` 应为 True

## 5. 合并 config 自定义片段（非 provider）
公司电脑 config.toml 的 provider/model/auth 由 Codex app 登录自配，本模板只合并非 provider 片段（plugins/mcp/features/memories/windows/desktop）。
```powershell
cd "$env:USERPROFILE\claude-stack\codex"
.\setup.ps1 -CodexHome "$env:USERPROFILE\.codex"
```
setup.ps1 把 config.template.toml 的 `{{...}}` 变量回填，合并到 `~/.codex/config.toml`，不覆盖 provider/model/auth。
- 合并后**手动去重**：保留 app 生成的 provider/model/auth/marketplaces/notify/runtime/hooks.state/projects 段，删迁移进来的重复段
- 变量回填值见 setup.ps1；路径不同则改 setup.ps1 里的 replacement

## 6. 装 MCP servers
- playwright：`npx @playwright/mcp@latest`（Codex 首次调用自动装）
- context7：`npx -y @upstash/context7-mcp`
- douyin：用 pipx 装 douyin-mcp-server（命令见 setup.ps1 注释）
- github-mcp：`setx GITHUB_PERSONAL_ACCESS_TOKEN "<你的token>"`（设环境变量后重启 Codex）
- code-spec-plugin：需先 clone Code-Spec-Plugin 项目到 `C:\ZYS\Code\Code-Spec-Plugin`；公司电脑没此项目则从 config.toml 删此 MCP 段
- cloudcli-browser：含真实 token，模板未含；公司电脑需要时重新获取 token 手动加

## 验证清单（全部通过才算迁移成功，逐项跑命令确认）
- [ ] `Test-Path "$env:USERPROFILE\.codex\config.toml"` 为 True，且 `Select-String -Path "$env:USERPROFILE\.codex\config.toml" -Pattern 'danger-full-access','pragmatic'` 命中（非 provider 片段已合并）
- [ ] `Test-Path "$env:USERPROFILE\.codex\instructions.md"` 为 True，且含 "lean-ctx" 和 "证据门槛"
- [ ] `Test-Path "$env:USERPROFILE\.codex\skills\ai-coding-guide\SKILL.md"` 为 True（开发 skill 已放）
- [ ] Codex 启动能正常对话（provider/auth 由 Codex app 登录配通）
- [ ] MCP servers 在 Codex 里可用：试调 playwright/context7
- [ ] hooks 生效：ponytail 等 plugin 的 session_start/user_prompt_submit hook 触发（Codex 设置里 hooks=true）

## 故障排查
- **config.toml 合并后 Codex 启动报 TOML 语法错**：重复段没去重干净。备份后用 app 生成的那份 provider/model/auth/marketplaces/notify/runtime/hooks.state/projects，只保留迁移进来的 features/memories/plugins/mcp_servers/windows/desktop 段
- **MCP server 启动失败**：检查 npx/pipx 在 PATH；Node 20+、Python 3.12；douyin 的 python 路径对（setup.ps1 回填的 `{{PIPX_VENV_PYTHON}}`）
- **provider 连不上（Codex 对话报错）**：Codex app 重新登录；或检查 config.toml 的 provider/model 配置（公司电脑自配，不走 cc-switch 代理）
- **runtime hash 路径不对（node_repl 等）**：这些是 Codex app 安装时自动生成的，别手填。删 config.toml 里手动加的 runtime 段，重启 Codex app 让它重建
- **gh clone 失败**：`gh auth status` 确认认证；账号要有 zys3198/claude-stack 访问权

## 已知限制
- **Mac 路径另写**：本模板 Windows 专用。Mac 的 Codex runtime 路径结构不同（cua_node/sky），需另写一套 config 模板和 setup 脚本。
- **provider/model/auth 公司电脑自配**：本机用 cc-switch 代理（PROXY_MANAGED），公司电脑不用 cc-switch，provider/model/auth 由 Codex app 登录或 config.toml 自配，不在本模板。
- **只迁开发相关 skill**：与开发无关的（营销/设计/内容/Office 等）不迁。skill 不在 git 仓库，靠手动从 `~/.cc-switch/skills/` 挑拷到 `~/.codex/skills/`。
- **auth token 绑定机器**：codex_oauth_auth.json 不能跨机拷贝，公司电脑重新登录 Codex app。
- **三个 marketplace 是 gitlink/ignored**：`i-have-adhd`、`minimalist-entrepreneur`（历史 gitlink，clone 后空目录）、`better-harness`（本次 ignore）。公司电脑需要时单独 git clone 到 `~/.claude/plugins/marketplaces/` 下。
- **runtime hash 路径**：cua_node 的 hash（如 fb8898c05a62885e）每次 Codex app 安装不同，不进模板，由 app 自动生成。
