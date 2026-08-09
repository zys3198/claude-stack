# Claude Code 配置清单表（速查 · 全量）

> 生成日期：2026-07-03 ｜ **2026-08-08 盘查刷新** ｜ 扫描方式：实盘 `~/.claude/` + `~/.claude.json` + `~/.cc-switch/cc-switch.db`
> 列约定：`路径 / 对象` · `用途` · `状态 / 计数` · `维护要点`
> **替代** 旧的 `config-inventory.md`（散文版，计数已过时，见文末「废弃说明」）。

---

## 0. 顶层配置文件（机器级）

| 路径 | 用途 | 状态 / 计数 | 维护要点 |
|------|------|-------------|----------|
| `~/.claude/CLAUDE.md` | 全局规则（13 节 + caveman/lean-ctx 段） | 活跃，本会话指令源 | 改前走 §5 GateGuard 声明 |
| `~/.claude/settings.json` | 主配置：env/permissions/hooks/statusLine/plugins | 见 §1 | 改完同步 ccswitch（§3）防热切换降级 |
| `~/.claude/settings.local.json` | 本机覆盖（不入库） | 未扫到独立项 | secrets 放这，别进 `settings.json` |
| `~/.claude/keybindings.json` | 快捷键绑定 | 存在 | - |
| `~/.claude/WORKFLOW_QUICKREF.md` | 工作流速查 | 存在 | - |
| `~/.claude/long-complex-task-prompt.md` | 长复杂任务 prompt（§10 引用） | 存在 | - |
| `~/.claude.json` | Claude Code 根状态 | **59 projects / 5 mcpServers / 42 顶层键**（2026-08-08 实测） | 见 §7 / §9；含 `userID` `machineID` |
| `~/.mcp.json` | 用户级 MCP（独立于 settings） | **0 servers（空）** | 实际 MCP 走 `~/.claude.json` 根 + ccswitch db |
| `~/.claude/.claude.json`（项目级） | claude 自身目录的 project 配置 | 存在（属 §9 的 59 条之一） | - |

---

## 1. settings.json 内部（`~/.claude/settings.json`）

### 1.1 env（模型与代理路由）

| 键 | 值 | 用途 | 维护要点 |
|----|----|------|----------|
| `ANTHROPIC_AUTH_TOKEN` | `PROXY_MANAGED` | 占位，真实 token 由 ccswitch 代理注入 | 别手填真值 |
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:15721` | 走 ccswitch 本地代理 | 与 ccswitch `proxy_config.listen_port=15721` 对齐 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` / `_NAME` | `claude-opus-4-8[1M]` / `glm-5.2` | Opus 路由 -> 后端 GLM-5.2 | 切 provider 时同步改 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` / `_NAME` | `claude-sonnet-4-6[1M]` / `deepseek-v4-pro` | Sonnet 路由 -> DeepSeek-v4-pro | 同上 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` / `_NAME` | `claude-haiku-4-5` / `deepseek-v4-flash` | Haiku 路由 -> DeepSeek-v4-flash | 同上 |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` / `_NAME` | `claude-fable-5[1M]` / `kimi-k3` | Fable 路由 -> Kimi-K3 | 同上 |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | 推理强度 | - |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | 实验特性：agent teams | 升级后可能改名，留意 |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | `262144` | 自动压缩窗口（256K） | - |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | `262144` | 最大上下文（256K） | - |
| `ENABLE_TOOL_SEARCH` | `true` | 延迟工具加载（本会话生效） | - |

### 1.2 行为开关

| 键 | 值 | 说明 |
|----|----|------|
| `includeCoAuthoredBy` | `false` | commit 不加 Co-authored-by |
| `attribution.commit` / `attribution.pr` | `""` | 空，配合上一条 |

> 注：`model` / `effortLevel` 字段**不在 settings.json**（2026-08-08 实测）；effort 走 env `CLAUDE_CODE_EFFORT_LEVEL=max`，模型走 env 的 `ANTHROPIC_DEFAULT_*_MODEL`。

### 1.3 permissions.allow

12 个 lean-ctx 工具免确认：`ctx_read` / `ctx_search` / `ctx_tree` / `ctx_overview` / `ctx_plan` / `ctx_metrics` / `ctx_compress` / `ctx_session` / `ctx_knowledge` / `ctx_graph` / `ctx_retrieve` / `ctx_provider`。

> 写类工具（ctx_edit / ctx_shell）**未**进 allow，仍走确认。

---

## 2. Hooks（settings.hooks）

事件 7 类 × 多 matcher。Python 解释器固定 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`。lean-ctx 用 `~/.cargo/bin/lean-ctx.exe`。

