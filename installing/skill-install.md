# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。权威源 = `~/.claude/skills/<name>/`（真目录本体，禁 symlink 指向外部），`~/.cc-switch/skills/` 仅作备份镜像、复制同步、用户手动。不用 agent-skills CLI 跨工具同步（见 memory `skill-mgmt-cc-switch-only`）。

套装按**仓库级**记一条，内部保留/裁剪写备注，不逐个开条目。自建 skill 不在这里，见 [custom-setup.md](custom-setup.md)。

模板见 [README.md](README.md)。

---

## 套件（仓库级）

### Matt Pocock skills（主力套件）
- 来源：https://github.com/mattpocock/skills
- 安装日期：2026-06/07（精确日待补）
- 安装方法：cc-switch 同步裸名形态进 `~/.claude/skills/`（model-invoked 可调）；另启用插件版 `mattpocock-skills@mattpocock`（`/plugin install`，见 tool-install.md marketplace 清单）
- 装到哪：`~/.claude/skills/` 裸名 + 插件版前缀 `mattpocock-skills:`。**裸名里 11 个是指向插件 cache 的 symlink**（本体在 `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/skills/...`，随插件升级路径变，非独立本体）：ask-matt / grill-me / grill-with-docs / grilling / handoff / setup-matt-pocock-skills / teach / to-spec / to-tickets / triage / wayfinder。**装回 = 启用 mattpocock 插件即恢复，不用复制**。其余裸名（diagnosing-bugs / tdd / request-refactor-plan / to-prd / to-issues 等）是真目录本体。
- 依赖：无
- 备注：**双形态并存**（memory `matt-skills-dual-form`）：裸名 model-invoked 可调；插件版 14 个 user-invoked 模型调不到需手动敲（含 ask-matt，见 `ask-matt-key-flow-decision`）。选型拍板：Matt 主力 + Superpowers 备用 + ECC 跳过（memory `skill-ecosystem-choice-2026-07`）。

### Superpowers（备用套件）
- 来源：https://github.com/obra/superpowers
- 安装日期：2026-06/07（待补）
- 安装方法：cc-switch 同步 + 插件版 `superpowers@claude-plugins-official` 启用
- 装到哪：`~/.claude/skills/`（brainstorming、systematic-debugging、test-driven-development、writing-plans、worktrees 等）
- 备注：定位=备用（流程类与 Matt 重叠时以 Matt 优先，画像匹配见选型 memory）。

### anthropic 官方 example-skills
- 来源：https://github.com/anthropics/skills
- 安装日期：待补
- 安装方法：cc-switch 同步 + 插件版 `example-skills@anthropic-agent-skills`
- 装到哪：`~/.claude/skills/`（docx / pptx / xlsx / pdf / canvas-design / theme-factory / web-artifacts-builder / skill-creator 等）

### 仓颉 cangjie-skill + first-principles pack
- 来源：三方仓颉生态（具体仓库待补）
- 安装日期：2026-07（采用记录见 memory `cangjie-skill-adoption-2026-07`）
- 安装方法：cc-switch 同步
- 装到哪：`~/.claude/skills/cangjie-skill` + first-principles pack 10 skill（axiomatic-thinking / critical-thinking / multi-mental-models / reductionism-deconstruction / logic-triple-check / implicit-assumption / contrarian-decision / founder-cognitive-boundary / zoom-out 等）
- 备注：RIA++ 质量扎实；20+ pack 可用性分级见该 memory。

### ECC（重型套件）
- 来源：https://github.com/affaan-m/ECC
- 安装日期：待补
- 安装方法：插件 marketplace（`/plugin marketplace add affaan-m/ECC`）+ 全插件启用；部分资产（statusline）已剥离（memory `statusline-independent-of-ecc`）
- 装到哪：插件 `ecc@ecc`；hooks（Fact-Forcing Gate / GateGuard 等）；cc-switch 侧另有裸名 skill
- 备注：用户拍板插件全开不关（memory `ecc-plugin-evaluation`）。升级会重置 settings 路径需留意。

### 思维/写作/学习类散件（cc-switch 同步，来源多为各作者仓库，逐个待补）
- 安装方法：cc-switch 同步进 `~/.claude/skills/`
- 清单（2026-08-07 盘点，119 个 skill 详见 memory `skill-routing-overhaul-2026-08-07`）：
  - 写作域：article-writer / edit-article / ai-text-polisher / human-writing / chinese-markdown-normalizer / javaguide-style-guide / publish-final-check / plagiarism-audit / review-doc / tech-article-review / multi-review-pipeline / drawio-article-illustration / drawio-chart
  - 学习域：deep-learn / cram-engine / tutorial-maker / research / last30days / tech-learning-roadmap（需 Exa API key，已配）/ obsidian-vault / learned
  - 前端域：frontend-design / frontend-ui-engineering / design-taste-frontend / emil-design-eng / apple-design / minimalist-ui / industrial-brutalist-ui / high-end-visual-design / impeccable / hallmark / hyperframes / animation-vocabulary / improve-animations / review-animations / find-animation-opportunities / pick-ui-library / redesign-existing-projects / design-an-interface / shadcn-vue-guide / imagegen-frontend-web / imagegen-frontend-mobile / remotion
  - 编码域散件：code-review / code-review-and-quality / debugging-and-error-recovery / git-workflow-and-versioning / security-and-hardening / spec-driven-development / simplify / neat-freak / improve-codebase-architecture / understand / understand-onboard / github-task / playwright / claude-api / officecli / storage-analyzer
  - 内容提取/平台：agent-reach / content-to-note / bili-note / douyin-video-summary / aihot / nuwa-skill
  - 其他：grilling / grill-with-docs / leader / darwin-skill / lean-ctx（skill 部分）/ gitnexus-exploring / ppt-master / understand-anything（另有插件版）/ full-output-enforcement（待考证来源）

## 单件登记（含地址/装法/位置）

### last30days
- 来源：https://github.com/mvanhorn/last30days-skill
- 安装日期：待补（2026-08-07 去链接化时复制进 .claude）
- 安装方法：clone/copy 进 `~/.claude/skills/last30days`（真目录本体）
- 装到哪：`~/.claude/skills/last30days`（SKILL.md / agents / references / scripts）
- 依赖：见 SKILL.md（拉 Reddit/X/YouTube/TikTok/HN/Polymarket/GitHub 数据，部分源需对应可用性；自带 doctor 健康检查）
- 备注：原是指向 cc-switch 的 symlink，2026-08-07 复制为 .claude 真目录。

### hallmark
- 来源：待补（SKILL.md frontmatter 无 github/homepage，v1.1.0）
- 安装日期：待补（2026-08-07 去链接化时复制进 .claude）
- 安装方法：copy 进 `~/.claude/skills/hallmark`（真目录本体）
- 装到哪：`~/.claude/skills/hallmark`（SKILL.md / references）
- 备注：Anti-AI-slop 设计 skill（greenfield/audit/redesign/design 提取）。原是指向 cc-switch 的 symlink，2026-08-07 复制为 .claude 真目录。

## 待补来源（安装时没记，回溯困难——以后装完当轮登记）
- 除 last30days/hallmark 外，以上散件的逐仓库 GitHub 地址与安装日期均未记录；需要重装时按名字在 cc-switch 源或对应作者仓库检索。

## 已卸载/备份
- `_weak-model-backup/`：2026-07-28 Carl 文章二轮精简移入 16 个（memory `skill-trim-carl-article-2026-07-28`）；判定原则见 skill-trimmer。
- E 类 5 份移备份夹（memory `skill-slim-audit-2026-07`）。
