# opencode 迁移计划（PLAN.md）

> 生成：2026-07-03 ｜ 基于：opencode 官方文档 + awesome-opencode 生态 + 用户 4 项决策
> 配置基线见 [`config-checklist.md`](./config-checklist.md)

---

## 0. 决策基线（用户已答）

| Q | 决策 |
|---|------|
| Q1 Plugins | 查每个官方描述，opencode 有等价的装；无的弃 |
| Q2 Hooks | 自定义（8 个自研 Python）→ opencode 补；插件自带（ecc/caveman/ponytail/lean-ctx）→ 不补 |
| Q3 lean-ctx | 按 lean-ctx 原生安装方式，opencode 侧接 MCP |
| Q4 Scope | **全迁**：opencode 主力，Claude Code 备份 |

---

## 1. 现状基线（迁移起点）

| 类别 | 当前 Claude Code 侧 |
|------|-------------------|
| Provider | ccswitch 代理 `127.0.0.1:15721`，GLM/DeepSeek/MiniMax/Kimi/Codex/OpenCode 全在 db |
| 全局规则 | `~/.claude/CLAUDE.md`（13 节 + caveman/lean-ctx 段） |
| Skills | `~/.claude/skills/`（144 个） |
| Agents | `~/.claude/agents/`（217 个 `.md`） |
| MCP | `~/.claude.json` mcpServers（8 个：lean-ctx/codegraph/gitnexus/context7/playwright/github/douyin/headroom） |
| 自研 Hooks | `~/.claude/hooks/*.py`（8 个 Python） |
| 插件 | enabledPlugins（19 个） |
| Keybindings | `~/.claude/keybindings.json` |
| Memory | `~/.claude/projects/C--Users-zys31/memory/`（10 文件） |

---

## 2. opencode 关键事实（决策依据）

来源：opencode.ai/docs + awesome-opencode GitHub

| 能力 | opencode 支持 |
|------|--------------|
| **Claude Code 兼容回退** | `~/.claude/CLAUDE.md`（无 AGENTS.md 时直读）、`~/.claude/skills/`（原生读） |
| 配置 | `~/.config/opencode/opencode.json`（全局） + 项目 `opencode.json` |
| Agent | JSON：`mode`(primary/subagent)/`model`/`prompt`/`permission` |
| MCP | `mcp`：local(command[]) / remote(url) |
| Plugin | npm `plugin: ["pkg"]`（Bun 自动装，缓存在 `~/.cache/opencode/node_modules/`）；或本地 `~/.config/opencode/plugins/`、`.opencode/plugins/` |
| Skill 权限 | `permission.skill`：`*`/`pr-review`/`internal-*` → allow/deny/ask |
| Rules | `AGENTS.md` 或 `instructions: [...]` glob |
| Hook 事件 | `tool.execute.before/after`、`file.edited`、`session.idle`、`session.created`、`message.updated`、`tui.prompt.append`、`permission.asked`、`shell.env`、`experimental.session.compacting`（**无 CC 的 PreToolUse/Stop 命名，语义可映射**） |
| Keybindings | `~/.config/opencode/tui.json`（键名体系不同） |
| StatusLine | 无原生 statusLine 配置（靠 plugin / TUI） |

---

## Phase 0 — 基线就绪（零成本）

| 步骤 | 动作 | 验收 |
|------|------|------|
| 0.1 | 装 opencode：`curl -fsSL https://opencode.ai/install \| bash`（Windows 用 download 页二进制） | `opencode --version` 出来 |
| 0.2 | ccswitch 切到 opencode app（db 已有 `OpenCode` provider，`is_current=1` codex 侧；claude app 侧有 `OpenCode Go`） | ccswitch UI 切到 opencode，settings.json 注入正常 |
| 0.3 | 装 **CCS OpenCode Sync** plugin（`JasonLandbridge/opencode-ccs-sync`）：自动把 ccswitch provider 同步进 opencode.json | 改 ccswitch 后 opencode.json 自动更新 |

> npm 包名待查 repo README 确认（部分 awesome 条目未标 npm 名）。

---

## Phase 1 — opencode 原生回退（零成本）