### 2.1 自研 Python hooks（settings.json 引用 = 生效）

| 文件 | 触发事件 | matcher | 用途 |
|------|----------|---------|------|
| `git_guard.py` | PreToolUse | `Bash\|shell...` | 拦危险 git（rm -rf / DROP / force push 等） |
| `secret_guard.py` | PreToolUse **且** PostToolUse | shell 类 | 拦密钥外泄（20+ 模式） |
| `dep_gate.py` | PreToolUse | shell 类 | Fact-Forcing Gate（拦截非代码 Edit/Write） |
| `placeholder_guard.py` | PreToolUse | Edit/Write 类 | 拦占位符（TODO / `...` / `for brevity`） |
| `edited_tracker.py` | PreToolUse **且** PostToolUse **且** SessionStart | Edit/Write + 全局 | 追踪改动文件 |
| `verify_recorder.py` | PostToolUse | shell 类 | 记录验证命令执行 |
| `verify_gate.py` | Stop | `.*` | 收尾验收闸 |

### 2.2 已清理的死代码（2026-08-08 删除）

| 文件 | 曾用途 | 状态 |
|------|--------|------|
| `turn_counter.py` | 曾挂 UserPromptSubmit 做轮次计数（>10 提示压缩） | 2026-08-08 删除（settings.json 未引用） |
| `learning_nudge.py` | 学习提醒（实验） | 2026-08-08 删除 |

> 状态文件 `turn_state.json` / `learning_state.json` 同删。hooks/ 现仅留 settings.json 引用的 7 个 Python hook（见 §2.1）。

### 2.3 lean-ctx 内置 hook（同一可执行文件，不同子命令）

| 子命令 | 事件 | matcher | 作用 |
|-------|------|---------|------|
| `hook observe` | SessionStart / UserPromptSubmit / PreCompact / SessionEnd / Stop / PostToolUse(`.*`) | `.*` | 会话观测，建索引 |
| `hook rewrite` | PreToolUse | `Bash\|bash\|PowerShell` | shell 压缩重写 |
| `hook redirect` | PreToolUse | `Read\|Grep\|Search\|List*` | 把原生 Read/Grep 重定向到 ctx_* |

### 2.4 备份与脚本

| 路径 | 用途 |
|------|------|
| `~/.claude/hooks/HOOKS_BACKUP.md` | hook 备份文档 |
| `~/.claude/hooks/lean-ctx-redirect.sh` / `lean-ctx-redirect-native` | 重定向脚本（双形态） |
| `~/.claude/hooks/lean-ctx-rewrite.sh` / `lean-ctx-rewrite-native` | 重写脚本 |

---

## 3. cc-switch（`~/.cc-switch/`）- provider 单一真相源

数据库 `cc-switch.db`（sqlite，**18 表**，2026-08-08 实测）。当前 claude provider = **VolcanoArk For Coding**（`is_current=1`，claude app_type）。

### 3.1 核心表

| 表 | 行数 | 用途 | 维护要点 |
|----|------|------|----------|
| `providers` | 13 | 多 provider 配置（claude/claude-desktop/codex/gemini/hermes/opencode） | 含 **真实 API key**，备份勿外传 |
| `provider_endpoints` | 10 | 每 provider 的 endpoint URL | - |
| `mcp_servers` | 5 | MCP 服务定义（跨工具同步源） | 与 `~/.claude.json` root mcpServers 对齐（均 5） |
| `skills` | **186** | 跨工具 skill 注册 | 磁盘 105，**db 多 81**（含磁盘已删/未同步项） |
| `skill_repos` | 10 | skill 仓库源 | - |
| `prompts` | 1 | 自定义 prompt | - |
| `settings` | 10 | ccswitch 自身设置（KV） | 含 `common_config_claude`（§3.3） |
| `proxy_config` | 4 | claude/codex/gemini/opencode 代理设置 | claude: `127.0.0.1:15721` enabled |
| `provider_health` | 4 | 健康检查 | - |
| `proxy_request_logs` | **21729** | 每次请求计费/延迟日志 | 大表，定期归档 |
| `model_pricing` | 188 | 计费表 | 升级模型时更新 |
| `stream_check_logs` | 0 | 流式探活 | - |
| `proxy_live_backup` | 2 | 热切换前备份 | - |
| `session_log_sync` | 1077 | 会话日志同步偏移 | - |
| `usage_daily_rollups` | **218** | 日用量汇总 | 已触发（旧为 0） |
| `profiles` | 0 | profile 配置 | - |

