# Claude Code 配置总览

> ⚠️ **已废弃（2026-07-03）** — 计数过时（134 skills / 21 plugins vs 实际 144 / 19），
> 且未覆盖 ccswitch db 全表、根 `~/.claude.json`、漂移项。
> **改看 [`config-checklist.md`](./config-checklist.md)**（表格式单一真相源；注意其 2026-08-11 头注：多项亦已过时，权威口径以 `README.md` + `installing/` 台账为准）。
> 本文件保留作历史参考，不再更新。

> 文档生成时间：2026-06-30  
> 范围：`C:\Users\zys31\.claude\`（全局） + 项目级 `~/.claude/CLAUDE.md`  
> 用途：盘点我手头所有配置，便于增减/备份/审计

---

## 0. 全局规则（`~/.claude/CLAUDE.md`）

13 节强约束（用户私有，全局生效）。`docs/config-inventory.md` 是被动盘点文档，**未被 CLAUDE.md、settings.json、hook 任何代码 import/require**；无公共函数/类暴露；纯 markdown 不读写数据文件。

| 节 | 主题 | 关键约束 |
|----|------|----------|
| §0 | 基本约定 | 中文回复；试验场 `C:\ZYS\Code\lab-area`；试验前在根目录建子目录隔离 |
| §1.0 | 项目定位 | 陌生项目首任务前 1-2 行明确角色+意义+目标写 memory |
| §1.1 | 改前 | `git status` 干净才动手；新建分支；改动确认线（≥3 文件先说明）；数据结构先于逻辑；安装位置先问 |
| §1.2 | 改中 | 标杆文件指名；长任务每节落盘；新增外部调用必问失败对策（重试/超时/熔断/降级/限流） |
| §1.3 | 改后 | 跑 lint+test+编译；字段对齐（Spec→Prompt→验收→测试→代码）；AI 坏味道三查（假绿/幻觉引用/幽灵代码）；注释只写 why；**人工确认线**（密钥/迁移/删除/推送/commit）不可自主 |
| §1.4 | AI 代码审查 | 必审无豁免；按 §3 Verify 分级；三维（正确性边界/数据结构选型/代码整洁） |
| §2 | 调试 | DB 错误查保留字；本地 MySQL 失败→SQLite 回退（生产禁） |
| §3 | Agent 调度 | 4-6 切片 + PLAN.md；先串后并；Verify 分级（低/中/高） |
| §4 | 止血 | 不再改→定位→回退（restore/revert/reset）→根因后重做；连续 2-3 轮打转复盘 |
| §5 | 规则管理 | AI 反复犯才入规则；hook 备份 `HOOKS_BACKUP.md` |
| §6 | 决策分层 | 自主 / 询问 / 必须确认；前端默认 `shadcn/ui` |
| §7 | 上下文管理 | 轮次>10 或连续 3 error→提示 /compact；机械改动→开新线程 |
| §8 | MCP | 只读默认接，写权限单独审批；自建 MCP 写 instructions |
| §9 | 平台 | Windows 11；symlink 不行 copy；PYTHONPATH 不设；UTF-8 强制；python312 |
| §10 | 输出完整性 | 禁止占位符/散文敷衍词；长任务激活 `full-output-enforcement` |
| §11 | 通用推理底线 | 先结论后依据；证据优先源码/官方文档/实测；探索性问题 2-3 句给推荐+权衡 |
| §12 | 证据门槛 | 确认性问题先查证据；记忆默认 suspect；不适用：建议/风格/开放讨论 |
| §13 | 交互纪律 | caveman 句型；教程内容不用 caveman；广播意图一句；3+ 步任务 TaskCreate |

> `long-complex-task-prompt.md` 原在 §10 引用；CLAUDE.md 瘦身后已不引用，文件保留手工使用。

---

## 1. Settings（`~/.claude/settings.json`）

### 1.1 模型与代理

```json
{
  "model": "sonnet",
  "effortLevel": "high"  // 环境变量 CLAUDE_CODE_EFFORT_LEVEL=max 覆盖
}
```

| 模型 | 别名 | 备注 |
|------|------|------|
| claude-sonnet-4-6[1M] | `sonnet` | 主模型 |
| claude-opus-4-8[1M] | `opus` | 高强度任务 |
| claude-haiku-4-5 | `haiku` | 轻量 |
| MiniMax-M3[1M] | `fable` | 实际后端映射 |

> **API 走本地代理** `http://127.0.0.1:15721`（`ANTHROPIC_AUTH_TOKEN: PROXY_MANAGED`）。  
> `DISABLE_AUTOUPDATER=1`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`、`ENABLE_TOOL_SEARCH=true`、`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`、`API_TIMEOUT_MS=3000000`（50 分钟）。

### 1.2 启用的插件（21 个，含 2 个未启用，全 user scope）

按 marketplace 归类；同 marketplace 多 plugin 共享同一 owner/repo。

#### A. Anthropic 官方（13 个，2 个 marketplace）

| 插件 | marketplace | owner/repo | 版本 | 路径 | 状态 |
|------|-------------|------------|------|------|------|
| `claude-code-setup@claude-plugins-official` | claude-plugins-official | `anthropics/claude-plugins-official` | 1.0.0 | `plugins/cache/claude-plugins-official/claude-code-setup/1.0.0/` | ✅ |
| `claude-md-management@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | 1.0.0 | `plugins/cache/claude-plugins-official/claude-md-management/1.0.0/` | ✅ |
| `code-review@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/code-review/f9b95ac41584/` | ✅ |
| `code-simplifier@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | 1.0.0 | `plugins/cache/claude-plugins-official/code-simplifier/1.0.0/` | ✅ |
| `commit-commands@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/commit-commands/f9b95ac41584/` | ✅ |
| `context7@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/context7/f9b95ac41584/` | ✅ |
| `feature-dev@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/feature-dev/f9b95ac41584/` | ✅ |
| `frontend-design@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/frontend-design/f9b95ac41584/` | ✅ |
| `github@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/github/f9b95ac41584/` | ✅ |
| `playwright@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/playwright/f9b95ac41584/` | ✅ |
| `skill-creator@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | f9b95ac | `plugins/cache/claude-plugins-official/skill-creator/f9b95ac41584/` | ✅ |
| `superpowers@claude-plugins-official` | 同上 | `anthropics/claude-plugins-official` | 6.0.3 | `plugins/cache/claude-plugins-official/superpowers/6.0.3/` | ✅ |
| `example-skills@anthropic-agent-skills` | anthropic-agent-skills | `anthropics/skills` | 35414756 | `plugins/cache/anthropic-agent-skills/example-skills/35414756ca55/` | ✅ |

