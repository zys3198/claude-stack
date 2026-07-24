# Claude Code 配置清单表（速查 · 全量）

> 生成日期：2026-07-03 ｜ 扫描方式：实盘 `~/.claude/` + `~/.claude.json` + `~/.cc-switch/cc-switch.db`
> 列约定：`路径 / 对象` · `用途` · `状态 / 计数` · `维护要点`
> **替代** 旧的 `config-inventory.md`（散文版，计数已过时，见文末「废弃说明」）。

---

## 0. 顶层配置文件（机器级）

| 路径 | 用途 | 状态 / 计数 | 维护要点 |
|------|------|-------------|----------|
| `~/.claude/CLAUDE.md` | 全局规则（13 节 + caveman/lean-ctx 段） | 活跃，本会话指令源 | 改前走 §5 GateGuard 声明 |
| `~/.claude/settings.json` | 主配置：env/permissions/hooks/statusLine/plugins | 见 §1 | 改完同步 ccswitch（§3）防热切换降级 |
| `~/.claude/settings.local.json` | 本机覆盖（不入库） | 未扫到独立项 | secrets 放这，别进 `settings.json` |
| `~/.claude/keybindings.json` | 快捷键绑定 | 存在 | — |
| `~/.claude/WORKFLOW_QUICKREF.md` | 工作流速查 | 存在 | — |
| `~/.claude/long-complex-task-prompt.md` | 长复杂任务 prompt（§10 引用） | 存在 | — |
| `~/.claude.json` | Claude Code 根状态（99 KB） | 35 projects / 8 mcpServers / 44 顶层键 | 见 §7 / §9；含 `userID` `machineID` |
| `~/.mcp.json` | 用户级 MCP（独立于 settings） | **0 servers（空）** | 实际 MCP 走 `~/.claude.json` 根 + ccswitch db |
| `~/.claude/.claude.json`（项目级） | claude 自身目录的 project 配置 | 存在（属 §9 的 35 条之一） | — |

---

## 1. settings.json 内部（`~/.claude/settings.json`）

### 1.1 env（模型与代理路由）

| 键 | 值 | 用途 | 维护要点 |
|----|----|------|----------|
| `ANTHROPIC_AUTH_TOKEN` | `PROXY_MANAGED` | 占位，真实 token 由 ccswitch 代理注入 | 别手填真值 |
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:15721` | 走 ccswitch 本地代理 | 与 ccswitch `proxy_config.listen_port=15721` 对齐 |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | `glm-5.2[1M]` | Fable 5 路由到 GLM-5.2 | 切 provider 时同步改 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-opus-4-8[1M]` | Opus 路由 | 名义 claude，经代理映射到 GLM-5.1（见 ccswitch provider meta） |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `claude-sonnet-4-6[1M]` | Sonnet 路由 → GLM-5 | 同上 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `claude-haiku-4-5` | Haiku 路由 → GLM-5 | 同上 |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | 推理强度 | — |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | 实验特性：agent teams | 升级后可能改名，留意 |
| `ENABLE_TOOL_SEARCH` | `true` | 延迟工具加载（本会话生效） | — |

### 1.2 行为开关

| 键 | 值 | 说明 |
|----|----|------|
| `model` | `opus` | 默认档位 |
| `effortLevel` | `high` | settings 内 effort（与 env `max` 共存） |
| `includeCoAuthoredBy` | `false` | commit 不加 Co-authored-by |
| `attribution.commit` / `attribution.pr` | `""` | 空，配合上一条 |

### 1.3 permissions.allow

| 对象 | 用途 |
|------|------|
| `mcp__lean-ctx__ctx_read` | 免确认读 |
| `mcp__lean-ctx__ctx_search` | 免确认搜 |
| `mcp__lean-ctx__ctx_tree` | 免确认树 |
| `mcp__lean-ctx__ctx_overview` / `ctx_plan` / `ctx_metrics` / `ctx_compress` / `ctx_session` / `ctx_knowledge` / `ctx_graph` / `ctx_retrieve` / `ctx_provider` | lean-ctx 其余免确认 |