### 3.2 providers 全量（13 个）

| name | app_type | category | is_current |
|------|----------|----------|------------|
| VolcanoArk For Coding | claude | - | **✅ 1** |
| DeepSeek | claude | cn_official | 0 |
| Kimi For Coding | claude | cn_official | 0 |
| Kimi For Coding Guide | claude | cn_official | 0 |
| Zhipu GLM | claude-desktop | cn_official | 1 |
| VolcanoArk For Coding | codex | - | 1 |
| Kimi For Coding | codex | cn_official | 0 |
| Zhipu GLM | opencode | cn_official | 0 |
| OpenCode Go | opencode | third_party | 0 |
| OMO Slim | opencode | omo-slim | 1 |
| MiniMax | opencode | cn_official | 0 |
| deepseek | hermes | - | 0 |
| Google Official | gemini | official | 0 |

> 当前 claude 主线 = VolcanoArk For Coding（火山方舟）。国内 provider 池：GLM / DeepSeek / MiniMax / Kimi / VolcanoArk。
> **secrets 全在 `providers.settings_config`**，备份/分享前必须脱敏。

### 3.3 ccswitch 设置同步

| 路径 / 对象 | 用途 | 维护要点 |
|-------------|------|----------|
| `~/.cc-switch/settings.json` | ccswitch 写回 claude settings.json 的模板 | 改 claude 配置后跑 skill `cc-switch-setting-sync` |
| `settings` 表 `common_config_claude` | 公共配置（防 provider 切换降级） | 同上 |
| `~/.cc-switch/BACKUP_BEFORE_CHANGE.md` | 改前备份说明 | - |
| `~/.cc-switch/RESTORE_SYMLINKS.md` | 符号链接恢复说明 | Windows symlink 常失败，按 CLAUDE.md §9 copy 不 symlink |
| `~/.cc-switch/codex_oauth_auth.json` | codex oauth 凭据 | secret |
| `~/.cc-switch/copilot_auth.json` | copilot 凭据 | secret |

---

## 4. 插件（enabledPlugins + marketplaces）

启用 **23 个**（来自 13 marketplace：12 GitHub + 1 本地 directory）。`installed_plugins.json` 记 23 条。

### 4.1 启用插件（23）

| 插件 | 来源 marketplace | 用途速记 |
|------|-----------------|----------|
| `claude-code-setup@claude-plugins-official` | 官方 | 自动化推荐 |
| `claude-md-management@claude-plugins-official` | 官方 | CLAUDE.md 维护 |
| `code-review@claude-plugins-official` | 官方 | PR review |
| `code-simplifier@claude-plugins-official` | 官方 | 代码精简 |
| `commit-commands@claude-plugins-official` | 官方 | commit/push/pr |
| `context7@claude-plugins-official` | 官方 | 文档查询 MCP |
| `feature-dev@claude-plugins-official` | 官方 | 特性开发流 |
| `frontend-design@claude-plugins-official` | 官方 | 前端设计 |
| `github@claude-plugins-official` | 官方 | github MCP |
| `playwright@claude-plugins-official` | 官方 | 浏览器自动化 |
| `skill-creator@claude-plugins-official` | 官方 | skill 创建 |
| `superpowers@claude-plugins-official` | 官方 | 流程 skill 集 |
| `andrej-karpathy-skills@karpathy-skills` | karpathy-skills | karpathy 准则 |
| `caveman@caveman` | caveman | caveman 模式 |
| `ecc@ecc` | ecc | ECC 全家桶 |
| `mattpocock-skills@mattpocock` | mattpocock | Matt Pocock skill 集 |
| `ponytail@ponytail` | ponytail | ponytail 模式 |
| `example-skills@anthropic-agent-skills` | anthropic-agent-skills | 示例 skill |
| `open-code-review@open-code-review` | open-code-review | review 工具 |
| `understand-anything@understand-anything` | understand-anything | 知识图谱 |
| `i-have-adhd@i-have-adhd` | i-have-adhd | ADHD 辅助 |
| `better-harness@better-harness` | better-harness | harness 增强 |
| `taste-skill@taste-skill` | taste-skill（本地 directory） | taste 设计 |