#### B. 第三方组织（3 个 marketplace）

| 插件 | marketplace | owner/repo | 版本 | 路径 | 状态 |
|------|-------------|------------|------|------|------|
| `open-code-review@open-code-review` | open-code-review | `alibaba/open-code-review` | 1.0.0 | `plugins/cache/open-code-review/open-code-review/1.0.0/` | ✅ |
| `ecc@ecc` | ecc | `affaan-m/ecc` | 2.0.0 | `plugins/cache/ecc/ecc/2.0.0/` | ✅ |
| `understand-anything@understand-anything` | understand-anything | `Egonex-AI/Understand-Anything` | 2.8.1 | `plugins/cache/understand-anything/understand-anything/2.8.1/` | ✅ |

#### C. 第三方个人（3 个 marketplace）

| 插件 | marketplace | owner/repo | 版本 | 路径 | 状态 |
|------|-------------|------------|------|------|------|
| `caveman@caveman` | caveman | `JuliusBrussee/caveman` | 25d22f8 | `plugins/cache/caveman/caveman/25d22f864ad6/` | ✅ |
| `ponytail@ponytail` | ponytail | `DietrichGebert/ponytail` | 4.8.3 | `plugins/cache/ponytail/ponytail/4.8.3/` | ✅ |
| `andrej-karpathy-skills@karpathy-skills` | karpathy-skills | `forrestchang/andrej-karpathy-skills` | 1.0.0 | `plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/` | ✅ |

#### D. 本地 directory（1 个，非 GitHub）

| 插件 | marketplace | 来源路径 | 版本 | 路径 | 状态 |
|------|-------------|----------|------|------|------|
| `taste-skill@taste-skill` | taste-skill | `C:\ZYS\Code\lab-area\taste-skill` | 1.0.0 | `plugins/cache/taste-skill/taste-skill/1.0.0/` | ⏸ 未启 |

#### E. 已装但未启用（合计 1 个 GitHub 第三方个人）

| 插件 | marketplace | owner/repo | 版本 | 路径 |
|------|-------------|------------|------|------|
| `minimalist-entrepreneur@minimalist-entrepreneur` | minimalist-entrepreneur | `slavingia/skills` | 1.0.0 | `plugins/cache/minimalist-entrepreneur/minimalist-entrepreneur/1.0.0/` |

> §1.2 统计：启用 19（Anthropic 官方 13 / 第三方组织 3 / 第三方个人 3）+ 未启用 2（第三方个人 1 / 本地 1）= 21 plugin / 10 marketplace（9 GitHub + 1 directory）。

**Plugin cache 旧版本残留**（每个 claude-plugins-official 子目录都有）：
- `82f22ec4f0a7/`、`b0aea92dae92/`、`dea48c048bcb/`、`f9b95ac41584/`、**`unknown/`**
- 共 12 个子插件 × 5 版本 ≈ 60 个残留目录，**磁盘浪费但不影响功能**
- 清理：`plugins/cache/claude-plugins-official/*/unknown/` 全删（`unknown/` 是被替换前的版本快照）
- 其他插件 cache 单版本（karpathy/caveman/ecc/ponytail/open-code-review/anthropic-agent-skills/understand-anything/minimalist-entrepreneur/taste-skill）

### 1.3 Hooks（11 块，6 类事件）

