# 用户自定义 Hook 备份（Codex 版）

**创建**:2026-06-14（Claude 版）；**迁 Codex**:2026-06-21
**目的**:`hooks.json` 被 lean-ctx 等工具重写时，从此恢复用户手加的 hook。
**关联**:AGENTS.md §5 指针指向本文件。
**头注 2026-08-11**：Codex 已卸载（`~/.codex` 已清），本备份仅作历史存档；Claude 侧 hooks 现状以 `settings.json` 引用为准。

## 加载机制

Codex **启动会话时一次性读取** `~/.codex/hooks.json`（与 Claude 一致：改了 hook 要重启会话才生效）。hook 有信任状态，未经导入流程手动新增的 hook 可能处于 untrusted；若重启后仍不触发，用 `/import` 重新导入。

## 脚本清单（`~/.codex/hooks/`）

| 脚本 | 事件/Matcher | 作用 |
|---|---|---|
| `git_guard.py` | PreToolUse 命令类 | 拦截破坏性命令（exit 2）+ commit/push/checkout 提醒 |
| `turn_counter.py` | UserPromptSubmit `.*` | 轮次计数 ≥20 提醒 /compact |
| `edited_tracker.py` | Pre/PostToolUse 编辑类 + SessionStart | 累计 ≥3 文件提醒 + 写状态(`edited_state.json`)：paths/edits_per_path/last_edit_ts/stop_blocks |
| `verify_recorder.py` | PostToolUse 命令类 | 检测验证命令(pytest/tsc/go test/npm test...40+ 模式)，更新 state.last_verify_ts/verify_cmds |
| `verify_gate.py` | Stop `.*` | 有代码改动且 last_edit_ts>last_verify_ts 且无验证 → block(exit 2)。拦 ≥3 次自动放行防死循环 |
| `placeholder_guard.py` | PreToolUse 编辑类 | 写入内容含 TODO/FIXME/省略/NotImplementedError/for brevity 等 → block(exit 2)。.md/.txt 文档豁免 |
| `secret_guard.py` | Pre+PostToolUse 命令类 | Pre:读机密文件→block；Post:stdout 命中 sk-/AKIA/ghp_/xox/AIza/BEGIN PRIVATE KEY → 告警 |
| `dep_gate.py` | PreToolUse 命令类 | 拦 pip/npm/yarn/cargo/go get/gem/composer/brew/apt 等新增依赖 → remind |

**已删除（迁 Codex 时作废）**:
- `inject_memory_context.py`：依赖 `~/.claude/memory/`，memory 精华已并入 AGENTS.md §5/§6。
- `self-evolve-stop.sh`：依赖 `~/.claude/projects/.../memory/`（Claude 专属路径结构）。

## tool_name 兼容性改造

Claude 的 shell 工具叫 `Bash`、编辑工具叫 `Edit/Write/MultiEdit`。Codex 工具名不同（shell 用类 `shell_command`/`exec`，编辑用 `apply_patch`），但精确名待确认。改造策略：
- **命令类**（git_guard/verify_recorder/secret_guard/dep_gate）：不再判 `tool_name == "Bash"`，改为**只要 `tool_input.command` 存在就检查**——工具名叫啥都不影响。
- **编辑类**（placeholder_guard/edited_tracker）：matcher 覆盖 `Edit|Write|MultiEdit|NotebookEdit|apply_patch|update|str_replace_based_edit_tool|file_edit`，且 edited_tracker 的 EDIT_TOOLS 元组同步扩充。

## 状态文件

`edited_state.json` / `turn_state.json` 均位于 `~/.codex/hooks/`（脚本内硬编码已从 `.claude` 改为 `.codex`）。字段（edited_state.json）：`{session_id, paths[], edits_per_path{}, last_edit_ts, last_verify_ts, verify_cmds[], stop_blocks}`。

## hooks.json 接线结构（11 块）