| 项 | 动作 | 说明 |
|----|------|------|
| 1.1 全局规则 | **不动**。opencode 无 `~/.config/opencode/AGENTS.md` 时自动读 `~/.claude/CLAUDE.md` | 13 节规则全继承 |
| 1.2 Skills | **不动**。opencode 原生读 `~/.claude/skills/`（144 个） | 配 `permission.skill: {"*":"allow"}` |
| 1.3 Memory | 装 **OpenCode Claude Memory** plugin（`kuitos/opencode-claude-memory`）：CC 兼容路径共享 markdown memory | 两边 memory 互通 |

---

## Phase 2 — 配置转换

| 项 | 源 | 目标 | 工作 |
|----|----|------|------|
| 2.1 MCP（8 个） | `~/.claude.json` mcpServers | `opencode.json` → `mcp`（local command[] / remote url） | 逐个转，多数 local 类型直接搬 command 数组 |
| 2.2 Agents（217 个） | `~/.claude/agents/*.md` frontmatter | `opencode.json` → `agent`（JSON） | **写批量转换脚本**：frontmatter → JSON，`mode` 默认 `subagent`，`prompt` 取 body |
| 2.3 Keybindings | `~/.claude/keybindings.json` | `~/.config/opencode/tui.json` | 键名对表重映射（opencode 用 `leader`/`session_*`/`input_*` 等） |
| 2.4 AGENTS.md（可选覆盖） | — | 若要 opencode 专属规则，建 `~/.config/opencode/AGENTS.md` | 否则走 CLAUDE.md 回退 |

---

## Phase 3 — 插件安装（Q1：19 plugins 映射）

### 3.1 MCP 类（直接走 opencode MCP）

| CC 插件 | opencode 处置 |
|---------|--------------|
| `context7` | opencode.json `mcp.context7` = remote `https://mcp.context7.com/mcp` ✅ |
| `playwright` | opencode MCP（local）**或** `OpenCode Chromium Browser Plugin`（`DJOCKER-FACE/opencode-chromium-browser-plugin`） |
| `github` | opencode MCP（local，与现有一致） |

### 3.2 skill 已在 ~/.claude/skills/（opencode 直读，功能保留）

| CC 插件 | 处置 |
|---------|------|
| `andrej-karpathy-skills` | skill 在 skills/，opencode 直读 ✅ |
| `superpowers` | brainstorming/debugging/writing-plans 等 skill 若在 skills/ → 直读；**plugin 自带的调度逻辑丢**（接受） |
| `ecc` 部分 skill | skills/ 里的直读；hook 链丢 |

### 3.3 有 opencode 等价（装 plugin）

| CC 插件 | opencode 替代 | repo |
|---------|--------------|------|
| `code-review` + `open-code-review` | **opencode-review** | `sun-praise/opencode-review` |
| `frontend-design` | **TypeUI** | `bergside/typeui` |
| `skill-creator` | **Openskills** 或 **Manage Skills** | `numman-ali/openskills` / `Randofrids-Dojo/ManageSkills` |
| `commit-commands`（release 部分） | **GitHub Release** | `amestsanntim/opencode-github-release` |
| `feature-dev`（subagent 流） | **Oh My Opencode** 含 Claude Code 兼容层 + agents | `code-yeongyu/oh-my-opencode` |

### 3.4 无 opencode 等价（弃，Q1 接受）

| CC 插件 | 处置 |
|---------|------|
| `claude-code-setup` | 弃（CC 专属 statusline 推荐） |
| `claude-md-management` | 走 AGENTS.md 原生 + 手动维护（无 plugin） |
| `code-simplifier` | 弃 |
| `example-skills` | 弃（示例） |
| `caveman` | 弃。mode 注入功能部分由 **opencode-personality**（`joostvanwollingen/opencode-personality`）替代，但不是 caveman 风格 |
| `ponytail` | 弃（无等价） |
| `understand-anything` | 查其 repo 是否支持 opencode；否则弃 |

### 3.5 新增（opencode 生态补强）

| plugin | 替代 CC 侧什么 | repo |
|--------|--------------|------|
| **CC Safety Net** | `git_guard.py` | `kenryu42/claude-code-safety-net` |
| **Envsitter Guard** | secret_guard 的 .env 拦截部分 | `boxpositron/envsitter-guard` |
| **Opencode Log Sanitizer** | secret_guard 的输出脱敏部分 | `errhythm/opencode-log-sanitizer` |
| **CCS OpenCode Sync** | 手动同步 provider | `JasonLandbridge/opencode-ccs-sync` |
| **OpenCode Claude Memory** | memory 跨工具 | `kuitos/opencode-claude-memory` |