所有脚本统一用 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`。

| 事件 | Matcher | 脚本 | 作用 |
|------|---------|------|------|
| **PreToolUse** | `Bash\|shell\|shell_command\|exec\|exec_command\|local_shell\|run\|terminal` | `git_guard.py` | 拦破坏性命令（`rm -rf`/`git reset --hard`/`git push -f`/`git branch -D`/`git clean -f`/`DROP TABLE`/`curl|sh`/`chmod -R 777`/`npm publish`/`>/dev/sdX`/`--no-verify`/`--no-gpg-sign`）；commit/push/checkout -b 需用户确认 |
| **PreToolUse** | 同上 | `secret_guard.py` | Pre: 命令命中 `.env`/`id_rsa`/`credentials.json` 等机密文件路径 → deny；Post: stdout 命中 `sk-`/`AKIA`/`ghp_`/`xox*`/`AIza`/`BEGIN PRIVATE KEY` → 告警 |
| **PreToolUse** | 同上 | `dep_gate.py` | 拦 pip/npm/yarn/cargo/go get/gem/composer/brew/apt 等新增依赖 → deny |
| **PreToolUse** | `Edit\|Write\|MultiEdit\|NotebookEdit\|apply_patch\|update\|str_replace_based_edit_tool\|file_edit` | `placeholder_guard.py` | 写入内容含 TODO/FIXME/HACK/XXX/NotImplementedError/省略/for brevity/其余同理/占位符 → deny（.md/.txt 文档豁免） |
| **PreToolUse** | 同上 | `edited_tracker.py` | Pre: 累计 ≥3 文件提醒确认线；Post: 写状态到 `edited_state.json` |
| **PreToolUse** | `Bash\|bash\|PowerShell\|powershell` | `lean-ctx.exe hook rewrite` | 自动重写命令走 lean-ctx 压缩版 |
| **PreToolUse** | `Read\|read\|ReadFile\|read_file\|View\|view\|Grep\|grep\|Search\|search\|ListFiles\|list_files\|ListDirectory\|list_directory` | `lean-ctx.exe hook redirect` | 重定向到 lean-ctx ctx_read/ctx_search/ctx_tree |
| **PostToolUse** | `Bash\|shell\|...` | `secret_guard.py` | 见上 |
| **PostToolUse** | 同上 | `verify_recorder.py` | 40+ 验证命令模式（pytest/jest/vitest/tsc/npm test/ruff/mypy/eslint/cargo test/xcodebuild/...）→ 写 `edited_state.json.last_verify_ts/verify_cmds` |
| **PostToolUse** | `Edit\|...` | `edited_tracker.py` | 写状态 |
| **PostToolUse** | `.*` | `lean-ctx.exe hook observe` | 观察 |
| **PreCompact** | `.*` | `lean-ctx.exe hook observe` | 观察 |
| **SessionStart** | `.*` | `edited_tracker.py` | 重置 state |
| **SessionStart** | `.*` | `lean-ctx.exe hook observe` | 观察 |
| **SessionEnd** | `.*` | `lean-ctx.exe hook observe` | 观察 |
| **Stop** | `.*` | `verify_gate.py` | 有代码改动且 `last_edit_ts > last_verify_ts` → block（exit 2），拦 ≥3 次自动放行防死循环 |
| **Stop** | `.*` | `lean-ctx.exe hook observe` | 观察 |
| **UserPromptSubmit** | `.*` | `turn_counter.py` | 轮次 ≥20 → 提示 /compact |
| **UserPromptSubmit** | `.*` | `lean-ctx.exe hook observe` | 观察 |

**未挂载但存在的脚本**：
- `rtk_prefix.py` — auto-prefix `rtk` 到支持的命令（Codex 风，参考性备份）
- `lean-ctx-redirect.sh` / `lean-ctx-rewrite.sh` — lean-ctx hook 的 shell 版本（被 .exe 替代）
- `lean-ctx-redirect-native` / `lean-ctx-rewrite-native` — 无扩展名的 lean-ctx native binary（Windows 原生重写/重定向器）
- `gitnexus/` — gitnexus 自带 hook 子目录（含 5 文件：`gitnexus-hook.cjs`/`hook-db-lock-probe.cjs`/`hook-lock.cjs`/`resolve-analyze-cmd.cjs`/`win-rm-list-json.ps1`），未在 settings.json 挂载
- `gitnexus-cli/skill-creator/feature-dev` 等 plugin 也带 hooks（`hooks/hooks.json`），但走 plugin 自动加载机制

**Plugin data 子目录**（`plugins/data/<plugin>-<marketplace>/state/`）：
- caveman / context7 / ecc / playwright / ponytail / superpowers / understand-anything 各有 `state/` 目录
- 存 plugin 自身状态（与 hooks 的 `*_state.json` 分开）

**状态文件**：
- `edited_state.json` — `{session_id, paths[], edits_per_path{}, last_edit_ts, last_verify_ts, verify_cmds[], stop_blocks}`
- `turn_state.json` — `{session_id, count}`
- `debug.log` — hook heartbeat 记录

**备份**：`HOOKS_BACKUP.md` 写明 Codex 迁回步骤（7 脚本清单 + 工具名兼容性 + 契约适配）+ 16 用例自检记录。

### 1.4 StatusLine

```bash
ECC=$(node ".../ecc/ecc/2.0.0/scripts/hooks/ecc-statusline.js" 2>/dev/null); \
CAVE=$(powershell ... ".../caveman/caveman/25d22f864ad6/src/hooks/caveman-statusline.ps1" 2>/dev/null); \
PONY=$(powershell ... ".../ponytail/ponytail/4.8.3/hooks/ponytail-statusline.ps1" 2>/dev/null); \
echo "$ECC $CAVE $PONY"
```

拼接三段：ecc 状态条 + caveman 模式条 + ponytail 模式条。

### 1.5 权限（permissions.allow）

只放开 lean-ctx MCP 的 12 个工具：

| 工具 | 用途 |
|------|------|
| `mcp__lean-ctx__ctx_read` | 读文件（10 mode + 压缩缓存） |
| `mcp__lean-ctx__ctx_search` | 模式搜索（压缩结果） |
| `mcp__lean-ctx__ctx_tree` | 目录树（压缩版） |
| `mcp__lean-ctx__ctx_overview` | 项目概览 |
| `mcp__lean-ctx__ctx_plan` | 计划 |
| `mcp__lean-ctx__ctx_metrics` | 指标 |
| `mcp__lean-ctx__ctx_compress` | 压缩 |
| `mcp__lean-ctx__ctx_session` | 会话状态 |
| `mcp__lean-ctx__ctx_knowledge` | 知识图谱 |
| `mcp__lean-ctx__ctx_graph` | 图查询 |
| `mcp__lean-ctx__ctx_retrieve` | 检索 |
| `mcp__lean-ctx__ctx_provider` | provider 信息 |

> 其他 MCP（context7 / playwright / douyin / gitnexus / codegraph / chrome-devtools）未在 allow 列表里，每次调用需审批。

### 1.6 settings.local.json

```json
{ "enabledMcpjsonServers": [] }
```

> 空——所有 MCP 走 settings.json 显式注册或 plugin config 加载。

---

## 2. 实际加载的 MCP（settings 外）

| MCP server | 状态 | 工具数/能力 |
|------------|------|------------|
| `a1b2c3d4-context7-mcp-001` | ✅ | `resolve-library-id` / `query-docs`（拉库文档） |
| `b2c3d4e5-playwright-mcp-002` | ✅ | 浏览器自动化 20+ 工具 |
| `codegraph` | ⚠️ 未索引 | 工作区无 `.codegraph/`，本会话不可用 |
| `douyin` | ✅ | `parse_douyin_video_info` / `extract_douyin_text` / `get_douyin_download_link` / `recognize_audio_*` |
| `gitnexus` | ✅ | 知识图谱 + PDG（`query`/`impact`/`api_impact`/`explain`/`trace`/`pdg_query`/`route_map` 等 17+ 工具） |
| `lean-ctx` | ✅ | 12 工具（见 §1.5）+ 76 内部能力 |
| `plugin:context7:context7` | ✅ | context7 文档查询 |
| `plugin:ecc:chrome-devtools` | ✅ | Chrome DevTools（lighthouse/performance/snapshot/screenshot 等） |

---

## 3. Skills（`~/.claude/skills/` — 134 个）

按主题分类。`name :: 用途` 格式。

### 3.1 编码与工程实践（25）

| Skill | 用途 |
|-------|------|
| tdd | TDD 红绿重构循环，集成风格测试 |
| test-driven-development | 测试驱动开发实施 |
| debugging-and-error-recovery | 系统性根因调试 |
| code-review-and-quality | 多轴代码审查 |
| code-simplification | 简化代码不改行为 |
| refactor / request-refactor-plan | 重构计划（带 GitHub issue 落地） |
| ci-cd-and-automation | CI/CD 管道自动化 |
| security-and-hardening | 加固代码（输入校验/认证/存储/外部集成） |
| observability-and-instrumentation | 日志/指标/追踪/告警 |
| performance-optimization | 性能优化 |
| git-workflow-and-versioning | Git 工作流与版本管理 |
| git-guardrails-claude-code | Codex git 危险命令拦截 |
| setup-pre-commit | Husky + lint-staged + tsc + test |
| setup-matt-pocock-skills | `## Agent skills` 块写 AGENTS.md |
| migrate-to-shoehorn | `as` 类型断言 → @total-typescript/shoehorn |
| scaffold-exercises | 习题目录脚手架 |
| spec-driven-development | 编码前先 spec |
| source-driven-development | 官方文档引用驱动实现 |
| planning-and-task-breakdown | 拆解为可执行任务 |
| incremental-implementation | 增量交付（多文件改动） |
| full-output-enforcement | 禁止截断/占位符 |
| ubiquitous-language | DDD 通用语言提取 |
| documentation-and-adrs | ADR 与文档 |
| deprecation-and-migration | 弃用与迁移 |
| doubt-driven-development | 高风险决策对抗审查 |