### 4.2 marketplaces（`known_marketplaces.json` 13 个）

| marketplace | 来源 |
|-------------|------|
| `claude-plugins-official` | github: anthropics/claude-plugins-official |
| `anthropic-agent-skills` | github: anthropics/skills |
| `mattpocock` | github: mattpocock/skills |
| `ecc` | github: affaan-m/ECC |
| `karpathy-skills` | github: forrestchang/andrej-karpathy-skills |
| `caveman` | github: JuliusBrussee/caveman |
| `ponytail` | github: DietrichGebert/ponytail |
| `open-code-review` | github: alibaba/open-code-review |
| `understand-anything` | github: Egonex-AI/Understand-Anything |
| `i-have-adhd` | github: ayghri/i-have-adhd |
| `better-harness` | github: QoderAI/better-harness |
| `minimalist-entrepreneur` | github: slavingia/skills（marketplace 在，无启用插件） |
| `taste-skill` | **directory: `C:\ZYS\Code\lab-area\taste-skill`**（唯一本地） |

> 注：`settings.json` 的 `extraKnownMarketplaces` 只列 6 个（官方/常用 GitHub 源）；完整 13 个在 `plugins/known_marketplaces.json`。ponytail 是 GitHub（非本地），旧版 checklist 误记为本地 directory。

### 4.3 缓存

| 路径 | 用途 |
|------|------|
| `~/.claude/plugins/plugin-catalog-cache.json` | marketplace 目录缓存 |
| `~/.claude/plugins/marketplaces/` | marketplace 元数据 |
| `~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/` | 已下载插件本体（statusLine 脚本引用 caveman/ponytail 此处） |

---

## 5. Skills（`~/.claude/skills/`）

磁盘 **105 个**（2026-08-08 实测 = 94 真目录 + 11 junction/symlink）；ccswitch db `skills` 表 **186**（db 多 81，含磁盘已删/未同步项）。

构成：
- **自建 26 个**（进 git，`.gitignore` skills/ 白名单 26 行，见 `installing/custom-setup.md`）
- **Matt Pocock junction 11 个**（指向 plugins/cache/mattpocock，启用插件即恢复）
- **第三方真目录 ~68 个**（cc-switch 同步或复制为本体，如 last30days / hallmark / cangjie-skill / 仓颉 first-principles pack 等）

主要分类（约值，精确见 `ls ~/.claude/skills/`）：编码工程 ~23 / 写作 13（自建）/ 学习 7 / 前端设计 ~22 / 平台内容 ~5 / 仓颉 pack ~9 / 元能力及其他 ~26。

> ai-text-polisher 2026-08-08 删除（被 human-writing 替代）；obsidian-vault 2026-08-07 删除。详见 `installing/custom-setup.md`。
> skill 用 cc-switch 单系统管理（memory `skill-mgmt-cc-switch-only`）。

---

## 6. Agents（`~/.claude/agents/`）

磁盘 **25 个** `.md`（2026-08-08 实测；旧值 217 已大幅精简）。按前缀：

| 前缀 | 数量 |
|------|------|
| `engineering-*` | 9 |
| `design-*` | 4 |
| `security-*` | 4 |
| `testing-*` | 8 |

> 另：插件提供的 agent（`ecc:*` / `caveman:cavecrew-*` / `feature-dev:*` / `understand-anything:*` 等）不在本目录，运行时由插件注入。

---

## 7. MCP 服务

**生效中 5 个**（`~/.claude.json` 根 `mcpServers`，与 ccswitch db `mcp_servers` 表一致）。`~/.mcp.json` 为空。

| server | 用途 | 备注 |
|--------|------|------|
| `lean-ctx` | 上下文压缩（ctx_read/ctx_shell/...） | CLAUDE.md 强制优先于原生 |
| `a1b2c3d4-context7-mcp-001` | 文档查询（context7） | 同名插件版 `context7@claude-plugins-official` 也启用，并存 |
| `b2c3d4e5-playwright-mcp-002` | 浏览器自动化 | 同名插件版也启用，并存 |
| `gitnexus` | 代码图谱 / 影响分析 / taint | 配合 gitnexus-exploring skill；command 指 npx 缓存目录，不稳 |
| `cloudcli-browser` | 云端浏览器会话 | npm 全局 `@cloudcli-ai/cloudcli` |