> Phase 4 的自研 hook 重写后，CC Safety Net / Log Sanitizer / Envsitter 可作冗余兜底或二选一。

---

## Phase 4 — Hook 迁移（Q2：8 自研 Python → TS plugin）

8 个全是自定义（`~/.claude/hooks/*.py`），按 Q2 全部 port 到 opencode TS plugin。

### 4.1 事件映射

| Python hook | CC 事件 | opencode 事件 | 处置 |
|-------------|---------|--------------|------|
| `secret_guard.py` | PreToolUse + PostToolUse (shell) | `tool.execute.before` + `tool.execute.after`（tool=bash） | port TS：扫 `sk-`/`AKIA`/`ghp_`/`xox*`/`AIza`/`BEGIN PRIVATE KEY` + 拦 `.env`/`id_rsa`/`credentials.json` 路径 |
| `git_guard.py` | PreToolUse (shell) | `tool.execute.before`（tool=bash） | port TS：拦 `rm -rf`/`git reset --hard`/`git push -f`/`git branch -D`/`git clean -f`/`DROP TABLE`/`curl\|sh`/`chmod -R 777`/`npm publish`/`--no-verify`；或装 **CC Safety Net** 替代 |
| `dep_gate.py` | PreToolUse (shell) | `tool.execute.before`（tool=bash） | port TS：拦 `pip`/`npm`/`yarn`/`cargo`/`go get`/`gem`/`composer`/`brew`/`apt` |
| `placeholder_guard.py` | PreToolUse (Edit/Write) | `tool.execute.before`（tool=write/edit） | port TS：拦 `TODO`/`FIXME`/`HACK`/`XXX`/`NotImplementedError`/`for brevity`/`...` 占位 |
| `verify_gate.py` | Stop | `session.idle` | port TS：有改动且未验证 → block（设阈值防死循环） |
| `edited_tracker.py` | PreToolUse + PostToolUse + SessionStart | `file.edited` + `session.created` | port TS：累计 ≥3 文件提醒确认线 |
| `verify_recorder.py` | PostToolUse (shell) | `tool.execute.after`（tool=bash） | port TS：识别 pytest/jest/tsc/ruff/mypy/eslint/cargo test 等 → 记 `last_verify_ts` |
| `turn_counter.py` | UserPromptSubmit | `message.updated` 或 `tui.prompt.append` | port TS：轮次 ≥20 → 提示 `/compact`（opencode: `session_compact` keybind） |

### 4.2 实施方式

- 单 plugin 文件合并：`~/.config/opencode/plugins/zys-guards.ts`，导出所有 hook
- 或每 hook 一个 plugin（更清晰，便于开关）
- TypeScript，`import type { Plugin } from "@opencode-ai/plugin"`
- 状态文件迁移：`edited_state.json` / `turn_state.json` 逻辑用 opencode `client.app.log()` + 本地 json

### 4.3 插件自带 hook（不补，Q2 逻辑）

| 来源 | hook | 处置 |
|------|------|------|
| `ecc` | git_guard/secret_guard/verify_gate/dep_gate/placeholder_guard 等 | 若装回 ecc 的 opencode 版则自带；无则靠 Phase 4 自研覆盖 |
| `caveman` / `ponytail` | statusline + mode 注入 | 无 opencode 版 → **功能丢失**（接受） |
| `lean-ctx` | observe/rewrite/redirect | 无 opencode 版 → 见 Phase 5 |

> **关键**：`Opencode Hooks Plugin`（`remain325/opencode-hooks-plugin`）声称「用 CC hook 定义接到 opencode」。但你的 hook 是 Python 命令式，非 CC 标准 hook 格式，**不一定直接吃**。先验证；不行就走 4.1 的 TS port。

---

## Phase 5 — lean-ctx（Q3：原生安装方式）

| 步骤 | 动作 |
|------|------|
| 5.1 | lean-ctx 已装（`~/.cargo/bin/lean-ctx.exe`）。无需重装 |
| 5.2 | opencode.json `mcp.lean-ctx` 注册为 local MCP（command 指向 `~/.cargo/bin/lean-ctx.exe`）→ `ctx_read`/`ctx_search`/`ctx_tree` 等工具可用 |
| 5.3 | auto-redirect（Read→ctx_read）/rewrite（shell 压缩）hook **无 opencode 原生**。接受手动调 ctx_* |
| 5.4（可选） | 若要自动压缩 shell 输出，装 **opencode-snip**（`VincentHardouin/opencode-snip`）：prefix `snip` 到 git/go/cargo/npm/docker 等，减 60-90% token。部分替代 lean-ctx rewrite |