### 3.2 内容创作与润色（15）

| Skill | 用途 |
|-------|------|
| article-writer | 深度文章创作（通用 + JavaGuide 模式） |
| article-writing-guide | 文章写作总路由 |
| edit-article | 编辑改进文章 |
| tech-article-review | 技术文章结构化评审 |
| review-doc | 4 Agent 并行技术文章审校 |
| multi-review-pipeline | 多 Agent 并行文档审查（合成去重） |
| publish-final-check | 发布前强制终检（4 子项） |
| plagiarism-audit | 对照外部来源审查抄袭/高仿 |
| ai-text-polisher | 中文技术文章去 AI 味 |
| humanizer-zh | 去除文本 AI 生成痕迹（维基指南） |
| shuorenhua | 检查清理中英文 AI 套路 |
| de-ai-orchestrator | 去 AI 味编排（按档位串 humanizer/shuorenhua/polisher） |
| writing-shape / writing-beats / writing-fragments | 写作工艺：分形/节拍/碎片 |
| javaguide-style-guide | JavaGuide docs/ai 风格判定源（MUST/SHOULD checklist） |
| chinese-markdown-normalizer | 中文 Markdown 规范化 |

### 3.3 教程与学习（8）

| Skill | 用途 |
|-------|------|
| tutorial-maker | Markdown 系列教程生成器（from-zero 自审门） |
| cram-engine | 期末速成（认知负荷+检索练习） |
| lesson-svg-diagram | 课程 HTML 配图升级为 SVG |
| markdown-viewer | Markdown 富图表/可视化 |
| interview-me | 一问一答深挖真实需求 |
| interview-java-backend | Java 后端模拟面试 |
| interview-ai-agent-dev | AI Agent 开发模拟面试 |
| ruthless-review | 阶段精通 + 苏格拉底挖 + teach-back 验证 |

### 3.4 AI 资讯与研究（5）

| Skill | 用途 |
|-------|------|
| aihot | 中文 AI 资讯查询（aihot.virxact.com） |
| last30days | 30 天内多平台（Reddit/X/YT/TT/HN/Polymarket/GH） |
| agent-reach | 17 平台 CLI/MCP/curl/Python（小红书/抖音/B 站/微博/Twitter/V2EX/Reddit/LinkedIn/GH/网页/公众号/RSS/YouTube/播客） |
| hv-analysis | 横纵深度研究（卡兹克） |
| doc-finder | 当前仓库 .md 全面查找 |
| answer-evidence-finder | 文章中提取引用片段 |
| hyperframes | （已在设计类列出） |

### 3.5 设计/前端/UI（15）