> 旧的 codegraph / github / douyin / headroom 已不在 mcpServers（2026-08-08 实测）。
> 只读 MCP 默认接；写权限走审批。配置命令原文见 `installing/mcp-install.md`。

---

## 8. Memory（`~/.claude/projects/C--Users-zys31/memory/`）

**37 个 `.md`**（2026-08-08 实测；旧值 10）。`MEMORY.md` 为索引，其余为单条记忆。

> 记忆数持续增长（2026-07-03 为 10，2026-08-08 为 37）。记忆 suspect，引用前验证（CLAUDE.md §12）。完整索引见 `MEMORY.md`。

---

## 9. Projects（`~/.claude/projects/`）

- `~/.claude.json` 记录 **59 条** project key（2026-08-08 实测；旧值 35）。
- 磁盘 **36 个** project 目录（旧值 16）。
- **漂移**：59 vs 36，约 23 条陈旧（斜杠/反斜杠重复 / 已删项目 / multica 临时 workdir）。

主要活跃项目（去重后）：

| 路径 | 用途 |
|------|------|
| `C:\Users\zys31` | 主工作目录（本会话） |
| `C:\ZYS\Code\lab-area` | 试验场（CLAUDE.md §0） |
| `C:\ZYS\Code\JavaGuide`（含 interview-guide / open-code-review 子项） | JavaGuide 项目 |
| `C:\ZYS\Code\agent-framework` / `agent-framework-cpp` / `agent-manager`(-server) | agent 框架 |
| `C:\ZYS\Code\wiki` | wiki |
| `C:\ZYS\Code\class\...` | 课程作业 |
| `C:\ZYS\Code\interview-guide`(-by-me) | 面试指南 |
| `C:\ZYS\Code\open-code-review` | OCR 项目 |
| `C:\ZYS\Code\DeepTutor` / `dtsf` / `novel` / `translate` / `pi-java` / `java-code` / `my-code` | 副项目 |
| multica workspaces（6 个 workdir） | multica 临时会话 |
| Open-Design / AionUi namespaces | 第三方平台项目 |

---

## 10. 备份与日志

| 路径 | 内容 | 维护要点 |
|------|------|----------|
| `~/.cc-switch/backups/db_backup_*.db` | 12 份 db 全量备份（2026-06-25 ~ 2026-08-08） | 滚动覆盖前确认最新可开 |
| `~/.cc-switch/backups/cc-switch.db.backup-*` / `cc-switch.db.*` | 早期命名备份 | 可清旧 |
| `~/.cc-switch/backups/sync-backup-*.json` | settings 同步前快照（多份） | 保留最近 3-5 份即可 |
| `~/.cc-switch/backups/hermes/` | hermes 专属备份 | - |
| `~/.cc-switch/backups/matt-fix-*.json` / `matt-key-swap-*.json` | Matt 插件修复/换 key 备份 | - |
| `~/.cc-switch/skill-backups/` | skill 改动前备份 | 滚动 |
| `~/.cc-switch/logs/` | ccswitch 运行日志 | 定期清 |
| `~/.claude/backups/.claude.json.backup.*` | 5 份 .claude.json 备份 | - |
| ccswitch db `proxy_request_logs` | **21729 行**请求计费日志 | 大表，月度归档 |
| ccswitch db `session_log_sync` | 1077 行会话同步偏移 | - |
| ccswitch db `usage_daily_rollups` | 218 行日用量汇总 | 已触发 |

---

## 11. 关键目录结构（`~/.claude/`）

