# 工具 / 插件安装台账

记录 CLI 工具、桌面软件、Claude Code 插件 marketplace 与插件启用状态。模板见 [README.md](README.md)。

---

## Claude Code 插件 marketplace（/plugin marketplace add）

| marketplace | 来源 | 状态 |
|---|---|---|
| claude-plugins-official | https://github.com/anthropics/claude-plugins-official | 启用中 |
| anthropic-agent-skills | https://github.com/anthropics/skills | 启用中 |
| mattpocock | https://github.com/mattpocock/skills | 启用中 |
| ecc | https://github.com/affaan-m/ECC | 启用中 |
| karpathy-skills | https://github.com/forrestchang/andrej-karpathy-skills | 启用中 |
| caveman | https://github.com/JuliusBrussee/caveman | 启用中 |
| ponytail | https://github.com/DietrichGebert/ponytail | 启用中 |
| open-code-review | https://github.com/alibaba/open-code-review | 启用中 |
| understand-anything | https://github.com/Egonex-AI/Understand-Anything | **已删 2026-08-18（二次）**：08-17 首删后插件文件+settings 注册被某机制回拉复活（原因未查明，疑插件同步），今日按 wayfinder ticket 02 拍板再删——settings.json 去 enabledPlugins+marketplace 注册、删 plugins/{marketplaces,cache,data}/understand-anything*、WORKFLOW_QUICKREF.md 引用改 gitnexus/lean-ctx。恢复=`claude plugin install understand-anything@understand-anything` 后重加 marketplace |
| i-have-adhd | https://github.com/ayghri/i-have-adhd | marketplace 在，无启用插件 |
| better-harness | https://github.com/QoderAI/better-harness | 启用中 |
| minimalist-entrepreneur | https://github.com/slavingia/skills | 已加 marketplace，无启用插件 |

安装方法（通用）：
```
/plugin marketplace add <owner/repo>
/plugin install <plugin>@<marketplace>
```

## 当前启用插件（settings.json enabledPlugins，2026-08-07 快照）

- 官方：claude-code-setup / claude-md-management / code-review / code-simplifier / commit-commands / context7 / feature-dev / frontend-design / github / playwright / skill-creator / superpowers
- 三方：ecc / mattpocock-skills / ponytail / caveman / open-code-review / better-harness / andrej-karpathy-skills / understand-anything / example-skills / taste-skill / i-have-adhd

**坑**：cc-switch / claude-stack 装卸插件会丢 enabledPlugins 状态，装完立刻查 settings.json 还认不认（memory `ccswitch-plugin-integration-fragile`）。

## CLI 工具

### cc-switch
- 来源：https://github.com/farion1231/cc-switch
- 用途：Claude Code provider/配置切换 + skill 单系统同步
- 安装日期：待补
- 安装方法：桌面应用安装包（GitHub Releases）
- 装到哪：`~/.cc-switch/cc-switch.db`（settings.common_config_claude 会覆盖 ~/.claude/settings.json 公共配置——防降级见 skill `cc-switch-setting-sync`）
- 备注：切 provider 热切换可能丢 enabledPlugins/hooks/statusLine 字段。

### lean-ctx 本体
- 见 [mcp-install.md](mcp-install.md)（cargo 装二进制 + MCP 注册 + hooks）

### GitNexus / cloudcli
- 见 [mcp-install.md](mcp-install.md)（npm 全局/npx 形态）

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

### Kimi WebBridge（浏览器控制桥）
- 来源：https://cdn.kimi.com/webbridge（skill 文档指向官方帮助页 kimi.com/zh-cn/features/webbridge）
- 安装日期：2026-08-11
- 安装命令原文：`irm https://cdn.kimi.com/webbridge/install.ps1 | iex`
- 装到哪：守护进程 `C:\Users\zys31\.kimi-webbridge\bin\kimi-webbridge.exe`（日志 `...\.kimi-webbridge\logs\daemon.log`）；skill 注入 `~/.claude/skills/kimi-webbridge` 和 `~/.hermes/skills/kimi-webbridge`（均 v1.11.5）
- 依赖：需配浏览器扩展（两段式：守护进程 HTTP `127.0.0.1:10086` ↔ 浏览器扩展）；无扩展则 `extension_connected:false` 驱动不了浏览器
- 备注：二进制未签名、无版本元数据，来源非官方渠道可核实——用户知情后仍装。状态查询 `kimi-webbridge status`；启停 `kimi-webbridge start/stop`（skill 禁自动 stop/restart/uninstall）。
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