| Skill | 用途 |
|-------|------|
| design-taste-frontend | Anti-slop 前端（landing/portfolio/redesign） |
| design-taste-frontend-v1 | v1 兼容版 |
| high-end-visual-design | 高级设计感教学（字体/阴影/卡片/动画） |
| impeccable | 设计/改/审/抛光/优化前端 |
| minimalist-ui | 干净编辑风界面 |
| industrial-brutalist-ui | 工业粗野（瑞士印刷+军用终端） |
| stitch-design-taste | Google Stitch 语义设计系统 |
| frontend-ui-engineering | 生产级 UI 构建 |
| imagegen-frontend-web | 网站设计参考图生成 |
| imagegen-frontend-mobile | 移动端原生屏概念图 |
| image-to-code | 图像→代码（先生成图再分析再实现） |
| gpt-taste | UX/UI + GSAP 动效（AIDA + 字体严格） |
| brandkit | 品牌指南板/logo/视觉世界 |
| design-an-interface | 多 Agent 并行设计多个接口方案 |
| apikey-image-gen | Hermes Web UI 图像生成 |
| grok-image-to-video | 图像→视频（xAI Grok Imagine） |
| hyperframes | AI 视频（HTML/CSS/JS 合成→MP4） |
| hatch-pet | 动画宠物/精灵图生成 |
| remotion | React+Remotion 可编辑视频 |
| ppt-master | 多格式 SVG 内容生成→PPTX |
| drawio-chart | Draw.io 图表（流程/架构/时序/ER） |
| drawio-article-illustration | 文章配图决策与验证 |

### 3.6 平台发布与笔记（8）

| Skill | 用途 |
|-------|------|
| content-to-note | 公众号/B 站/抖音链接→结构化 MD 笔记 |
| bili-note | B 站视频+opus/article→MD 笔记 |
| douyin-video-summary | 抖音视频→whisper.cpp 转录+结构化摘要 |
| multi-platform-publisher | 知乎/小红书/CSDN/B 站/公众号/掘金 一键分发 |
| obsidian-vault | Obsidian vault 增删改查（`C:\ZYS\Code\wiki`） |
| cc-switch-setting-sync | Codex config.toml 同步进 ccswitch DB |
| storage-analyzer | macOS/Windows 只读存储分析 |
| shipping-and-launch | 生产发布 checklist |

### 3.7 Skill 元能力（6）

| Skill | 用途 |
|-------|------|
| ai-coding-guide | 用哪个 skill/插件/工具 + 配合（中文触发） |
| find-skills | 发现并安装 skill |
| using-agent-skills | 会话启动时发现/调用 skill（meta-skill） |
| skill-creator | 从 git 历史生成 SKILL.md |
| darwin-skill | skill 自动优化（SkillLens 9 维 + SkillOpt 验证门 + 盲评） |
| darwin-weekly-audit | 周期体检（基线评估） |

### 3.8 GitNexus 工具集（9）

| Skill | 用途 |
|-------|------|
| gitnexus-cli | CLI 索引/分析/wiki |
| gitnexus-guide | GitNexus 自身介绍 |
| gitnexus-exploring | 代码理解/架构追踪 |
| gitnexus-debugging | bug 追踪 |
| gitnexus-impact-analysis | 改动影响分析 |
| gitnexus-pr-review | PR 评审 |
| gitnexus-refactoring | 安全重构 |
| gitnexus-taint-analysis | CFG/taint/PDG 污点分析 |
| gitnexus-pdg-query | PDG 控制/数据依赖查询 |

### 3.9 Understand-Anything 工具集（9）

| Skill | 用途 |
|-------|------|
| understand | 仓库→交互式知识图谱 |
| understand-chat | 代码问答 |
| understand-dashboard | 交互式 Web 仪表板 |
| understand-diff | git diff/PR 分析 |
| understand-domain | 业务领域提取→领域流图 |
| understand-explain | 文件/函数/模块深读 |
| understand-knowledge | LLM wiki 知识库→图谱 |
| understand-onboard | 新人 onboarding 指南 |
| understand-dashboard | 仪表板 |

### 3.10 上下文/调试/质量（5）

| Skill | 用途 |
|-------|------|
| context-engineering | agent 上下文配置 |
| context-management | 上下文饱和分层压缩 |
| neat-freak | 会话结束知识清理（OCD 级） |
| qa | 交互式 QA（报 bug→GitHub issue） |
| review | 与固定点（commit/branch/tag/merge-base）以来的改动做双轴审查 |

### 3.11 其他（10）

- `api-and-interface-design`：稳定 API/接口设计
- `to-issues` / `to-prd` / `triage`：计划→GitHub issues / 当前上下文→PRD / 状态机 triage
- `qiaomu-ai-prd`：从一行想法生成 AI 可实现 PRD
- `playwright`：终端自动化浏览器
- `browser-testing-with-devtools`：Chrome DevTools MCP 浏览器测试
- `karpathy-guidelines`：编码行为准则（避过度复杂/小变更/假设/可验证成功标准）
- `zoom-out`：让 agent 拉远看更高层
- `learned` / `teach`：自创 skill 索引？
- `idea-refine`：结构化发散-收敛打磨概念
- `grill-me` / `grill-with-docs`：苏格拉底压力测试计划/对文档/领域模型

> 完整列表见 `~/.claude/skills/*/SKILL.md`（134 项）。

---

## 4. Agents（`~/.claude/agents/` — 217 个）

按命名空间分组。**所有 agent 共享同一种 frontmatter**：`name` / `description` / `color` / `emoji` / `vibe` / `tools`。

### 4.1 engineering-*（32）

