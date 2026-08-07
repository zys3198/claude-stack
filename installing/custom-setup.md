# 自建设施台账（非外部安装，自己造的）

记录自建 skill / hook / statusline / 全局配置的出处与迁移要点。外部装的见 skill-install.md / mcp-install.md / tool-install.md。

自建资产迁移原则：**git 仓库已追踪全部自建**（24 个 skill + CLAUDE.md + hooks + statusline + installing/ 本目录，见 `.gitignore` 白名单），`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠 skill-install.md / tool-install.md 记录的地址与命令重装。

---

## 自建 skill（~/.claude/skills/ 下，非 cc-switch 同步）

### 四域开工路由器（v1.4.x，持续演进）
- `ai-coding-guide`（编码域，v1.4.9）/ `article-writing-guide`（写作域）/ `learning-guide`（学习域，v1.4.6）/ `frontend-guide`（前端域，v1.5.3）
- 出处：2026-07 多轮会话沉淀；质量标准见 memory `router-guide-skill-quality-bar`；审查工具 `guide-skill-auditor`
- 迁移要点：四个一起拷；各有 CHANGELOG.md 记演进；互相有跨域转介引用，别只拷一个。

### code-change-workflow
- 出处：2026-07-29 CLAUDE.md 瘦身（§1-4 流程迁入，memory `claude-md-slimming-20260729`）
- 内容：改前/改中/改后清单、AI 代码审查、调试、Agent 调度、止血回退

### expose-unknowns
- 出处：暴露 unknown 方法论沉淀（memory `expose-unknowns-method`）

### guide-skill-auditor（v1.3.0）
- 出处：router 型 guide 质量审查方法论固化（memory `router-guide-skill-quality-bar`）

### skill-trimmer
- 出处：skill 库精简判定框架（Carl 四删五留 + 本机三决议，memory `skill-trim-carl-article-2026-07-28`）

### cc-switch-setting-sync
- 出处：防 cc-switch 切换 provider 降级 settings.json 的同步流程

### 写作 skill（自建 13 个）
- article-writer / edit-article / ai-text-polisher / chinese-markdown-normalizer / javaguide-style-guide / multi-review-pipeline / drawio-article-illustration / drawio-chart / publish-final-check / plagiarism-audit / review-doc / tech-article-review / content-to-note
- 出处：2026-06/07 写作流程沉淀；publish-final-check 演进耦合在 article-writing-guide/CHANGELOG.md；plagiarism-audit 针对实战漏网（Codex-book 整源漏审）设计；tech-article-review 与 review-doc 划边界（单 agent 逐段增量 vs 4 agent 并行）

### 学习 skill（自建 3 个）
- deep-learn / cram-engine / tutorial-maker

### 前端 skill（自建 1 个）
- shadcn-vue-guide（中文手写 + 本机 .bak 编辑痕）

### ai-coding-coach
- 学习陪跑模式（partner-coach/coach/engineer），ai-coding-guide 路由出口的协作行为定义

### ~~handoff / teach~~（更正 2026-08-07）
- **非自建**——磁盘上是 Matt 插件 symlink（指 plugins/cache），归 Matt 插件管，见 skill-install.md Matt Pocock 条目。之前误标自建。

### ~~obsidian-vault~~（2026-08-07 删除）
- 曾硬编码 wiki 路径（C:\ZYS\Code\wiki），用户拍板删除磁盘目录。若日后需要按 skill-install.md 散件检索重装。

### learning-guide 配套归档
- 学习记录归档流程，归档目录 `C:\ZYS\Wiki\80-records`（外部路径，迁移时另拷）

## hooks / statusline / 配置

### ~/.claude/hooks/
- ecc 系 hooks（Fact-Forcing Gate / GateGuard 等）随 ecc 插件来；另有自建/调整个别脚本
- 备份：`~/.claude/hooks/HOOKS_BACKUP.md`

### statusline（已脱离 ecc）
- 位置：`~/.claude/statusline`，含 cost + git 分支段（memory `statusline-independent-of-ecc`）
- 坑：ecc 升级可能重置 settings.json 里的 statusLine 路径，升级后检查。

### settings.json 关键本机定制
- `enabledPlugins` 清单快照见 tool-install.md
- lean-ctx 注入段在 CLAUDE.md 尾部（`<!-- lean-ctx -->` 包围，官方注入，别手改）

### CLAUDE.md 本身
- 2026-07-29 瘦身至 ~8.3KB，备份 `CLAUDE.md.bak-20260729`
- 常驻硬约束在 §1；装后登记规则见 §1 最后一行（installing/ 本台账）

## memory
- 位置：`~/.claude/projects/C--Users-zys31/memory/`
- 迁移：整目录拷；MEMORY.md 是索引。