> 写类工具（ctx_edit / ctx_shell）**未**进 allow，仍走确认。

---

## 2. Hooks（settings.hooks）

事件 7 类 × 多 matcher。Python 解释器固定 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`。lean-ctx 用 `~/.cargo/bin/lean-ctx.exe`。

### 2.1 自研 Python hooks（`~/.claude/hooks/`）

| 文件 | 触发事件 | matcher | 用途 |
|------|----------|---------|------|
| `git_guard.py` | PreToolUse | `Bash\|shell...` | 拦危险 git（rm -rf / DROP / force push 等） |
| `secret_guard.py` | PreToolUse **且** PostToolUse | shell 类 | 拦密钥外泄（20+ 模式） |
| `dep_gate.py` | PreToolUse | shell 类 | Fact-Forcing Gate（拦截非代码 Edit/Write） |
| `placeholder_guard.py` | PreToolUse | Edit/Write 类 | 拦占位符（TODO / `...` / `for brevity`） |
| `edited_tracker.py` | PreToolUse **且** PostToolUse **且** SessionStart | Edit/Write + 全局 | 追踪改动文件 |
| `verify_recorder.py` | PostToolUse | shell 类 | 记录验证命令执行 |
| `verify_gate.py` | Stop | `.*` | 收尾验收闸 |
| `turn_counter.py` | UserPromptSubmit | `.*` | 轮次计数（>10 提示压缩） |
| `HOOKS_BACKUP.md` | — | — | hook 清单备份说明 |

### 2.2 lean-ctx 内置 hook（同一可执行文件，不同子命令）

| 子命令 | 事件 | matcher | 作用 |
|-------|------|---------|------|
| `hook observe` | SessionStart / UserPromptSubmit / PreCompact / SessionEnd / Stop / PostToolUse(`.*`) | `.*` | 会话观测，建索引 |
| `hook rewrite` | PreToolUse | `Bash\|bash\|PowerShell` | shell 压缩重写 |
| `hook redirect` | PreToolUse | `Read\|Grep\|Search\|List*` | 把原生 Read/Grep 重定向到 ctx_* |

### 2.3 备份与脚本

| 路径 | 用途 |
|------|------|
| `~/.claude/hooks/HOOKS_BACKUP.md` | hook 备份文档 |
| `~/.claude/hooks/lean-ctx-redirect.sh` / `lean-ctx-redirect-native` | 重定向脚本（双形态） |
| `~/.claude/hooks/lean-ctx-rewrite.sh` / `lean-ctx-rewrite-native` | 重写脚本 |

---

## 3. cc-switch（`~/.cc-switch/`）— provider 单一真相源

数据库 `cc-switch.db`（sqlite，17 表）。当前 claude provider = **Zhipu GLM**（`is_current=1`，健康）。

### 3.1 核心表

| 表 | 行数 | 用途 | 维护要点 |
|----|------|------|----------|
| `providers` | 14 | 多 provider 配置（claude/claude-desktop/codex/gemini/hermes） | 含 **真实 API key**，备份勿外传 |
| `provider_endpoints` | 10 | 每 provider 的 endpoint URL | — |
| `mcp_servers` | 8 | MCP 服务定义（跨工具同步源） | 与 `~/.claude.json` root mcpServers 对齐 |
| `skills` | **132** | 跨工具 skill 注册 | 磁盘 144，**12 个未同步**（漂移） |
| `skill_repos` | 7 | skill 仓库源 | — |
| `prompts` | 1 | 自定义 prompt | — |
| `settings` | 7 | ccswitch 自身设置（KV） | 含 `common_config_claude`（§3.3） |
| `proxy_config` | 3 | claude/codex/gemini 代理设置 | claude: `127.0.0.1:15721` enabled |
| `provider_health` | 1 | 健康检查（仅 GLM 当前记录） | healthy=1 |
| `proxy_request_logs` | **23241** | 每次请求计费/延迟日志 | 大表，定期归档 |
| `model_pricing` | 163 | 计费表 | 升级模型时更新 |
| `stream_check_logs` | 1 | 流式探活 | — |
| `proxy_live_backup` | 1 | 热切换前备份 | `live_takeover_active=0` |
| `session_log_sync` | 783 | 会话日志同步偏移 | — |
| `usage_daily_rollups` | 0 | 日用量汇总（未触发） | — |

### 3.2 providers 全量（14 个）

| name | app_type | category | is_current | endpoint |
|------|----------|----------|------------|----------|
| Zhipu GLM | claude | cn_official | **✅ 1** | open.bigmodel.cn/api/anthropic |
| DeepSeek | claude | cn_official | 0 | api.deepseek.com/anthropic |
| MiniMax | claude | cn_official | 0 | api.minimaxi.com/anthropic |
| Kimi For Coding | claude | cn_official | 0 | api.kimi.com/coding |
| OpenCode Go | claude | third_party | 0 | opencode.ai/zen/go |
| Codex | claude | third_party | 0 | chatgpt.com/backend-api/codex |
| Zhipu GLM | claude-desktop | cn_official | 1 | open.bigmodel.cn/api/anthropic |
| OpenCode Go | claude-desktop | third_party | 0 | opencode.ai/zen/go |
| Codex | claude-desktop | third_party | 0 | chatgpt.com/backend-api/codex |
| Claude Desktop Official | claude-desktop | official | 0 | claude.ai/download |
| OpenAI Official | codex | official | 0 | chatgpt.com/codex |
| OpenCode | codex | — | **1（codex 当前）** | opencode.ai/zen/go/v1 |
| deepseek | hermes | — | 0 | api.deepseek.com |
| Google Official | gemini | official | 0 | ai.google.dev |

> 国内订阅主线（claude app_type）：GLM(主) / DeepSeek / MiniMax / Kimi，与 memory `user-solo-founder-china` 一致。
> **secrets 全在 `providers.settings_config`**（GLM/MiniMax/Kimi/codex-oauth token），备份/分享前必须脱敏。

### 3.3 ccswitch 设置同步

| 路径 / 对象 | 用途 | 维护要点 |
|-------------|------|----------|
| `~/.cc-switch/settings.json` | ccswitch 写回 claude settings.json 的模板 | 改 claude 配置后跑 skill `cc-switch-setting-sync` |
| `settings` 表 `common_config_claude` | 公共配置（防 provider 切换降级） | 同上 |
| `~/.cc-switch/BACKUP_BEFORE_CHANGE.md` | 改前备份说明 | — |
| `~/.cc-switch/RESTORE_SYMLINKS.md` | 符号链接恢复说明 | Windows symlink 常失败，按 CLAUDE.md §9 copy 不 symlink |
| `~/.cc-switch/codex_oauth_auth.json` | codex oauth 凭据 | secret |
| `~/.cc-switch/copilot_auth.json` | copilot 凭据 | secret |

---

## 4. 插件（enabledPlugins + marketplaces）

启用 **19 个**（来自 6 marketplace + 1 本地）。

### 4.1 启用插件

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
| `superpowers@claude-plugins-official` | 官方 | 流程 skill 集（brainstorming/debugging/etc） |
| `andrej-karpathy-skills@karpathy-skills` | karpathy-skills | karpathy 准则 |
| `caveman@caveman` | caveman | caveman 模式（本会话生效） |
| `ecc@ecc` | ecc | ECC 全家桶（hook/agent/build/review） |
| `ponytail@ponytail` | ponytail（本地 directory） | ponytail 模式（本会话生效） |
| `example-skills@anthropic-agent-skills` | anthropic-agent-skills | 示例 skill |
| `open-code-review@open-code-review` | open-code-review | review 工具 |
| `understand-anything@understand-anything` | understand-anything | 知识图谱 |

### 4.2 marketplaces（`extraKnownMarketplaces`）

| marketplace | 来源 repo |
|-------------|-----------|
| `claude-plugins-official` | anthropics/claude-plugins-official |
| `anthropic-agent-skills` | anthropics/skills |
| `caveman` | JuliusBrussee/caveman |
| `ecc` | affaan-m/ECC |
| `karpathy-skills` | forrestchang/andrej-karpathy-skills |
| `understand-anything` | Egonex-AI/Understand-Anything |

> ponytail = 本地 directory marketplace（非 GitHub）。

### 4.3 缓存

| 路径 | 用途 |
|------|------|
| `~/.claude/plugins/plugin-catalog-cache.json` | marketplace 目录缓存 |
| `~/.claude/plugins/marketplaces/` | marketplace 元数据（空目录标记） |
| `~/.claude/plugins/cache/{ecc,caveman,ponytail}/...` | 已下载插件本体（statusLine 脚本引用此处） |

---

## 5. Skills（`~/.claude/skills/`）

磁盘 **144 个**（ccswitch db 注册 132，**12 个未同步**）。

按职能分组（沿用旧 doc 分类，计数已刷新）：

| 类别 | 数量（约） | 代表 skill |
|------|-----------|-----------|
| 编码与工程实践 | ~25 | tdd / debugging-and-error-recovery / api-and-interface-design / code-review-and-quality / git-workflow-and-versioning |
| 内容创作与润色 | ~15 | article-writer / ai-text-polisher / humanizer-zh / chinese-markdown-normalizer / de-ai-orchestrator |
| 教程与学习 | ~8 | tutorial-maker / cram-engine / interview-java-backend / ruthless-review |
| AI 资讯与研究 | ~5 | last30days / aihot / hv-analysis |
| 设计 / 前端 / UI | ~15 | frontend-ui-engineering / drawio-chart / high-end-visual-design / industrial-brutalist-ui / minimalist-ui |
| 平台发布与笔记 | ~8 | content-to-note / bili-note / douyin-video-summary / publish-final-check |
| Skill 元能力 | ~6 | using-agent-skills / writing-great-skills / nuwa-skill / darwin-skill / find-skills |
| GitNexus 工具集 | ~9 | gitnexus-cli / -exploring / -debugging / -pr-review / -impact-analysis / -taint-analysis |
| Understand-Anything 工具集 | ~9 | understand / -onboard / -explain / -domain / -knowledge / -dashboard |
| 上下文 / 调试 / 质量 | ~5 | context-management / context-engineering / lean-ctx / neat-freak / impeccable |
| 其他 | ~30+ | storage-analyzer / apikey-image-gen / obsidian-vault / plagiarism-audit / karpathy-guidelines 等 |

> 精确清单见 `ls ~/.claude/skills/`。skill 用 cc-switch 单系统管理（memory `skill-mgmt-cc-switch-only`）。

---

## 6. Agents（`~/.claude/agents/`）

磁盘 **217 个** `.md`。按前缀分类（沿用旧 doc）：

| 前缀 | 数量（约） |
|------|-----------|
| `engineering-*` | 32 |
| `marketing-*` | 35 |
| `sales-*` | 11 |
| `security-*` | 10 |
| `design-*` | 9 |
| `testing-*` | 8 |
| `gis-*` | 13 |
| `finance-*` | 5 |
| `legal-*` | 3 |
| `healthcare-*` | 2 |
| `product-*` | 5 |
| `project-management-*` | 7 |
| `support-*` | 6 |
| `paid-media-*` | 7 |
| `academic-*` | 5 |
| `specialized-*` | 13 |
| `xr-*` / `game-*` / `narrative-*` | 7 |
| 无前缀（data-/identity-/zk- 等） | ~30 |

> 另：插件提供的 agent（`ecc:*` / `caveman:cavecrew-*` / `feature-dev:*` / `understand-anything:*` / `claude-code-guide` 等）不在本目录，运行时由插件注入（见会话开头 agent 列表）。

---

## 7. MCP 服务

**生效中 8 个**（来自 `~/.claude.json` 根 `mcpServers`，与 ccswitch db `mcp_servers` 表一致）。`~/.mcp.json` 为空。

| server | 用途 | 备注 |
|--------|------|------|
| `lean-ctx` | 上下文压缩（ctx_read/ctx_shell/...） | CLAUDE.md 强制优先于原生 |
| `codegraph` | 代码图谱索引 | 当前未索引（会话提示无 `.codegraph/`） |
| `gitnexus` | 代码图谱 / 影响分析 / taint | 配合 gitnexus-* skills |
| `a1b2c3d4-context7-mcp-001` | 文档查询（context7） | 别名 mcp__plugin_context7_context7 |
| `b2c3d4e5-playwright-mcp-002` | 浏览器自动化 | — |
| `c3d4e5f6-github-mcp-003` | github 操作 | 含 issue/PR 写权限 |
| `douyin` | 抖音视频解析 / ASR | — |
| `headroom` | （用途见 db `server_config`） | — |

> 只读 MCP 默认接；写权限（github PR / douyin 下载）走审批。

---

## 8. Memory（`~/.claude/projects/C--Users-zys31/memory/`）

**10 文件**（9 条记忆 + `MEMORY.md` 索引）。

| 文件 | 类型 | 摘要 |
|------|------|------|
| `MEMORY.md` | 索引 | 一行一条指针 |
| `user-solo-founder-china.md` | user | 一人公司 / 国内市场 |
| `tutorial-content-no-caveman.md` | feedback | 教程内容不用 caveman |
| `skill-mgmt-cc-switch-only.md` | feedback | skill 走 cc-switch 单系统 |
| `lean-ctx-bashenv-fix.md` | feedback | lean-ctx hook 已修复（2026-07-01） |
| `lean-ctx-bashenv-fix-tempworkaround.md` | feedback | 旧绕法，已废弃 |
| `user-prefer-official-approach.md` | user | 偏好官方做法 |
| `evidence-over-meta-guides.md` | feedback | 生态比较看一手证据 |
| `skill-ecosystem-choice-2026-07.md` | project | skill 选型（Matt Pocock + Superpowers） |
| `constraint-adherence-over-approx.md` | feedback | 约束超标偏好精简 |

> 记忆 suspect，引用前验证（CLAUDE.md §12）。

---

## 9. Projects（`~/.claude/projects/`）

- `~/.claude.json` 记录 **35 条** project key（含 `C:/...` 与 `C:\...` 同路径重复，如 JavaGuide 出现 3 次）。
- 磁盘 **16 个** project 目录。
- **漂移：~19 条陈旧**（旧路径 / 斜杠反斜杠重复 / 已删项目）。

主要活跃项目（去重后）：

| 路径 | 用途 |
|------|------|
| `C:\Users\zys31` | 主工作目录（本会话） |
| `C:\ZYS\Code\lab-area` | 试验场（CLAUDE.md §0） |
| `C:\ZYS\Code\JavaGuide` | JavaGuide 项目 |
| `C:\ZYS\Code\agent-framework` | agent 框架 |
| `C:\ZYS\Code\wiki` | wiki |
| `C:\ZYS\Code\class\...` | 课程作业（campus-dining / 人工智能 / 数据库 / 计组） |
| `C:\ZYS\Code\Agent-Learning-Hub` / `Backend-Learning-Hub` | 学习 hub |
| `C:\ZYS\Code\interview-guide` / `open-code-review` / `open-note-book` / `cc-connect-by-myself` | 副项目 |
| `C:\ZYS\Download\usage_data_2026_6` | 用量数据 |
| Open-Design namespaces（brand-github / brand-javaguide） | Open-Design 平台项目 |

---

## 10. 备份与日志

| 路径 | 内容 | 维护要点 |
|------|------|----------|
| `~/.cc-switch/backups/db_backup_*.db` | 8 份 db 全量备份（2026-06-25 ~ 2026-07-03） | 滚动覆盖前确认最新可开 |
| `~/.cc-switch/backups/cc-switch.db.backup-*` | 早期命名备份 | 可清旧 |
| `~/.cc-switch/backups/sync-backup-*.json` | settings 同步前快照（多份） | 保留最近 3-5 份即可 |
| `~/.cc-switch/backups/hermes/` | hermes 专属备份 | — |
| `~/.cc-switch/skill-backups/` | skill 改动前备份（last30days/find-skills/douyin-video-summary/claude-md-audit 等） | 滚动 |
| `~/.cc-switch/sync-backup-20260625_223814.json` | 顶层同步备份 | — |
| `~/.cc-switch/logs/` | ccswitch 运行日志 | 定期清 |
| ccswitch db `proxy_request_logs` | **23241 行**请求计费日志 | 大表，考虑月度归档 |
| ccswitch db `session_log_sync` | 783 行会话同步偏移 | — |

---

## 11. 关键目录结构（`~/.claude/`）

```
.claude/
├── CLAUDE.md                      # 全局规则
├── WORKFLOW_QUICKREF.md           # 速查
├── long-complex-task-prompt.md    # §10 引用
├── settings.json                  # 主配置
├── keybindings.json               # 快捷键
├── agents/      (217 .md)         # 自定义 agent
├── skills/      (144 目录)        # skill
├── hooks/       (13 文件)         # 自研 + lean-ctx
│   ├── statusline/  (空)
│   └── gitnexus/    (空)
├── plugins/                       # 插件
│   ├── marketplaces/  (空)
│   ├── plugin-catalog-cache.json
│   └── cache/{ecc,caveman,ponytail}/
├── ide/         (空)              # IDE 集成
├── lib/                           # 库
│   └── awesome-design-md/  (空)
├── docs/        (1 文件)          # 文档
│   └── config-inventory.md        # ← 旧版，已废弃见下
└── projects/    (16 目录)         # 会话历史 + memory
    └── C--Users-zys31/memory/ (10 文件)