| Agent | 定位 |
|-------|------|
| AI Data Remediation Engineer | 自愈数据管道（air-gapped SLM + 语义聚类） |
| AI Engineer | ML 模型开发部署 |
| Autonomous Optimization Architect | API 性能 shadow-test + 财务/安全护栏 |
| Backend Architect | 后端架构/DB/API/云 |
| CMS Developer | Drupal/WordPress 主题+插件 |
| Code Reviewer | 构造性可执行反馈 |
| Codebase Onboarding Engineer | 熟悉陌生代码库 |
| Data Engineer | 可靠数据管道（lakehouse/Spark/dbt/流） |
| Database Optimizer | schema/query/index/性能（PG/MySQL/Supabase） |
| DevOps Automator | 基础设施自动化 + CI/CD |
| Drupal Shopping Cart Engineer | Drupal Commerce |
| Email Intelligence Engineer | 邮件→结构化数据 |
| Embedded Firmware Engineer | 裸机/RTOS（ESP32/STM32/nRF/FreeRTOS） |
| Feishu Integration Developer | 飞书开放平台全套 |
| Filament Optimization Specialist | Filament PHP 后台重构 |
| Frontend Developer | 现代 Web（React/Vue/Angular） |
| Git Workflow Master | 高级 Git 工作流（rebase/worktree/CI） |
| Incident Response Commander | 生产事故指挥 |
| IT Service Manager | ITIL 4 |
| Minimal Change Engineer | 最小可行 diff（拒范围蔓延） |
| Mobile App Builder | iOS/Android/跨端 |
| Multi-Agent Systems Architect | 多 agent 管道架构 |
| OrgScript Engineer | OrgScript 语法/AST/业务逻辑 |
| Prompt Engineer | LLM prompt 制作与优化 |
| Rapid Prototyper | 超快 PoC/MVP |
| Senior Developer | 高级实现（Laravel/Livewire/FluxUI/CSS/Three.js） |
| Software Architect | 系统设计/DDD/架构模式 |
| Solidity Smart Contract Engineer | EVM 智能合约/gas/可升级 |
| SRE | SLO/error budget/可观测/混沌 |
| Technical Writer | 开发者文档/API/README |
| Voice AI Integration Engineer | Whisper/云 ASR 全管道 |
| WeChat Mini Program Developer | 微信小程序全套 |
| WordPress Shopping Cart Engineer | WooCommerce |

### 4.2 marketing-*（35）

按地区/平台分：

**国内（17）**：
- AEO Foundations Architect / Agentic Search Optimizer / AI Citation Strategist（AEO/GEO）
- Baidu SEO Specialist / Bilibili Content Strategist / China E-Commerce Operator
- China Market Localization Strategist / Douyin Strategist / Kuaishou Strategist
- Livestream Commerce Coach / Private Domain Operator / WeChat Official Account Manager
- Weibo Strategist / Xiaohongshu Specialist / Zhihu Strategist
- Carousel Growth Engine（抖音/IG 轮播自动生成+发布+学习循环）

**海外（10）**：
- App Store Optimizer / Cross-Border E-Commerce Specialist / Global Podcast Strategist
- Instagram Curator / LinkedIn Content Creator / Reddit Community Builder
- Short-Video Editing Coach / TikTok Strategist / Twitter Engager
- X/Twitter Intelligence Analyst

**通用营销（8）**：
- Book Co-Author / Content Creator / Email Marketing Strategist
- Growth Hacker / Multi-Platform Publisher（中文一键分发）/ Podcast Strategist
- PR & Communications Manager / SEO Specialist / Social Media Strategist
- Video Optimization Specialist

### 4.3 sales-*（11）

Account Strategist / Sales Coach / Sales Data Extraction Agent / Deal Strategist / Discovery Coach / Sales Engineer / Offer & Lead Gen Strategist / Outbound Strategist / Sales Outreach / Pipeline Analyst / Proposal Strategist

### 4.4 security-*（10）

Application Security Engineer / Security Architect / Blockchain Security Auditor / Cloud Security Architect / Compliance Auditor / Incident Responder / Penetration Tester / Senior SecOps Engineer / Threat Detection Engineer / Threat Intelligence Analyst

### 4.5 design-*（9）

Brand Guardian / Image Prompt Engineer / Inclusive Visuals Specialist / Persona Walkthrough Specialist / UI Designer / UX Architect / UX Researcher / Visual Storyteller / Whimsy Injector

### 4.6 testing-*（8）

Accessibility Auditor / API Tester / Evidence Collector（截图强迫症，默认找 3-5 问题）/ Performance Benchmarker / Reality Checker（默认 NEEDS WORK）/ Test Results Analyzer / Tool Evaluator / Workflow Optimizer

### 4.7 gis-*（13）

3D & Scene Developer（Cesium/ArcGIS）/ GIS Analyst / BIM/GIS Specialist / Cartography Designer / Drone/Reality Mapping / GeoAI/ML Engineer / Geoprocessing Specialist / GIS QA Engineer / Solution Engineer / Spatial Data Engineer / Spatial Data Scientist / Technical Consultant / Web GIS Developer

### 4.8 finance-*（5）

Bookkeeper & Controller / Financial Analyst / FP&A Analyst / Investment Researcher / Tax Strategist

### 4.9 legal-*（3）

Billing & Time Tracking / Client Intake / Document Review

### 4.10 healthcare-*（2）

Customer Service / Marketing Compliance Specialist

### 4.11 product-*（5）

Behavioral Nudge Engine / Feedback Synthesizer / Product Manager / Sprint Prioritizer / Trend Researcher

### 4.12 project-management-*（7）

Experiment Tracker / Jira Workflow Steward / Meeting Notes Specialist / Project Shepherd / Studio Operations / Studio Producer

**无前缀**：
- `project-manager-senior.md` — Senior Project Manager（spec→task + 记忆历史项目）

### 4.13 support-*（6）

Analytics Reporter / Executive Summary Generator / Finance Tracker / Infrastructure Maintainer / Legal Compliance Checker / Support Responder

### 4.14 paid-media-*（7）

Paid Media Auditor / Ad Creative Strategist / Paid Social Strategist / PPC Campaign Strategist / Programmatic & Display Buyer / Search Query Analyst / Tracking & Measurement Specialist

### 4.15 academic-*（5）

Anthropologist / Geographer / Historian / Narratologist / Psychologist

### 4.16 specialized-*（13）