---

## Phase 6 — 切换 + 验收

### 6.1 双轨试跑（必走，Q4 全迁前过渡）

- Claude Code 不动，opencode 并行装好
- 各 Phase 完成后用 opencode 跑一遍日常任务（lab-area 试验场），对照 Claude Code 体验
- 至少 1 周双轨，记录差异/缺功能/不顺手点

### 6.2 验收 checklist

| 项 | 验收标准 |
|----|---------|
| Provider | ccswitch 切 GLM/DeepSeek/MiniMax/Kimi，opencode 都能跑 |
| 规则 | `~/.claude/CLAUDE.md` 13 节在 opencode 生效（中文回复、§1.1 确认线等） |
| Skills | `~/.claude/skills/` 144 个被 opencode 识别（`/skills` 或等价命令列出） |
| MCP | lean-ctx/context7/playwright/github/douyin 等 8 个能用 |
| Agents | 217 个转换后在 opencode 可调用（抽查 5-10 个） |
| Hooks | secret_guard/git_guard/verify_gate 在 opencode 触发正确（构造测试场景） |
| Memory | opencode 写 memory → Claude Code 可读，反之亦然 |
| Keybindings | tui.json 常用键（提交/换行/中断/模型切换）对齐习惯 |

### 6.3 全切（Q4）

- 验收全过 → 日常主力 opencode
- Claude Code 保留为备份（不动配置，紧急回退用）

---

## 7. 风险 + 回退

| 风险 | 影响 | 缓解 |
|------|------|------|
| 217 agent 转格式工作量大 | Phase 2 慢 | 写转换脚本批处理；只转常用子集（engineering/code-reviewer/debugging 等），余者按需转 |
| caveman/ponytail/ecc 功能丢失 | mode 注入 + 部分 hook 链没了 | Q1/Q2 已接受；ecc 的安全 hook 由 Phase 4 自研补 |
| opencode hook 语义与 CC 不同 | verify_gate/turn_counter 行为偏移 | 用 `session.idle`/`message.updated` 近似；阈值可调 |
| lean-ctx auto 压缩丢失 | token 消耗上升 | 手动 ctx_* + opencode-snip 补 |
| opencode 模型路由不如 CC 灵活 | env ANTHROPIC_DEFAULT_*_MODEL 等价物 | ccswitch provider meta 处理 model 映射 |
| GateGuard / Fact-Forcing Gate 无 opencode 版 | 非代码 Edit 拦截丢失 | port `dep_gate.py` 等价 TS hook（Phase 4 已含） |

**回退路径**：任一 Phase 卡住且无法 1-2 轮解决 → 停，回 Claude Code 主力（配置未动，零成本回退）。连续 2-3 轮卡同方向 → §4 止血，复盘再继续。

---

## 8. 时间线（粗估）

| Phase | 预估 | 依赖 |
|-------|------|------|
| 0 基线 | 0.5 天 | 无 |
| 1 原生回退 | 0.5 天 | 0 |
| 2 配置转换 | 2-3 天（agent 转换脚本是大头） | 1 |
| 3 插件安装 | 1 天（逐个查 npm 名 + 验证） | 1 |
| 4 Hook port | 2-3 天（8 个 TS plugin） | 2 |
| 5 lean-ctx | 0.5 天 | 2 |
| 6 双轨试跑 | 1 周 | 0-5 全完 |
| 6 全切 | 0.5 天 | 试跑过 |

**合计实施 ~7 天 + 试跑 1 周**。可并行：Phase 2/3/4 独立切片。

---

## 9. 下一步动作（待你确认开工）

1. Phase 0.1 装 opencode（要不要现在帮你跑安装命令？需确认安装位置：全局还是项目本地）
2. Phase 3 各 plugin 的 npm 包名逐个查证（awesome 列表只给 GitHub repo，部分需读 README 确认 npm 名）
3. Phase 4 是否用单 plugin 合并还是每 hook 独立（建议独立，便于开关）
4. Phase 2.2 agent 转换脚本：要不要写？

确认后按 Phase 推进。每 Phase 完成落盘进度到此文件。