```

---

## 12. 已识别漂移项（需处理）

| 项 | 实际 | 应有 | 处理建议 |
|----|------|------|----------|
| Skills 同步 | 磁盘 144 vs ccswitch 132 | 一致 | 跑 ccswitch skill 同步，或核对 12 个差项是否该入 db |
| Projects 陈旧 | claude.json 35 条 vs 磁盘 16 目录 | 去重 | 清理斜杠/反斜杠重复 + 已删项目（备份 .claude.json 后） |
| 旧 doc 计数 | config-inventory.md: 134 skills / 21 plugins | 144 / 19 | 已由本文件替代（见下） |
| claude.json 体积 | 99 KB | — | 大量 `tipsHistory`/`projects` 历史；可周期性瘦身 |
| `usage_daily_rollups` | 0 行 | 由 `proxy_request_logs`(23241) 汇总 | 触发一次 rollup 任务 |

---

## 13. 维护节奏建议

| 频率 | 动作 |
|------|------|
| 每次改 settings.json 后 | 跑 skill `cc-switch-setting-sync`（防热切换降级） |
| 周 | 清 ccswitch `logs/`、`backups/` 旧档（留近 5 份） |
| 月 | 归档 `proxy_request_logs`（>50k 行触发）+ 触发 `usage_daily_rollups` |
| 季 | 清理 `~/.claude.json` 陈旧 projects key（先整文件备份） |
| 升级 Claude Code 后 | 核对 env 键名（`CLAUDE_CODE_EXPERIMENTAL_*` 易变）+ hook 事件名 |
| 加装 provider 后 | 验 `provider_health` 写入 + `is_current` 切换正常 |

---

## 14. 文件位置速查（最常用）

| 想改 | 去 |
|------|----|
| 全局规则 | `~/.claude/CLAUDE.md` |
| 模型路由 / effort | `~/.claude/settings.json` → `env` |
| hook 行为 | `~/.claude/hooks/*.py` + `settings.json` → `hooks` |
| 启用/禁插件 | `settings.json` → `enabledPlugins` |
| 加 MCP | ccswitch db `mcp_servers` 或 `~/.claude.json` → `mcpServers` |
| 切 provider | ccswitch（写 `providers.is_current` + 注入 settings.json） |
| 状态栏 | `settings.json` → `statusLine.command`（拼 ECC + caveman + ponytail） |
| 记忆 | `~/.claude/projects/C--Users-zys31/memory/` |

---

## 废弃说明

`~/.claude/docs/config-inventory.md`（730 行散文版，2026-07-03 前生成）已被本文件替代：
- 旧版计数过时（134 skills / 21 plugins vs 实际 144 / 19）。
- 旧版未覆盖 ccswitch db 全表、根 `~/.claude.json`、漂移项。
- 本文件为单一真相源；旧文件顶部已加跳转。