Chief of Staff / Civil Engineer（多国规范）/ Cultural Intelligence Strategist / Developer Advocate / Document Generator（PDF/PPTX/DOCX/XLSX）/ French Consulting Market Navigator / Korean Business Navigator / MCP Builder / Model QA Specialist / Pricing Analyst / Salesforce Architect / Strategy Duel Agent（36 计博弈）/ Workflow Architect

### 4.17 xr-*（3）

XR Cockpit Interaction Specialist / XR Immersive Developer / XR Interface Architect

### 4.18 game-*（3）

Game Audio Engineer / Game Designer / Level Designer

### 4.19 narrative-*（1）

Narrative Designer

### 4.20 其他无前缀（25+）

| Agent | 定位 |
|-------|------|
| accounts-payable-agent | 跨支付通道（加密/法币/稳定币） |
| agentic-identity-trust | agent 身份与信任系统 |
| agents-orchestrator | 自主流水线（leader of process） |
| change-management-consultant | ADKAR/Kotter/Prosci 变革管理 |
| chief-financial-officer | 资本配置/财务规划/M&A |
| corporate-training-designer | 企业培训体系设计 |
| customer-service | 通用客服 |
| customer-success-manager | 售后续约/扩展 |
| data-consolidation-agent | 销售数据合并入实时仪表板 |
| data-privacy-officer | GDPR/CCPA/全球隐私 |
| esg-sustainability-officer | ESG/可持续/碳中和 |
| government-digital-presales-consultant | ToG 政企数字转型（信创/等保） |
| grant-writer | 资助申请（联邦/基金会） |
| healthcare-customer-service | 医疗客服（同情心） |
| hospitality-guest-services | 酒店餐饮服务 |
| hr-onboarding | 入职全流程 |
| identity-graph-operator | 共享身份图 |
| language-translator | 西/英实时翻译（场景化） |
| loan-officer-assistant | 贷款/抵押全流程 |
| lsp-index-engineer | LSP 客户端编排+语义索引 |
| ma-integration-manager | M&A 后整合（D1/100天/协同） |
| macos-spatial-metal-engineer | 原生 Swift + Metal/Vision Pro |
| medical-billing-coding-specialist | ICD-10/CPT/HCPCS 编码 |
| operations-manager | Lean/Six Sigma 流程优化 |
| organizational-psychologist | 组织心理/心理安全/倦怠 |
| personal-growth-mentor | 跨域个人发展（无激励废话） |
| real-estate-buyer-seller | 房产买卖 |
| recruitment-specialist | 招聘运营+中国平台+劳动法 |
| report-distribution-agent | 销售报告按地域分发 |
| retail-customer-returns | 零售退货/换货/退款 |
| supply-chain-strategist | 供应链/采购战略 |
| study-abroad-advisor | 美/英/加/澳/欧/港/新 留学 |
| technical-artist | Art→Engine 流水线（shader/VFX/LOD） |
| terminal-integration-specialist | 终端仿真+SwiftTerm |
| visionos-spatial-engineer | visionOS 空间计算/Liquid Glass |
| zk-steward | Zettelkasten 知识库管家（Luhmann 风） |

> 完整列表见 `~/.claude/agents/*.md`（217 项）。

---

## 5. 关键目录结构

```
~/.claude/
├── CLAUDE.md                 # 全局规则（13 节）
├── long-complex-task-prompt.md
├── settings.json             # 主配置（含 extraKnownMarketplaces 6 个）
├── settings.local.json       # 局部（空 MCP）
├── settings.json.bak         # 备份
├── settings.json.bak-hooks-rewrite
├── config.json               # {"primaryApiKey":"any"}
├── keybindings.json          # 自定义键位（ctrl+j / shift+enter）
├── .local/                   # 用户私有配置（gitignored）
├── .caveman-active           # caveman 运行时标记
├── .caveman-active.*         # 历史 pid 文件
├── .ponytail-active          # ponytail 运行时标记
├── .last-cleanup             # 上次清理时间戳
├── .last-update-result.json  # 上次升级结果
├── agents/                   # 217 agent .md
├── skills/                   # 134 skill 目录（每个含 SKILL.md）
├── hooks/                    # 9 hook 脚本 + 状态文件 + gitnexus 子目录
├── plugins/
│   ├── installed_plugins.json
│   ├── known_marketplaces.json
│   ├── plugin-catalog-cache.json
│   ├── cache/                # 实际安装（部分含 unknown/ 旧版残留）
│   ├── data/                 # plugin 自身状态（7 个 plugin 各有 state/）
│   └── marketplaces/         # 源仓库
├── projects/                 # 15 项目目录（4 个有 memory/）
├── teams/                    # 8 session 残留
├── docs/                     # 文档（含 superpowers/{plans,specs}/）
│   ├── superpowers/
│   │   ├── plans/            # superpowers plan 落盘（gitignored）
│   │   └── specs/            # superpowers spec 落盘（gitignored）
│   └── config-inventory.md   # 本文件
├── backups/                  # 备份
├── file-history/             # 文件历史
├── session-data/             # 会话数据
├── session-env/              # 会话环境
├── sessions/                 # 8 个 session
├── plans/                    # plan 落盘
├── tasks/                    # 任务
├── jobs/                     # 任务/作业
├── paste-cache/              # 粘贴缓存
├── cache/                    # 通用缓存
├── metrics/                  # 指标
├── telemetry/                # 埋点
├── shell-snapshots/          # shell 快照
├── ide/                      # IDE 集成
├── daemon/                   # 后台进程（含 status/lock）
├── daemon.log / daemon.lock / daemon.status.json
├── bash-commands.log         # bash 调用日志
├── cost-tracker.log          # 成本追踪
├── history.jsonl             # 历史
├── mcp-health-cache.json     # MCP 健康检查缓存
```

