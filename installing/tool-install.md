# 工具 / 插件安装台账

记录 CLI 工具、桌面软件、Claude Code 插件 marketplace 与插件启用状态。模板见 [README.md](README.md)。

---

## Claude Code 插件 marketplace（/plugin marketplace add）

当前集合来自 `plugins/known_marketplaces.json`；插件启用状态来自 `settings.json`。

| marketplace | 来源 | 当前状态 |
|---|---|---|
| claude-plugins-official | https://github.com/anthropics/claude-plugins-official | marketplace 存在；插件部分启用 |
| mattpocock | https://github.com/mattpocock/skills | marketplace 存在；插件启用 |
| caveman | https://github.com/JuliusBrussee/caveman | marketplace 存在；插件启用 |
| ponytail | https://github.com/DietrichGebert/ponytail | marketplace 存在；插件启用 |
| open-code-review | https://github.com/alibaba/open-code-review | marketplace 存在；插件启用 |
| better-harness | https://github.com/QoderAI/better-harness | marketplace 存在；插件启用 |
| taste-skill | https://github.com/Leonxlnx/taste-skill | marketplace 存在；插件启用 |
| last30days-skill | https://github.com/mvanhorn/last30days-skill | marketplace 存在；插件启用 |
| officecli | https://github.com/officecli/officecli | marketplace 存在；插件禁用 |
| impeccable | https://github.com/pbakaus/impeccable | marketplace 存在；插件启用 |
| ppt-master | https://github.com/hugohe3/ppt-master | marketplace 存在；插件禁用 |
| anthropic-agent-skills | https://github.com/anthropics/skills | 已移除；当前 `known_marketplaces.json` 无记录 |
| ecc | https://github.com/affaan-m/ECC | 已移除；当前 `known_marketplaces.json` 无记录 |
| karpathy-skills | https://github.com/forrestchang/andrej-karpathy-skills | 已移除；当前 `known_marketplaces.json` 无记录 |
| understand-anything | https://github.com/Egonex-AI/Understand-Anything | **已删 2026-08-18（二次）**：08-17 首删后插件文件+settings 注册被某机制回拉复活（原因未查明，疑插件同步），今日按 wayfinder ticket 02 拍板再删——settings.json 去 enabledPlugins+marketplace 注册、删 plugins/{marketplaces,cache,data}/understand-anything*、WORKFLOW_QUICKREF.md 引用改 gitnexus/lean-ctx。恢复=`claude plugin install understand-anything@understand-anything` 后重加 marketplace |
| i-have-adhd | https://github.com/ayghri/i-have-adhd | 已移除；当前 `known_marketplaces.json` 无记录 |
| minimalist-entrepreneur | https://github.com/slavingia/skills | 已移除；当前 `known_marketplaces.json` 无记录 |

安装方法（通用）：
```
/plugin marketplace add <owner/repo>
/plugin install <plugin>@<marketplace>
```

## 当前插件状态（settings.json）

- 配置记录日期：2026-09-04

- 启用：`better-harness@better-harness`、`caveman@caveman`、`claude-md-management@claude-plugins-official`、`code-review@claude-plugins-official`、`context7@claude-plugins-official`、`github@claude-plugins-official`、`impeccable@impeccable`、`last30days@last30days-skill`、`mattpocock-skills@mattpocock`、`ponytail@ponytail`、`skill-creator@claude-plugins-official`、`taste-skill@taste-skill`
- 禁用：`frontend-design@claude-plugins-official`、`open-code-review@open-code-review`、`playwright@claude-plugins-official`
- 低频插件复核（`claude plugin list`，2026-09-04）：以上 3 个插件均禁用。

### taste-skill 1.0.0（2026-09-04 恢复）
- 来源：https://github.com/Leonxlnx/taste-skill
- 安装命令原文：`claude plugin install taste-skill@taste-skill --scope user`
- 装到哪：`~/.claude/plugins/cache/taste-skill/taste-skill/1.0.0`
- 状态：`taste-skill@taste-skill`，scope=user，enabled；`claude plugin list` 与 `installed_plugins.json` 均已核对
- 依赖：无额外依赖
- cc-switch：执行 `sync_claude_common.py`，old len=9709 → new len=9746，readback=MATCH；备份 `~/.cc-switch/backups/sync-backup-20260904_171520.json`

**坑**：cc-switch / claude-stack 装卸插件会丢 enabledPlugins 状态，装完立刻查 settings.json 还认不认（memory `ccswitch-plugin-integration-fragile`）。

## CLI 工具

### cc-switch
- 来源：https://github.com/farion1231/cc-switch
- 用途：Claude Code provider/配置切换；2026-08-13 起不再管理 skills
- 安装日期：待补
- 安装方法：桌面应用安装包（GitHub Releases）
- 装到哪：`~/.cc-switch/cc-switch.db`（settings.common_config_claude 会覆盖 ~/.claude/settings.json 公共配置——防降级见 skill `cc-switch-setting-sync`）
- 备注：切 provider 热切换可能丢 enabledPlugins/hooks/statusLine 字段。

### lean-ctx 本体
- 见 [mcp-install.md](mcp-install.md)（cargo 装二进制 + MCP 注册 + hooks）

### GitNexus
- 见 [mcp-install.md](mcp-install.md)（npm 全局/npx 形态）

### cloudcli-browser（已卸载）
- 见 [mcp-install.md](mcp-install.md)（历史 MCP 记录）