| 事件 | 脚本 | matcher |
|---|---|---|
| PreToolUse | git_guard / secret_guard / dep_gate | `Bash|shell|shell_command|exec|exec_command|local_shell|run|terminal` |
| PreToolUse | placeholder_guard / edited_tracker | `Edit|Write|MultiEdit|NotebookEdit|apply_patch|update|str_replace_based_edit_tool|file_edit` |
| PostToolUse | secret_guard / verify_recorder | （同命令类 matcher） |
| PostToolUse | edited_tracker | （同编辑类 matcher） |
| UserPromptSubmit | turn_counter | `.*` |
| Stop | verify_gate | `.*` |
| SessionStart | edited_tracker（重置） | `.*` |

## 恢复步骤

1. 读 `hooks.json`，检查上述脚本是否在对应事件块里。
2. 缺哪块，从清单复制 `command`：`C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe "C:/Users/zys31/.codex/hooks/<脚本>.py"`。
3. `python -c "import json; json.load(open(r'C:\Users\zys31\.codex\hooks.json'))"` 验证 JSON。
4. **重启 Codex 会话生效**。

## Codex 契约适配（2026-06-21）

**起因**：从 Claude 迁来的 hook 用 Claude 旧契约，导致 Codex 每次 PreToolUse 报 `invalid pre-tool-use JSON`。

**Codex 权威契约**（抓自 https://developers.openai.com/codex/hooks ，缓存 `%TEMP%\openai-docs-cache\codex-hooks.md`）：
- **PreToolUse 实际叫 `PermissionRequest`**：只能 `allow`/`deny`，**不支持注入 context**。
  - 输出：`{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny","message":"..."}}}`
  - 无命中 → 静默（stdout 空 + exit 0 = 默认放行）。
- **PostToolUse / UserPromptSubmit**：可用 `hookSpecificOutput.additionalContext` 注入开发者上下文。
- **Stop**：exit 0 时 stdout 须为 JSON（空也行但加 `{}` 更稳）；exit 2 + stderr = block。

**改动对照**：
- `git_guard`：BLOCK + commit/push/checkout 全改 `deny`（原 `remind` 软提示 → 硬拦，符合 §1.3 人工确认线）。
- `secret_guard`：Pre 读机密 → `deny`；Post 泄密 → `decision:block` + `additionalContext`。**修了既有 bug**：`SECRET_FILES` 正则锚定从 `(^|[/\\])` 改 `(^|[/\\\s])`，否则 `cat .env`（空格在前）漏检。
- `dep_gate`：新增依赖 → `deny`（原 `remind` → 硬拦）。
- `placeholder_guard`：改 `deny`。**修了既有 bug**：补 `apply_patch` 分支（Codex 编辑工具就是它，patch 文本在 `tool_input.command`，扫描以 `+` 开头的添加行）。
- `edited_tracker`：去掉 PreToolUse 的 `remind`（Codex Pre 不支持 context），保留状态记录（写文件、PostToolUse）。≥3 文件提醒、抖动守卫**功能失效**（Codex 无软提示通道），靠人工纪律替代。
- `verify_gate`：exit 0 的 4 个放行点补 `print("{}")`。
- `turn_counter`：**无需改**（UserPromptSubmit + additionalContext 本就合法）。
- `_contract_probe.py`：**从 hooks.json 移除**（调试残留，matcher `.*` 每次都跑，log 膨胀）。脚本文件保留备查。

**Python 解释器**：`C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe` 在 Codex hooks 环境可用（probe log 持续增长为证）；sandbox 文件系统看不到它，不影响 hook 运行。

**自检**：16 用例（拦截/放行/各事件）全过，stdout 均合法 JSON。验证 runner 见本节末。

**备份**：改动前全量备份在 `C:\Users\zys31\codex-hooks-backup-20260621\`（hooks.json + 9 个 .py）。

**生效**：重启 Codex 会话。`/import` 重新导入可刷新 trust 状态。

## 调参记录表（误伤/漏报）

| 日期 | Hook | 类型 | 触发 | 处置 | 调参建议 |
|---|---|---|---|---|---|
| 2026-06-21 | secret_guard | 漏报 | `cat .env` 空格在前漏检 | 正则锚加 `\s` | 已修 |
| 2026-06-21 | placeholder_guard | 漏报 | apply_patch 工具无分支 | 补 apply_patch 分支扫 command | 已修 |
| | | | | | |