---

## 6. Memory（`~/.claude/projects/C--Users-zys31/memory/`）

索引 `MEMORY.md` + 3 条记忆：

| 文件 | 类型 | 主题 |
|------|------|------|
| `MEMORY.md` | 索引 | 三条记忆指针 |
| `tutorial-content-no-caveman.md` | feedback | 教程/学习/教学不用 caveman 压缩 |
| `user-solo-founder-china.md` | user | 一人公司主攻国内；优先国内平台，跳过出海 |
| `skill-mgmt-cc-switch-only.md` | feedback | Skill 管理只用 cc-switch；别引入 agent-skills CLI 跨工具同步 |

---

## 7. Projects（15 个）

| 目录 | 含义 |
|------|------|
| `C--Users-zys31` | 当前用户主目录会话（**含 memory/**：3 条记忆 + MEMORY.md） |
| `C--Users-zys31--claude` | .claude 配置会话 |
| `C--Users-zys31-AppData-Roaming-Open-Design-namespaces-release-stable-win-data-projects-brand-github-000408` | Open Design 关联项目（brand-github） |
| `C--Users-zys31-AppData-Roaming-Open-Design-namespaces-release-stable-win-data-projects-brand-javaguide-b786bf` | Open Design 关联项目（brand-javaguide） |
| `C--ZYS-Code-agent-framework` | agent-framework 项目（含 memory/） |
| `C--ZYS-Code-class-----` | class 项目（多连字符，含 memory/） |
| `C--ZYS-Code-lab-area` | **试验场**（CLAUDE.md §0 指定，含 memory/） |
| `C--ZYS-Code-wiki` | Obsidian vault |
| `C--ZYS-Download-usage-data-2026-6` | 用量数据下载 |
| `C--ZYS-Software-Open-Design-resources-app-prebundled` | Open Design resources 预捆绑 |
| `C--ZYS-class-----` | 课程（多个类似） |
| `C--ZYS-class--------` | 课程（多个类似） |
| `C--ZYS-class-----------tutorial` | 课程（多个类似） |
| `C--ZYS-class-----------tutorial-----` | 课程（多个类似） |
| `C--ZYS-demo` | demo 项目 |

> 4 个项目目录含 `memory/`：user / agent-framework / class / lab-area

---

## 8. 备份与日志

| 路径 | 用途 |
|------|------|
| `backups/` | 备份目录 |
| `settings.json.bak` | settings 旧版 |
| `settings.json.bak-hooks-rewrite` | hook 重写前备份 |
| `bash-commands.log` | bash 命令日志 |
| `cost-tracker.log` | 成本追踪 |
| `telemetry/` | 埋点 |
| `daemon.log` | daemon 进程日志 |
| `hooks/debug.log` | hook heartbeat |
| `history.jsonl` | 会话历史 |

---

## 9. 维护建议

1. **未启用插件**：minimalist-entrepreneur、taste-skill 已装但未启用，按需开。
2. **daemon 在跑**：后台进程持续开销，确认是否需要（`daemon.status.json` 可看状态）。
3. **hook 链长**：PreToolUse 同时跑 git_guard/secret_guard/dep_gate/edited_tracker 4 个 Python 脚本 + lean-ctx redirect/rewrite，观察性能影响。
4. **skill 134 个** + **agent 217 个**：远超日常使用，多数处于"按需加载"状态。定期清无用 skill 减少启动期注入 token。
5. **statusLine 3 拼接**：node + powershell + powershell，每次刷新都 spawn 进程，慢的话可合成单脚本。
6. **API_TIMEOUT_MS=3000000（50 分钟）**：极少情况需要，多数任务可在 5 分钟内完成。
7. **代理 `127.0.0.1:15721`**：本地代理需保持运行，否则 Claude Code 无法启动。
8. **Plugin cache 旧版本残留**：claude-plugins-official 12 子目录 × 5 版本（含 unknown/）≈ 60 目录闲置磁盘，清理 `plugins/cache/claude-plugins-official/*/unknown/` 即可回收。
9. **ECC 2.0.0 实际载荷大**：含 67 agents + 92 commands + 224 skills + 32 docs + 42 scripts，启用即注入显著启动 token；按需触发而非全量。
10. **MCP context7 双存在**：裸 `a1b2c3d4-context7-mcp-001` 与命名空间 `plugin:context7:context7` 同时加载，工具重复；选其一保留即可。
11. **`.local/` 已 gitignored**：用户私有配置存放点，目前空目录，未来放 secret/API key/个性化脚本。
12. **plugin data state/**：7 个 plugin 在 `plugins/data/*/state/` 有独立状态目录，与 hooks 的 `*_state.json` 不互通，调试时按 plugin 路径找。

---

## 10. 文件位置速查

| 想看什么 | 文件 |
|----------|------|
| 启用哪些 plugin | `settings.json` → `enabledPlugins` |
| 已知 marketplace 源 | `settings.json` → `extraKnownMarketplaces` + `plugins/known_marketplaces.json` |
| 启用哪些 MCP | `settings.json` → `permissions.allow` + 实际 MCP server list |
| hook 触发逻辑 | `hooks/*.py` + `HOOKS_BACKUP.md` |
| 已知 marketplace | `plugins/known_marketplaces.json` |
| 已装 plugin 路径 | `plugins/installed_plugins.json` |
| 键位绑定 | `keybindings.json` |
| 私有配置 | `.local/`（gitignored） |
| skill 用途 | `skills/<name>/SKILL.md`（首行 description） |
| agent 用途 | `agents/<name>.md`（frontmatter description） |
| 全局规则 | `CLAUDE.md` |
| 长期记忆 | `projects/<dir>/memory/MEMORY.md` + 各 .md |
| 备份 | `backups/` + `settings.json.bak*` |