### @alibaba-group/open-code-review 1.9.0
- 来源：https://github.com/alibaba/open-code-review（npm 包 `@alibaba-group/open-code-review`）
- 安装日期：未留存；全局包 `package.json` 文件时间戳为 2026-08-10
- 安装命令原文：未留存；可复现命令：`npm install -g @alibaba-group/open-code-review`
- 装到哪：`C:\Users\zys31\AppData\Roaming\npm\node_modules\@alibaba-group\open-code-review`；命令入口 `C:\Users\zys31\AppData\Roaming\npm\ocr.cmd`
- 依赖：Node.js / npm
- 用途：代码审查 CLI，命令为 `ocr`
- 备注：与 Claude Code marketplace `open-code-review` 为同一上游项目的两种安装形态；当前全局版本为 1.9.0。

### GitLab CLI（glab）
- 来源：https://gitlab.com/gitlab-org/cli（winget 包 `GLab.GLab`）
- 安装日期：2026-08-13
- 安装命令原文：`winget install --exact --id GLab.GLab --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity`
- 装到哪：`C:\Users\zys31\AppData\Local\Programs\glab\glab.exe`（用户 PATH 已包含该目录）
- 依赖：Windows Package Manager（winget）；GitLab 登录或 API Token 才能执行远端写操作
- 备注：已验证 `glab 1.113.0 (d628813)`；当前终端可能需重开后才能直接解析 `glab` 命令。

### OpenAI Codex CLI（已卸载）
- 来源：https://github.com/openai/codex（npm 包 `@openai/codex`）
- 卸载日期：2026-08-11
- 卸载命令原文：`codex logout`；`npm uninstall -g @openai/codex`
- 原安装位置：`C:\Users\zys31\AppData\Roaming\npm\node_modules\@openai\codex`、`C:\Users\zys31\.codex`
- 依赖：Node.js / npm
- 备注：Windows 核心已清理；同时删除未注册的 VS Code Codex 扩展内容、4 条定向 npm 缓存及 `C:\Users\zys31\AGENTS.md`。按用户选择保留 CC Switch 内 Codex 数据、不扫描 WSL；VS Code 占用的 0 文件扩展空目录保留。

### Kimi WebBridge（浏览器控制桥，已卸载 2026-08-31）
- 来源：官方安装器 `https://cdn.kimi.com/webbridge`（skill 文档指向官方帮助页 `https://www.kimi.com/features/webbridge`）；官方上游仓库另见 `https://github.com/MoonshotAI/kimi-code`
- 安装日期：2026-08-11
- 卸载日期：2026-08-31
- 卸载命令原文：`kimi-webbridge uninstall --yes`；官方命令停止 daemon 后因 Windows 禁止进程删除自身 exe 退出，随后手动清理残留目录与 Claude skill，并移除用户 PATH。
- 清理范围：`C:\Users\zys31\.kimi-webbridge`、`C:\Users\zys31\.claude\skills\kimi-webbridge`、用户 PATH 中对应 bin；Chrome 扩展保留。
- 安装命令原文：`irm https://cdn.kimi.com/webbridge/install.ps1 | iex`
- 装到哪：守护进程 `C:\Users\zys31\.kimi-webbridge\bin\kimi-webbridge.exe`（日志 `...\.kimi-webbridge\logs\daemon.log`）；skill 注入 `~/.claude/skills/kimi-webbridge` 和 `~/.hermes/skills/kimi-webbridge`（均 v1.11.5）
- 依赖：需配浏览器扩展（两段式：守护进程 HTTP `127.0.0.1:10086` ↔ 浏览器扩展）；无扩展则 `extension_connected:false` 驱动不了浏览器
- 兼容性核验（2026-08-26）：`MoonshotAI/kimi-code/plugins/official/kimi-webbridge/kimi.plugin.json` 为 Kimi 原生插件格式（v1.11.3），不是 Claude Code `.claude-plugin/plugin.json`；当前未安装 `kimi-webbridge@<marketplace>`，避免伪造兼容关系。
- 备注：官方安装器来源为 `cdn.kimi.com`；二进制未签名、无版本元数据，仍需保留来源与权限风险记录。状态查询 `kimi-webbridge status`；启停 `kimi-webbridge start/stop`（skill 禁自动 stop/restart/uninstall）。
- 风险提示：守护进程常驻 + 用用户真实登录态控浏览器 + 往 AI runtime 写 skill，权限面大。

## 运行环境基线
- Node.js（`C:\Program Files\nodejs\node.exe`）
- Python 3.12（解释器名 `python312`；不设 PYTHONPATH）
- Rust/cargo（`~/.cargo/bin`，lean-ctx 依赖；MinGW64/MSVC 可能不可用，优先 pre-built）


## WSL Ubuntu 桌面组件

### Breeze Cursor Theme
- 来源：Ubuntu 26.04 官方仓库（`resolute-updates/universe`）
- 安装日期：2026-08-11
- 安装命令原文：`wsl.exe -d Ubuntu -u root -- apt-get install -y breeze-cursor-theme`
- 装到哪：WSL Ubuntu 系统包 `breeze-cursor-theme`；主题目录 `/usr/share/icons/breeze_cursors`
- 依赖：APT；本次仅新增该包
- 备注：当前用户通过 `gsettings` 设置 `org.gnome.desktop.interface cursor-theme` 为 `breeze_cursors`，大小 24。

