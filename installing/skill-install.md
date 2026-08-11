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
- 装到哪：`~/.claude/skills/` 裸名 + 插件版前缀 `mattpocock-skills:`。**更正 2026-08-11**：旧称「裸名里 11 个是指向插件 cache 的 symlink」已过期——当日实测 skills/ 下 0 个 junction/symlink，裸名全是真目录本体；装回需复制或重装，不再「启用插件即恢复」。
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
- 来源：https://github.com/Yeadon8888/cangjie-skill（仓颉）+ https://github.com/kangarooking/first-principles-skill（第一性原理 pack；2026-08-11 公网反查锁定）
- 安装日期：2026-07（采用记录见 memory `cangjie-skill-adoption-2026-07`）
- 安装方法：cc-switch 同步
- 装到哪：`~/.claude/skills/cangjie-skill` + first-principles pack 7 个在案（axiomatic-thinking / contrarian-decision / implicit-assumption / logic-triple-check / multi-mental-models / organizational-refresh / reductionism-deconstruction）
- 备注：RIA++ 质量扎实；20+ pack 可用性分级见该 memory。更正 2026-08-11：critical-thinking 经用户人工复核认定为自建，已入 git 白名单；zoom-out 实为 mattpocock/skills 成员，不属此 pack；founder-cognitive-boundary 磁盘已不在。

### ECC（重型套件）
- 来源：https://github.com/affaan-m/ECC
- 安装日期：待补
- 安装方法：插件 marketplace（`/plugin marketplace add affaan-m/ECC`）+ 全插件启用；部分资产（statusline）已剥离（memory `statusline-independent-of-ecc`）
- 装到哪：插件 `ecc@ecc`；hooks（Fact-Forcing Gate / GateGuard 等）；cc-switch 侧另有裸名 skill
- 备注：用户拍板插件全开不关（memory `ecc-plugin-evaluation`）。升级会重置 settings 路径需留意。

### 思维/写作/学习类散件（cc-switch 同步）
- 安装方法：cc-switch 同步进 `~/.claude/skills/`
- **口径更正 2026-08-11**：旧「2026-08-08 实测 105 个（94 真目录 + 11 junction/symlink）」作废——当日实测 0 symlink；全量复核后 skills/ 为 184 目录 = 31 自建（入 git，见 custom-setup.md）+ 约 150 非自建（仓库级来源多已锁定，见上方「散件来源反查登记」）。原分类示例段已删（把自建误列第三方，与 custom-setup.md 冲突）。

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

## 散件来源反查登记（2026-08-11 公网反查确认）

重装通用方法：`npx skills add <owner/repo>` 或 clone 后 copy 进 `~/.claude/skills/<name>`。以下均为第三方，不进 git。

| 来源仓库 | 本地 skill |
|---|---|
| addyosmani/agent-skills | api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, observability-and-instrumentation, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, using-agent-skills |
| kangarooking/first-principles-skill | axiomatic-thinking, contrarian-decision, implicit-assumption, logic-triple-check, multi-mental-models, organizational-refresh, reductionism-deconstruction（critical-thinking 已被用户认定为自建，入 git） |
| Yeadon8888（仓颉生态） | cangjie-skill, nuwa-skill, darwin-skill |
| KKKKhazix/khazix-skills | hv-analysis, leader, neat-freak, storage-analyzer |
| emilkowalski/skills | emil-design-eng, animation-vocabulary, review-animations, improve-animations, find-animation-opportunities, apple-design, pick-ui-library |
| alvinunreal/oh-my-opencode-slim | worktrees, codemap, clonedeps, deepwork, simplify, reflect |
| mattpocock/skills（插件外裸名） | to-prd, to-issues, request-refactor-plan, qa, design-an-interface, zoom-out |
| abhigyanpatwari/GitNexus（`npx gitnexus analyze` 自动装） | gitnexus-cli, gitnexus-debugging, gitnexus-exploring, gitnexus-guide, gitnexus-impact-analysis, gitnexus-pdg-query, gitnexus-pr-review, gitnexus-refactoring, gitnexus-taint-analysis |
| leonxlnx/taste-skill（含改名副本，description 逐字相同实锤） | gpt-taste, image-to-code, minimalist-ui, industrial-brutalist-ui, redesign-existing-projects, stitch-design-taste, design-taste-frontend, design-taste-frontend-v1, high-end-visual-design, full-output-enforcement, brandkit, imagegen-frontend-mobile, imagegen-frontend-web |
| 单件 | agent-reach=Panniantong/Agent-Reach, douyin-video-summary=liu-wei-ai, shuorenhua=MrGeDiao/shuorenhua, find-skills=vercel-labs/skills, lean-ctx=yvgude/lean-ctx, hatch-pet=openai/skills, officecli=officecli/officecli, markdown-viewer=markdown-viewer/skills, bili-note=BiliNote 系（精确上游未锁定） |

插件匹配直接定第三方（不再逐个验证）：Matt 插件 25 裸名、test-driven-development（superpowers）、caveman 套件 7、understand-anything 8。

仍未锁定来源（公网搜不到且非用户自建）：human-writing、ppt-master、qiaomu-ai-prd、remotion、playwright（本地含 LICENSE/NOTICE）、ruthless-review、tech-learning-roadmap、writing-great-skills、doc-finder 之外的 review/slop-review/design/apikey-image-gen/grok-image-to-video/hyperframes/github-task/loop-engineering 等——以磁盘现状为用，重装时按名再查。

## 待补来源（安装时没记，回溯困难——以后装完当轮登记）
- 除 last30days/hallmark 外，以上散件的逐仓库 GitHub 地址与安装日期均未记录；需要重装时按名字在 cc-switch 源或对应作者仓库检索。
- **cram-engine / edit-article**（2026-08-11 移入本类）：原在 Git 白名单当自建追踪，2026-08-11 用户逐个复核时未认领为自建 → 按「非自定义进 installing」规则移出白名单（磁盘目录保留）。cram-engine 来源已锁定：https://github.com/liuliu667/cram-engine（README 实锤，`npx skills add liuliu667/cram-engine`）；edit-article 来源仍待补。注：二者仍被 tracked 路由器引用（learning-guide / article-writing-guide / deep-learn / tutorial-maker）——本机可用，clean clone 后需按来源重装。
- 2026-08-11 用户复核全量结论：skills/ 下 187 目录 = 31 自定义（已全入 Git 白名单）+ 154 非自定义（本台账管辖，来源大多待补）+ learned 空目录 + .ruff_cache。用户标记待删：darwin-weekly-audit、learned、obsidian-vault——**均已于 2026-08-11 物理删除并验证**（均未入 Git，无 git 历史残留）。

## 已卸载/备份
- `_weak-model-backup/`：2026-07-28 Carl 文章二轮精简移入 16 个（memory `skill-trim-carl-article-2026-07-28`）；判定原则见 skill-trimmer。
- E 类 5 份移备份夹（memory `skill-slim-audit-2026-07`）。