```
.claude/
├── CLAUDE.md                      # 全局规则
├── WORKFLOW_QUICKREF.md           # 速查
├── long-complex-task-prompt.md    # §10 引用
├── settings.json                  # 主配置
├── keybindings.json               # 快捷键
├── agents/      (25 .md)          # 自定义 agent（旧 217，已精简）
├── skills/      (105 目录)        # skill（94 真目录 + 11 junction）
├── hooks/       (9 .py + 状态/脚本) # 自研 7 引用 + 2 死代码 + lean-ctx 脚本
├── statusline/  (4 js + lib/3)    # 自建 statusline（已脱离 ecc）
├── plugins/                       # 插件
│   ├── marketplaces/
│   ├── installed_plugins.json     # 23 插件
│   ├── known_marketplaces.json    # 13 marketplace
│   └── cache/{marketplace}/{plugin}/{version}/
├── external-configs/ (6 文件)     # cc-switch/codex 配置备份
├── installing/ (5 md)             # 装回台账（2026-08-08 盘查刷新）
├── docs/        (3 文件)          # 文档（本文件 + config-inventory 废弃 + opencode 迁移）
└── projects/    (36 目录)         # 会话历史 + memory
    └── C--Users-zys31/memory/ (37 .md)
```

---

## 12. 已识别漂移项

| 项 | 实际 | 应有 | 处理建议 |
|----|------|------|----------|
| Skills 同步 | 磁盘 105 vs ccswitch 186 | 一致 | db 多 81（含已删/未同步），跑 ccswitch skill 同步或核对差项 |
| Projects 陈旧 | claude.json 59 条 vs 磁盘 36 目录 | 去重 | 清理斜杠/反斜杠重复 + 已删项目 + multica 临时 workdir（备份 .claude.json 后） |
| hooks 死代码 | turn_counter.py / learning_nudge.py 未引用 | 删或挂回 | 走 §1 人工确认线 |
| 旧 doc 计数 | config-inventory.md: 134 skills / 21 plugins | 105 / 23 | 已由本文件替代（见废弃说明） |
| `usage_daily_rollups` | 218 行 | 持续汇总 | 已触发，正常 |

---

## 13. 维护节奏建议

| 频率 | 动作 |
|------|------|
| 每次改 settings.json 后 | 跑 skill `cc-switch-setting-sync`（防热切换降级） |
| 周 | 清 ccswitch `logs/`、`backups/` 旧档（留近 5 份） |
| 月 | 归档 `proxy_request_logs`（>50k 行触发）+ 核对 `usage_daily_rollups` |
| 季 | 清理 `~/.claude.json` 陈旧 projects key（先整文件备份） |
| 升级 Claude Code 后 | 核对 env 键名（`CLAUDE_CODE_EXPERIMENTAL_*` 易变）+ hook 事件名 |
| 加装 provider 后 | 验 `provider_health` 写入 + `is_current` 切换正常 |

---

## 14. 文件位置速查（最常用）

| 想改 | 去 |
|------|----|
| 全局规则 | `~/.claude/CLAUDE.md` |
| 模型路由 / effort | `~/.claude/settings.json` -> `env`（`ANTHROPIC_DEFAULT_*_MODEL` + `_NAME`） |
| hook 行为 | `~/.claude/hooks/*.py` + `settings.json` -> `hooks` |
| 启用/禁插件 | `settings.json` -> `enabledPlugins` |
| 加 MCP | ccswitch db `mcp_servers` 或 `~/.claude.json` -> `mcpServers`（命令原文见 `installing/mcp-install.md`） |
| 切 provider | ccswitch（写 `providers.is_current` + 注入 settings.json） |
| 状态栏 | `settings.json` -> `statusLine.command`（入口 `~/.claude/statusline/statusline.js` 自建，拼 caveman + ponytail 插件脚本） |
| 记忆 | `~/.claude/projects/C--Users-zys31/memory/` |
| 装回台账 | `~/.claude/installing/`（5 md，2026-08-08 盘查刷新） |

---

## 废弃说明

`~/.claude/docs/config-inventory.md`（730 行散文版，2026-07-03 前生成）已被本文件替代：
- 旧版计数过时（134 skills / 21 plugins vs 实际 105 / 23）。
- 旧版未覆盖 ccswitch db 全表、根 `~/.claude.json`、漂移项。
- 本文件为单一真相源；旧文件顶部已加跳转。

---

> **2026-08-08 盘查刷新要点**：模型映射全改（opus->glm-5.2 / sonnet->deepseek-v4-pro / haiku->deepseek-v4-flash / fable->kimi-k3）、插件 19->23、marketplace 6->13（ponytail 实为 GitHub 非本地）、skills 144->105、agents 217->25、MCP 8->5、memory 10->37、projects 35->59(磁盘36)、cc-switch 当前 provider GLM->VolcanoArk、hooks 死代码 2 个（turn_counter/learning_nudge）、statusline 已脱离 ecc 为自建。