## @deepseek-ai/dsh uninstall 2026-08-16
- action: uninstalled deepseek harness CLI (@deepseek-ai/dsh), full cleanup
- install cmd: npm i -g @deepseek-ai/dsh + npx @deepseek-ai/dsh web
- uninstall cmd: npm uninstall -g @deepseek-ai/dsh (removed 528 packages)
- cleaned: npm global pkg + bin links (dsh/dsh.cmd/dsh.ps1); entire C:\Users\zys31\.dsh\ (243 files: .credentials.yaml, sessions/storages, skills/agents/commands copies of ~/.claude, profiles with nested node_modules + web)
- kept: ~/.claude/skills original (69 dirs verified intact); npm/npx cache checked clean
- note: .dsh/skills(162) & .dsh/agents were independent copies not junctions; no dsh process running before delete
- 2026-08-16 residue sweep: removed persistent user env vars OPENCODE_GO_KEY + OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS (dsh opencode-go provider config); removed 5 TEMP dsh-* dirs (acl-locks + spill). settings.json ANTHROPIC_DEFAULT_*_MODEL_NAME deepseek/glm mappings KEPT (active Claude Code proxy config, not dsh residue). Verified gone.

## cc-connect 卸载 2026-08-16
- 状态: 已删除(用户决定不再用, tmux agent 方案试完回滚后整体放弃)
- 删除内容: npm 全局包 + ~/.cc-connect/ 全部(配置/会话/日志/微信 token) + schtasks 任务 cc-connect + daemon.ps1
- 后果: 微信遥控 Claude Code 桥接已断, 需重装 + 重扫微信才可恢复
- 相关记忆已清: cc-connect-weixin-bridge.md / cc-connect-session-storage.md
- 备份残留: ~/.cc-connect/*.bak-pre-tmux-* (删目录时一并清); 会话 72c6103d 在 ~/.claude/projects 保留

## alibaba/skill-up v0.9.0（已转正，2026-08-17）
- 来源：https://github.com/alibaba/skill-up（阿里开源 Agent Skills 评估 CLI）
- 安装日期：2026-08-17（lab 冒烟测试 → 同日转正）
- 安装命令原文：`curl.exe -sL -o skill-up.zip https://github.com/alibaba/skill-up/releases/download/v0.9.0/skill-up_0.9.0_windows_amd64.zip` + `unzip`
- 装到哪：`C:\Users\zys31\bin\skill-up.exe`（已在 PATH，与 mycode.exe 同目录）
- 依赖：无（pre-built Go 二进制 26MB）；真实 agent 评测复用 claude CLI 登录态，无需 ANTHROPIC_API_KEY
- 备注：核心价值=行为型回归测试（rule_based/script 免费确定，agent_judge 贵）；产出 Anthropic 兼容 grading.json/benchmark.json/result.json/HTML。实测 Windows 原生可跑 claude_code 引擎（与官方「仅 macOS/Linux」文档矛盾）。升级：v0.9.0 二进制替换；撤回=删 exe + skill 的 evals/ 目录
- **evals 覆盖（2026-08-17 实盘，7 skill / 33 case 全过）**：ai-coding-guide 8 / article-writing-guide 8 / learning-guide 6 / guide-skill-auditor 5 / expose-unknowns 3 / code-change-workflow 2 / ai-readable-project 1。`ai-coding-coach/evals/` 为空壳（0 case，待补）。新增/补套件后当轮在此追加。跑法：`cd <skill目录> && skill-up run`（每 skill 的 evals/eval.yaml 自包含：claude_code 引擎 + rule_based 判官 + 240s 超时）。

## 终端增强套件全卸载 2026-08-17
- action: 卸载 PowerShell 终端增强软件(用户要求删干净,仅保留性能优化)
- 卸载命令原文(逐个,均 winget uninstall,全部"已成功卸载"):
  - `winget uninstall --id JanDeDobbeleer.OhMyPosh --disable-interactivity --accept-source-agreements`(Oh My Posh 30.6.1,提示符)
  - `winget uninstall --id junegunn.fzf ...`(fzf 0.74.2,模糊搜索)
  - `winget uninstall --id ajeetdsouza.zoxide ...`(zoxide 0.10.0,智能跳转)
  - `winget uninstall --id eza-community.eza ...`(eza 0.23.5,ls)
  - `winget uninstall --id sharkdp.bat ...`(bat 0.26.1,cat)
  - `winget uninstall --id sxyazi.yazi ...`(Yazi 26.5.6,文件管理器)
- 卸载位置: 全部在 `C:\Users\zys31\AppData\Local\Microsoft\WinGet\Links`(oh-my-posh 原在 WindowsApps 用户级);验证 `Get-Command` 6 命令全 gone
- 模块清理: PSFzf 2.7.12(PowershellGallery,`C:\Users\zys31\Documents\PowerShell\Modules\PSFzf`)——PSFzf.dll 被运行中 pwsh 会话锁定,**待进程释放后删目录**
- 文件删除: `~Documents\PowerShell\omp.omp.json` + `omp.omp.json.bak-20260817` + `-lite`(omp 配置及其备份)
- profile 改动: `Microsoft.PowerShell_profile.ps1` 删除 omp/PSFzf/zoxide/eza/bat/yazi 六个块,保留:UTF-8 编码、`$isInteractive` 守卫、PATH 兜底、PSReadLine(预测+历史搜索)、cc/cr 别名
- 保留的优化: PSReadLine 配置、非交互守卫、`cc`/`cr`(claude 启动)别名、git 全局 10 别名;实测冷启动 484ms/profile 开销 160ms
- 依赖: winget、PowershellGallery;无其他
- 备注: 恢复=winget install 各包后重写 profile 块;omp 主题文件已删需重建。相关记忆 `terminal-visual-default-preference`(用户偏好默认视觉,连 omp 纯黑白也停用)

## pi coding agent（earendil-works/pi，DIY agent 实验室）2026-08-18
- 来源：https://github.com/earendil-works/pi（fork：github.com/zys3198/pi，MIT）
- 安装日期：2026-08-18
- 安装命令原文：
  1. `git clone https://github.com/zys3198/pi.git C:\ZYS\Code\pi` —— GitHub 直连 443 超时，实际经 `https://gh-proxy.com/https://github.com/zys3198/pi.git` 镜像克隆成功（5719 commits，HEAD=2509b5c03=上游最新）；clone 后 `git remote set-url origin` 钉回真 GitHub + `git remote add upstream https://github.com/earendil-works/pi.git`
  2. `cd C:\ZYS\Code\pi && npm install --ignore-scripts`（exit 0，found 0 vulnerabilities）
  3. `npm run build:offline` —— **失败**：a) 缺 model-data（`packages/ai/src/providers/data/` 在 gitignore，须 `npm run hydrate:model-data` 联网拉目录）；修复=经 gh-proxy 下载官方 release 源码包 `pi-0.84.2-source.tar.gz`（6.2MB），tar 提取 `packages/ai/src/providers/data/`（40 json + .manifest.json）与 `data-json.d.ts` 入仓库；b) 提取后 check:model-data 通过，但 tsgo 编译报 `src/providers/xai.ts(8,2)` 类型错（HEAD 比 v0.84.2 release 新，xai.ts 已认 openai-completions+responses，生成类型列旧）——**纯编译期错，dev 走 tsx 跑源码不受影响**
- dev 跑法：`cd C:\ZYS\Code\pi && .\pi-test.ps1 [args]`（官方 Windows 入口，tsx 直跑 `packages/coding-agent/src/cli.ts`；`--no-env` 清约 35 个 provider env 隔离密钥）
- 装到哪：仓库 `C:\ZYS\Code\pi`；配置 `~/.pi/agent/settings.json`（defaultProvider=opencode-go + shellPath=`C:/ZYS/Software/Git/bin/bash.exe` + enableAnalytics/enableInstallTelemetry=false）；`~/.pi/agent/APPEND_SYSTEM.md`（4 条用户核心规则：中文/不确定先问/多步报进度/极简不加戏）
- 依赖：Node 24 / npm 11（本机已有）；**Git Bash 硬前置**——本机 Git 在 `C:\ZYS\Software\Git`（非 Program Files），且 PATH 里 `System32\bash.exe`（WSL 转发器）排前，必须 settings shellPath 钉死否则 pi 会误启 WSL bash
- 模型：默认 opencode-go（env `OPENCODE_API_KEY`，**尚未配置** → `pi auth check --provider opencode-go` 报 `not_ready/credentials_not_configured`，属预期）。火山 Ark 走**官方配置式扩展**（非源码改动）：`~/.pi/agent/extensions/ark.ts` 用 `pi.registerProvider("ark", { baseUrl: https://ark.cn-beijing.volces.com/api/coding/v3, apiKey: "$ARK_API_KEY", api: "openai-completions", models: [7 个] })`——**必须用 `/api/coding/v3` 端点**（coding 工具专用；通用 `/api/v3` 对 coding 模型清单报 `InvalidEndpointOrModel.NotFound`，2026-08-18 实测 3/7 通：deepseek-v4-flash/kimi-k2.7-code/deepseek-v4-pro）；扩展目录 `~/.pi/agent/extensions/` 自动发现 + `/reload` 热重载（docs/extensions.md）。opencode-go 原生（env-api-keys.ts 确认）。用户 8/16 清 dsh 时已删 `OPENCODE_GO_KEY`，需重新申请
- 冒烟：`--version`=0.84.2、`--list-models` 正常（无 key 只列默认可见集 anthropic13+minimax3，非缺数据）、`pi auth check` 命令可用
- 备注：GH 直连本机不通、gh-proxy 镜像可用（clone/release 都靠它）；上游每日大 commit 量，策略=main 纯镜像+自定义走特性分支；构建类型错处理=跟上生成文件/连网 `npm run build`/或 checkout 贴近 release



## superpowers 插件卸载（手法层转 mattpocock-skills + ask-matt）2026-08-19
- 来源：claude-plugins-official marketplace，原安装记录见本文件前文
- 卸载日期：2026-08-19
- 卸载动作原文：
  1. ~/.claude/settings.json enabledPlugins 删 `superpowers@claude-plugins-official` 一行（手动编辑）
  2. python ~/.claude/skills/cc-switch-setting-sync/scripts/sync_claude_common.py（dry-run 9062→9013 后写入，备份 `~/.cc-switch/backups/sync-backup-20260819_134401.json`，readback MATCH）——防切 provider 时 SP 复活
- 插件缓存目录 `~/.claude/plugins/cache/claude-plugins-official/superpowers` 留盘未删（不加载即不生效；要彻底删另行确认）
- 同步改动：ai-coding-guide routing.md/routing-classification-details.md/ecosystems.md 清全部 superpowers 条件路径→改指 matt 单环（grilling/tdd/diagnosing-bugs/code-review 为 model-invoked；ask-matt/grill-me/to-spec 等为 user-invoked 需手动敲）；expose-unknowns/skill-trimmer/ccswitch-architecture 同步；eval case rt-named-plugin-priority 改锚 ponytail
- 背景决策：手法层不自建不自动借，matt 套件替代 SP；ask-matt = matt 套件内官方路由（idea→ship 主流程 grill-with-docs→to-spec→to-tickets→implement）
- 依赖：mattpocock-skills@mattpocock 插件保持启用
- 备注：恢复 = settings.json 加回 enabledPlugins 行 + 跑同一 sync 脚本


## code-simplifier + claude-code-setup 插件卸载 2026-08-19
- 来源：claude-plugins-official marketplace
- 卸载日期：2026-08-19
- 卸载动作原文：
  1. ~/.claude/settings.json enabledPlugins 删 `code-simplifier@claude-plugins-official` 与 `claude-code-setup@claude-plugins-official` 两行（手动编辑）
  2. python ~/.claude/skills/cc-switch-setting-sync/scripts/sync_claude_common.py（dry-run 9013→8905 后写入，备份 `~/.cc-switch/backups/sync-backup-20260819_141800.json`，readback MATCH）
- 插件缓存留盘未删（不加载即不生效）
- 判决依据：能力补丁型随模型变强贬值——code-simplifier=subagent 简化代码（强模型原生能力，ponytail 纪律已覆盖）；claude-code-setup=一次性配置推荐（用完即弃）。references 零引用，已扫确认
- 同日已卸 superpowers（见前条）；可议未砍：claude-md-management、better-harness
- 备注：恢复 = settings.json 加回 enabledPlugins 行 + 跑同一 sync 脚本

## Poppler PDF 工具 25.07.0-0（2026-08-21）
- 来源：https://github.com/oschwartz10612/poppler-windows/releases/download/v25.07.0-0/Release-25.07.0-0.zip（WinGet 包 `oschwartz10612.Poppler`）
- 安装日期：2026-08-21
- 安装命令原文：`winget install --id oschwartz10612.Poppler --exact --accept-source-agreements --accept-package-agreements`
- 装到哪：用户级 WinGet 安装目录；命令别名加入用户 PATH
- 依赖：Windows Package Manager（winget）、Microsoft.VCRedist.2015+.x64
- 用途：提供 `pdftoppm`、`pdfinfo`、`pdftotext` 等 PDF 读取工具
- 备注：安装后需重启 shell 才能解析更新后的 PATH

### Claude Code 原生版 2.1.251（2026-08-29）
- 来源：https://claude.ai/install.ps1（Anthropic 官方 Windows 原生安装器）
- 安装日期：2026-08-29
- 安装命令原文：`powershell.exe -NoProfile -Command "Invoke-RestMethod 'https://claude.ai/install.ps1' | Invoke-Expression"`
- 替换动作原文：验证原生二进制版本与 Authenticode 签名后执行 `npm uninstall -g @anthropic-ai/claude-code`
- 装到哪：`C:\Users\zys31\.local\bin\claude.exe`；版本文件 `C:\Users\zys31\.local\share\claude\versions\2.1.251`
- 依赖：Windows 10 1809+、x64/ARM64；本机为 win32-x64
- 备注：替换 npm 全局版 2.1.251；原 npm 平台 optional dependency 缺失，`bin\claude.exe` 仅为 500 字节占位脚本。原生二进制签名有效，签名者 `Anthropic, PBC`；`claude doctor` 报 `No installation issues found`，自动更新已启用。用户配置 `~/.claude/`、`~/.claude.json` 与项目配置未删除。

### OpenAI Codex CLI 0.151.0（重新安装，2026-08-29）
- 来源：https://www.npmjs.com/package/@openai/codex（npm 包 `@openai/codex`）
- 安装日期：2026-08-29
- 安装命令原文：`npm uninstall -g @openai/codex && npm cache verify && npm install -g @openai/codex@latest --include=optional`
- 装到哪：启动器 `C:\Users\zys31\AppData\Roaming\npm\codex.cmd`；主包 `...\node_modules\@openai\codex`；Windows x64 原生包位于主包的 `node_modules\@openai\codex-win32-x64`
- 依赖：Node.js / npm；运行时原生包 `@openai/codex@0.151.0-win32-x64`
- 备注：修复主包存在但 optional dependency 缺失导致的启动失败。已验证 `codex-cli 0.151.0`；`codex.exe` 为 Windows x86-64 PE32+，Authenticode 签名有效，签名者 `OpenAI OpCo, LLC`。

### Agent Reach 1.5.0（2026-09-02）
- 来源：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md；上游包：https://github.com/Panniantong/agent-reach/archive/main.zip
- 更新日期：2026-09-02
- 更新命令原文：`python -m pip install --upgrade https://github.com/Panniantong/agent-reach/archive/main.zip`
- 装到哪：Agent Reach 入口 `C:\Users\zys31\AppData\Local\Programs\Python\Python312\Scripts\agent-reach`；包目录 `C:\Users\zys31\AppData\Local\Programs\Python\Python312\Lib\site-packages`
- 依赖：Python 3.12；feedparser 6.0.14；yt-dlp 2026.8.19；mutagen 1.48.1；pycryptodomex 3.23.0；yt-dlp-ejs 0.8.0；已有 loguru、python-dotenv、pyyaml、requests、rich、websockets、brotli
- 同步更新：已安装 `twitter-cli`（已是最新 v0.8.5）、`bilibili-cli`（已是最新 v0.6.2）、`xiaohongshu-cli`（v0.6.4）、`yt-dlp`；未新增 OpenCLI
- 验证：`agent-reach version`=v1.5.0；`agent-reach doctor`=5/15 个渠道可用；YouTube=`yt-dlp`、B站=`bili-cli`、V2EX=`V2EX API (public)`、RSS=`feedparser`、网页=`Jina Reader`
- 备注：`rdt-cli` 未更新；文档要求从未由用户明确指定的 Git 仓库安装固定提交，安全策略拦截。Twitter、Reddit、小红书仍需显式 Cookie；Exa 未配置；未运行会读取或写入浏览器 Cookie 的命令。

### DTSF 前端项目工具链（2026-09-04）
- 来源：项目锁文件 `C:\ZYS\Code\dtsf-eam\code\frontend\soybean-admin\pnpm-lock.yaml`
- 安装日期：2026-09-04
- 安装命令原文：`pnpm install --frozen-lockfile`
- 装到哪：`C:\ZYS\Code\dtsf-eam\code\frontend\soybean-admin\node_modules`
- 依赖：Node.js、pnpm；pnpm workspace 共链接 897 个包，全部从本地缓存复用
- 备注：`simple-git-hooks` 已设置项目 Git hooks；pnpm 拦截 `tesseract.js@7.0.0` 构建脚本并返回 `ERR_PNPM_IGNORED_BUILDS`，未执行 `pnpm approve-builds`；前端类型检查及生产构建均无需该脚本并已通过。

### Cloudflare Tunnel CLI 2026.8.3（2026-09-05 核验）
- 来源：https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/（WinGet 包 `Cloudflare.cloudflared`）
- 原安装日期：未核实；本次核验日期：2026-09-05
- 本次安装命令原文：`winget install --id Cloudflare.cloudflared --exact --accept-package-agreements --accept-source-agreements`
- 本次命令结果：WinGet 检测到现有 2026.8.3，且无可用升级；未重复安装
- 装到哪：`C:\Program Files (x86)\cloudflared\cloudflared.exe`
- 依赖与权限面：Windows Package Manager；运行 Quick Tunnel 时建立出站连接，并通过随机 `trycloudflare.com` HTTPS 地址临时公开本机目标 HTTP 服务
- 当前状态：可用；已验证 `cloudflared version 2026.8.3 (built 2026-08-31T02:48 UTC)`
- 备注：当前 PATH 不含安装目录，需使用绝对路径或后续单独配置 PATH；Quick Tunnel 仅用于测试，停止进程后公网入口失效。

## headroom-ai 0.37.0（2026-09-05）

- 来源：https://github.com/headroomlabs-ai/headroom（PyPI `headroom-ai[all]`）；决策依据：https://zhenjia.dev/posts/headroom-cc-switch-coexist
- 安装日期：2026-09-05
- 安装命令原文：`uv tool install --python 3.13 "headroom-ai[all]"`
- 装到哪：exe `C:\Users\zys31\.local\bin\headroom.exe`（uv tool）；包在 uv cache `...\uv\cache\archive-v0\ZvCxZqX063vhJ65f\`
- 依赖：uv 0.12.7；Python 3.13.13（uv 管理）
- 配置：env `HEADROOM_BEACON=off`、`HEADROOM_CC_SWITCH_RECONCILE=1`；`headroom proxy --host 127.0.0.1 --port 8787`
- 验证：`/health` 200；`/admin/upstream` 返回 `captured_upstream=http://127.0.0.1:15721`、`cc_switch_reconcile=true`；settings.json `ANTHROPIC_BASE_URL` 被 reconciler 改写为 `http://127.0.0.1:8787`，token/model 映射原样保留；本 CC 会话经 8787 链路正常对话
- 备注：
  - 持久化（2026-09-05 同日补装）：管理员终端跑 `headroom install apply --preset persistent-service --no-telemetry --env HEADROOM_BEACON=off --env HEADROOM_CC_SWITCH_RECONCILE=1`（Windows 自动降级 persistent-task），创建计划任务 `headroom-default-startup`（登录自启，动作=`C:\Users\zys31\.headroom\deploy\default\ensure-headroom.cmd`）与 `headroom-default-health`；任务部署不支持 `headroom install start`，手动拉起用 `Start-ScheduledTask -TaskName headroom-default-startup`
  - 回滚：`uv tool uninstall headroom-ai`；cc-switch 重新切换一次 provider 即覆盖回 15721
  - 遥测已关；官方 `{"env":{}}` 时 reconciler 默认直连不插手

### OpenAI Codex CLI 0.153.4（已卸载，2026-09-05）
- 来源：https://www.npmjs.com/package/@openai/codex（npm 包 `@openai/codex`）
- 卸载日期：2026-09-05（此前生命周期：2026-08-26 卸载 → 2026-08-29 重装 0.151.0 → 自动升至 0.153.4）
- 卸载命令原文：`npm uninstall -g @openai/codex`（输出 `removed 2 packages`）；`Remove-Item -LiteralPath "C:\Users\zys31\.codex" -Recurse -Force`
- 原安装位置：启动器 `C:\Users\zys31\AppData\Roaming\npm\codex.cmd`；主包 `...\npm\node_modules\@openai\codex`；配置目录 `C:\Users\zys31\.codex`（78.7MB，其中 `.tmp/` 占 76MB）
- 依赖：Node.js / npm
- 恢复所需材料（已备份到 `C:\Users\zys31\.claude\backups\codex-pi-purge-20260905\`）：`codex-config.toml`（426B，cc-switch 注入的 `model_provider=arkcli-coding-plan` + Volcano bearer token + lab-area `trust_level=trusted` + `[windows] sandbox=elevated`）、`codex-version.json`、`codex-installation_id`
- 恢复步骤：`npm install -g @openai/codex@latest --include=optional` → 从 cc-switch GUI 切一次 Codex provider 自动重建 `~/.codex/config.toml`（或直接拷回备份的 codex-config.toml）
- 备注：**cc-switch 侧全部保留**（用户明确要求）——`~/.cc-switch/cc-switch.db`、`codex_oauth_auth.json`（2417B，version 2，1 个 account，default_account_id 在位）、`settings.json` 卸载前后均校验存在且 mtime 未变。`~/.codex/auth.json` 本就不存在（codex 账户凭据由 cc-switch 托管，与 `~/.codex` 物理隔离），故删目录不影响账户。卸载前无 codex 进程运行。

### pi coding agent 残留清理（2026-09-05）
- 背景：2026-09-04 用户拍板弃用 pi（见 [[pi-migration-native-goal]] 存档），本次做物理清理
- 卸载/删除命令原文：`Remove-Item -LiteralPath <各路径> -Recurse -Force`（逐条字面量执行；多路径循环脚本会被 gateguard 判为 `/` 拦截）
- 已删除清单（合计约 250MB，全部不可逆）：
  1. `C:\ZYS\Code\pi` —— fork 仓库 86.8MB / 1438 文件。删前核验：`git status` clean、`@{u}..HEAD` 无未推送 commit、无 stash、HEAD=853a80d26 与 origin/main 同步，origin 指向 `https://github.com/earendil-works/pi`（上游），可重新 clone
  2. `C:\Users\zys31\.claude\backups\skill-trim-20260903\pi-side` —— 150.89MB / 16263 文件（skills 27 目录 10MB + skills-sync 140.89MB）
  3. `C:\ZYS\Code\lab-area\.pi` —— 约 200 个空 session 目录 / 0.05MB
  4. `C:\ZYS\Code\lab-area\exp\2026-08-23-hermes-migration` —— 11.13MB（sessions.db + failures.md/MEMORY.md/USER.md）
  5. `C:\ZYS\Code\lab-area\exp\2026-08-23-pi-smoke` —— 空目录
  6. `C:\ZYS\Code\lab-area\exp\2026-08-23-skill-pilot` —— 0.382MB（ai-coding-guide 08-23 副本）
- **已知永久损失（用户在明确告知后仍选择全删，2026-09-05）**：
  - pi-side 里 7 个 skill 为孤本，既不在 `~/.claude/skills/` 也不在 skill-trim-20260903 兄弟目录：`ai-coding-guide`（08-25 最新版）、`codebase-deep-index`、`design-cold-index`、`guide-skill-auditor`、`javaguide-style-guide`、`lesson-svg-diagram`、`misc-cold-index`。其中 ai-coding-guide 尚存 3 处 08-23 旧副本（`exp/2026-08-23-skill-full`、`exp/2026-08-28-skill-unify-backup\claude` 与 `\pi-self`、`exp/2026-08-23-skill-convert-test\work`），其余 6 个无任何副本
  - `hermes-migration/failures.md` 的 25 条长期 correction/preference（learning-first 定案、learning-personas 执行细则、PowerShell 正则坑、终端视觉别重设计、学习重点四方向等）未沉淀进 `~/.claude/projects/*/memory/`，无副本
- 未受影响：`~/.pi` 本次开始前即不存在；`C:\ZYS\Code\pi-stack` 不存在；`skill-trim-20260903` 其余 13 项存档（ai-coding-coach / article-writing-guide / deep-learn / expose-unknowns / generic-course-tutor-workspace / hallmark / lean-ctx / learning-guide / learning-personas / preflight-check / tech-learning-roadmap / tutorial-maker / wiki-skill--from-lab-area）完好

### Go 1.27.0（2026-09-07）
- 来源：https://go.dev/dl/；WinGet 包 `GoLang.Go`
- 安装日期：2026-09-07
- 安装命令原文：`winget install --exact --id GoLang.Go --accept-package-agreements --accept-source-agreements --disable-interactivity`
- 装到哪：`C:\Program Files\Go\bin\go.exe`；默认 GOPATH=`C:\Users\zys31\go`
- 依赖：Windows Package Manager（winget）；Go 官方 Windows amd64 MSI
- 验证：`go version go1.27.0 windows/amd64`；当前已安装但现有终端 PATH 尚未刷新，重开 PowerShell 后使用 `go` 命令
- 备注：首次尝试带 `--scope user` 失败（当前 MSI 不支持该 scope）；移除 scope 后安装成功。用途：为 Herdr Windows 插件构建提供 Go，尤其是 `cloudmanic/herdr-plus`。

### Herdr 0.8.2（2026-09-07，lab 试用中，未转正）
- 来源：https://herdr.dev/zh-cn/docs/install/ ；上游仓库 https://github.com/herdrdev/herdr
- 安装日期：2026-09-07
- 用途：终端复用器（tmux/zellij 类）。核心卖点=**AI 编程 agent 感知**（自动检测 pane 内 agent 的 idle/working/blocked 并向上汇总到 pane→tab→workspace 侧栏）+ **会话持久化**（detach/reattach、重启恢复、窗格历史回放）
- 安装命令原文（**未用官方 `irm | iex` 一行流**，改落盘方式便于杀软扫描与人工审查）：
  1. `curl.exe -fsSLo install.cmd https://herdr.dev/install.cmd` —— 729B，审阅结论：仅把 install.ps1 下到 `%TEMP%` 再执行，无其他逻辑
  2. `curl.exe -fsSLo install.ps1 https://herdr.dev/install.ps1` —— 834 行，审计见下
  3. `powershell.exe -NoProfile -File "C:\ZYS\Code\lab-area\exp\2026-09-07-herdr\install.ps1"` —— **刻意不加 `-ExecutionPolicy Bypass`**（该开关被权限门拦截；实测也不需要：curl.exe 下载不打 Zone.Identifier/MOTW，LocalMachine 策略 `RemoteSigned` 按本地脚本放行）
- 装到哪：
  - 本体 `C:\Users\zys31\.herdr\packages\standalone\releases\0.8.2-x86_64-pc-windows-msvc\`（`herdr.exe` 22.4MB + `conpty\` + `THIRD-PARTY-NOTICES\`，合计 23.6MB）
  - junction `C:\Users\zys31\.herdr\packages\standalone\current` → 上述版本目录
  - junction `C:\Users\zys31\AppData\Local\Programs\Herdr\bin` → 上述版本目录（**无第二份拷贝**）
  - 配置（尚未生成）：`%APPDATA%\herdr\config.toml`；socket `%APPDATA%\herdr\herdr.sock`
- PATH：`HKCU\Environment` 的 `Path` 前置了**版本目录本身**（非 junction）。installer 的 `Update-PathRegistryEntry` 会按 ReleasesDir 父级匹配剔除旧版本条目，`herdr update` 理应自动改写——**升级后需复查该条目是否指向新版本**
- 依赖：无（单二进制，自带 app-local ConPTY 运行时）。**不得只拷 `herdr.exe`，必须保留整个目录**
- 安装器审计（2026-09-07）：只从 `herdr.dev` 拉 `latest.json` / `preview.json` 清单；对下载产物做 **SHA-256 校验**；只写 `HKCU\Environment`（不碰 HKLM）；免管理员；版本化目录 + junction，更新不覆盖运行中的二进制
- 验证：`herdr --version` = `herdr 0.8.2`；`herdr agent list` 返回结构化 JSON `server_not_running`（预期，TUI 未启动）
- 备注：
  - **Claude Code 集成层级=混合**：`herdr integration install claude` 只提供原生会话恢复，状态判定仍走屏幕检测（读 pane 底部缓冲区匹配 TOML 规则）。因此**不需要改 `~/.claude/settings.json`**，绕开 safety-net hooks 锁死坑（memory `safety-net-edit-lockout`）
  - 排障：`herdr agent list` 看识别结果；`herdr agent explain <target> --json` 看判定依据；检测规则可本地覆盖 `~/.config/herdr/agent-detection/<agent>.toml`（Windows 实际路径待确认）
  - 通道：默认 stable；`herdr channel set preview|stable` 切换；`herdr update` 仅对自家 installer 装的实例生效
  - **未核实项**：完整 agent 支持列表（只确认 `claude`/`codex` 为文档示例）；官方承认存在但未读到的「Windows 平台特定限制」；Windows 上 socket API / 远程访问是否受限（`herdr.dev/agent-guide.md` 该段源文本损坏）
  - 卸载：删 `C:\Users\zys31\.herdr`、`%LOCALAPPDATA%\Programs\Herdr`、`%APPDATA%\herdr`，并从 `HKCU\Environment` 的 `Path` 移除版本目录条目
  - 试验目录：`C:\ZYS\Code\lab-area\exp\2026-09-07-herdr\`（留存 install.cmd / install.ps1 副本）
  - 选型理由：与 Wave Terminal 对比后选定——Wave 是宿主级替换（要重验 headroom 8787 链路 / hooks / statusline），herdr 是薄层复用器不动现有链路；且不接管 skill/配置/记忆，退出成本接近零（对照 pi 退役时丢 7 个 skill 孤本的教训）

### agent-browser 0.36.0（2026-09-07）
- 来源：https://github.com/vercel-labs/agent-browser（npm 包 `agent-browser`）
- 安装日期：2026-09-07
- 安装命令原文：`npm install -g agent-browser`
- 装到哪：启动器 `C:\Users\zys31\AppData\Roaming\npm\agent-browser.ps1`；全局包 `C:\Users\zys31\AppData\Roaming\npm\node_modules\agent-browser`
- 依赖：Node.js / npm；本次未额外执行 `agent-browser install`，由 CLI 自动启动可用浏览器
- 用途：AI 浏览器自动化 CLI；`snapshot` 获取可访问性树和元素引用，配合 `click/fill` 操作
- 验证：`agent-browser --version`=`0.36.0`；`open https://example.com` → `snapshot` 成功得到 `e1/e2` 引用 → `close` 正常
- 备注：Lightpanda 未安装；恢复命令为上述 npm 安装命令，卸载为 `npm uninstall -g agent-browser`
