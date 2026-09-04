# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。第三方优先记录 Claude Code 插件；无兼容插件时才记录 `~/.claude/skills/<name>/` 裸 skill。**2026-08-13 起 cc-switch 不再管理 skills**（镜像/skill-backups/repos 已全清，见 memory `skill-mgmt-cc-switch-only`）。不用 agent-skills CLI 跨工具同步。

套装按**仓库级**记一条，内部保留/裁剪写备注，不逐个开条目。自建 skill 不在这里，见 [custom-setup.md](custom-setup.md)。

模板见 [README.md](README.md)。

---

## 套件（仓库级）

### Matt Pocock skills（主力套件）
- 来源：https://github.com/mattpocock/skills
- 安装日期：2026-06/07（精确日待补）
- 安装方法：clone/copy 进 `~/.claude/skills/` 裸名形态（model-invoked 可调）；另启用插件版 `mattpocock-skills@mattpocock`（`/plugin install`，见 tool-install.md marketplace 清单）
- 装到哪：`~/.claude/skills/` 裸名 + 插件版前缀 `mattpocock-skills:`。**更正 2026-08-11**：旧称「裸名里 11 个是指向插件 cache 的 symlink」已过期——当日实测 skills/ 下 0 个 junction/symlink，裸名全是真目录本体；装回需复制或重装，不再「启用插件即恢复」。
- 依赖：无
- 备注：**双形态并存**（memory `matt-skills-dual-form`）：裸名 model-invoked 可调；插件版 14 个 user-invoked 模型调不到需手动敲（含 ask-matt，见 `ask-matt-key-flow-decision`）。选型拍板：Matt 主力 + Superpowers 备用 + ECC 跳过（memory `skill-ecosystem-choice-2026-07`）。

### ~~Superpowers（备用套件）~~（已卸载 2026-08-19）
- 来源：https://github.com/obra/superpowers
- 安装日期：2026-06/07（待补）
- 安装方法：曾 clone/copy 进 `~/.claude/skills/`，并启用插件 `superpowers@claude-plugins-official`
- 装到哪：曾在 `~/.claude/skills/`（brainstorming、systematic-debugging、test-driven-development、writing-plans、worktrees 等）
- 当前状态：插件已卸载，缓存目录按历史记录保留；当前不加载。
- 备注：历史定位=备用（流程类与 Matt 重叠时以 Matt 优先）；恢复方式见本文件下方卸载记录。

### 仓颉 cangjie-skill + first-principles pack
- 来源：https://github.com/Yeadon8888/cangjie-skill（仓颉）+ https://github.com/kangarooking/first-principles-skill（第一性原理 pack；2026-08-11 公网反查锁定）
- 安装日期：2026-07（采用记录见 memory `cangjie-skill-adoption-2026-07`）
- 安装方法：clone/copy 进 `~/.claude/skills/`
- 装到哪：`~/.claude/skills/cangjie-skill` + first-principles pack 7 个在案（axiomatic-thinking / contrarian-decision / implicit-assumption / logic-triple-check / multi-mental-models / organizational-refresh / reductionism-deconstruction）
- 备注：RIA++ 质量扎实；20+ pack 可用性分级见该 memory。更正 2026-08-11：critical-thinking 经用户人工复核认定为自建，已入 git 白名单；zoom-out 实为 mattpocock/skills 成员，不属此 pack；founder-cognitive-boundary 磁盘已不在。

### ~~ECC（重型套件）~~（已卸载 2026-08-13）
- 来源：https://github.com/affaan-m/ECC
- 安装日期：待补；卸载日期：2026-08-13
- 安装方法：曾通过插件 marketplace（`/plugin marketplace add affaan-m/ECC`）安装并启用
- 曾装到哪：插件 `ecc@ecc`；hooks（Fact-Forcing Gate / GateGuard 等）；部分 hook 与 chrome-devtools MCP 已按用户决策剥离保留
- 当前状态：插件与 marketplace 已移除；缓存可能作为历史回退对照保留，不代表当前可用。
- 备注：插件卸载与剥离细节见 `custom-setup.md`「ecc 剥离/卸载」章节；恢复需重新安装并重新评估 hook 冲突。

### ~~LoopForge devflow~~ → 已 fork 脱轨为自有系统 ai-coding-guide（2026-08-18）
- 来源：https://github.com/Tencent/LoopForge（上游 clone 在 `C:\ZYS\Code\loopforge`，HEAD 09c7652，仅作「看官方更新」参考窗口，**不再 pull 升级**，好更新人工挑拣吸收）
- 安装日期：2026-08（fork 脱轨定案 2026-08-18，用户拍板）
- 历史状态：`~/.claude/skills/ai-coding-guide/` 曾是 DevFlow 官方骨架 fork；现已退出全局 skill，旧 guide 归档于 `~/.claude/archive/ai-coding-guide-v1.9.0/`，后续 fork 版已删除并备份于 `~/.claude/backups/ai-coding-guide-delete-20260902/`。本条仅保留来源与 fork 前史。
- 装到哪/构成：状态机骨架（scripts/templates/rules/agents/adapters=仅 claude+shared）+ `references/clarify-requirements.md`（2026-08-18 起顶层 `devflow-clarify-requirements/` skill 吸收入本体，原目录已删）+ 根级 `manifest.json`（adapter_registry.py 依赖，load-bearing）
- 定制点：SKILL.md 名前/描述/标题 + 编码路由 stopgap 段、`commands/ai-coding-guide.md`（claude 化重写）、`references/routing-stopgap.md`（新建）、`references/runtime-core.md` 适配器段改 claude、`rules/stages/summary.md` 第 4 条（82-能力沉淀证据草稿）；删 `adapters/{codebuddy,codex,cursor}` + `agents/openai.yaml`；tests 删 7 个 codebuddy 专项、4 个适配 claude
- 依赖：Python 3.8+ 标准库
- 测试基线：**20 passed / 2 failed**（2 失败 = Windows 路径分隔符断言，平台差异勿修）；`scripts/validate_config.py` OK（adapters=1）。注意：跑 pytest 先清 `PYTHONIOENCODING`/`PYTHONUTF8` 环境变量（harness 注入 utf-8 会致子进程输出被 GBK 解码假失败）
- 维护归属：自有系统，日常维护见 custom-setup.md「ai-coding-guide（编码域总入口系统）」；本条目仅留来源与 fork 前史

#### DTSF 项目 DevFlow Claude 适配器
- 来源：本地 `~/.claude/skills/ai-coding-guide/` 的 Claude adapter（上游前史见本节 LoopForge 条目）
- 安装日期：2026-08-20
- 安装命令原文：`python3 /c/Users/zys31/.claude/skills/ai-coding-guide/scripts/install_adapter.py --adapter claude --project-root . --refresh-managed --copy-skills`
- 装到哪：`C:\ZYS\Code\dtsf\.claude\`（2 个 DevFlow 执行器、portable `ai-coding-guide` 副本及托管清单）
- 依赖：Python 3.8+、Claude Code `Agent` 工具
- 备注：Windows 按项目约束使用复制，不尝试 symlink；只为 OA 考勤计划及后续隔离阶段服务。安装输出：`agents_installed=2`、`agents_preserved=0`、`ai-coding-guide=copied`。

### 思维/写作/学习类散件
- 安装方法：clone/copy 进 `~/.claude/skills/`（`npx skills add <owner/repo>` 或手动 copy）
- **历史盘点口径（2026-08-11，已过期）**：旧记录曾统计 skills/ 为 184 目录 = 31 自建 + 约 150 非自建；当前归属与可用状态以 `custom-setup.md` 的当前清单、实际 `skills/` 目录和本文件后续条目为准。原分类示例段已删，避免把自建误列第三方。

## 单件登记（含地址/装法/位置）

### eli5
- 来源：https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md
- 更新日期：2026-08-31
- 覆盖方法：读取上游 `eli5/skills/eli5/SKILL.md` 内容，覆盖 `~/.claude/skills/eli5/SKILL.md`；获取命令：`gh api repos/anthropics/claude-plugins-community/contents/eli5/skills/eli5/SKILL.md --jq .content | base64 -d`
- 装到哪：`~/.claude/skills/eli5/SKILL.md`
- 依赖：HTML artifact 能力（源 skill 要求）
- 备注：替换原 116 行本地版本；当前版本触发 `/eli5 <主题>`，输出大图少文字的 HTML artifact。

### last30days
- 来源：https://github.com/mvanhorn/last30days-skill
- 安装日期：待补（2026-08-07 去链接化时复制进 .claude）
- 安装方法：clone/copy 进 `~/.claude/skills/last30days`（真目录本体）
- 装到哪：`~/.claude/skills/last30days`（SKILL.md / agents / references / scripts）
- 依赖：见 SKILL.md（拉 Reddit/X/YouTube/TikTok/HN/Polymarket/GitHub 数据，部分源需对应可用性；自带 doctor 健康检查）
- 备注：原是指向 cc-switch 的 symlink，2026-08-07 复制为 .claude 真目录。

### modlens
- 来源：https://github.com/liustack/modlens
- 安装日期：2026-08-16
- 安装方法：clone/copy 进 `~/.claude/skills/modlens`（官方 INSTALL.md Path A）
- 装到哪：`~/.claude/skills/modlens`（SKILL.md / references / scripts/run.sh+run.ps1）
- 依赖：node 22.19+ / npx / bun 任一（本机 node v24 ✓）+ 一个 vision 引擎
- 用途：给纯文本模型（DeepSeek/GLM 等）加视觉，粘贴图片→结构化 JSON 证据（OCR/版面/语义）
- 引擎：**openai 兼容 → 阿里云百炼 DashScope（qwen3-vl-plus）**，境内直连稳定，端到端验证通过（OCR 正确，~7.5s）。曾试 claude-cli（复用 Claude Code 登录）但 **Windows 上不稳**：claude.exe 派生后台 helper 进程泄漏不退出，导致 `spawn EINVAL` / 结果坏（"Unsupported Image"）/ temp 清理 EPERM 飘忽，4 次测试仅 1 次全对。定位为上游未覆盖的「原生 exe shim」+ 进程泄漏 bug。**SKILL.md 已打本地补丁**（「Run it」段 Windows claude-cli 说明：需 `-p claude-cli --provider-bin <claude.exe 绝对路径>`），重装会丢失需重打。也试过 gemini-api（key 已配）但 **403 被墙**（Gemini API 境内不可用），留作有代理时的备选。当前故障转移链：openai → gemini-api → claude-cli（后两者境内会失败，仅噪音）
- 配置：`~/.modlens/config.json`（0600）。注意：环境变量 `ANTHROPIC_BASE_URL=http://127.0.0.1:15721`（本地网关），切 anthropic provider 会走到它

### leader
- 来源：https://github.com/KKKKhazix/khazix-skills/tree/main/leader
- 安装日期：2026-08-31
- 安装方法：读取 GitHub Contents API 固定提交 `7a5c4934be4106ac740ffdb95280bb81b3f4b83c` 后复制文件
- 装到哪：`~/.claude/skills/leader/SKILL.md` + `references/anatomy.md` + `references/style.md`
- 依赖：无额外依赖
- 备注：上游目录仅含 SKILL.md 与两份 references；已审查，无 scripts、外部命令、远程安装、数据上传、密钥读取或配置修改指令。

## 散件来源反查登记（2026-08-11 公网反查确认）

无 Claude Code plugin manifest 的裸 skill 重装方法：`npx skills add <owner/repo>` 或 clone 后 copy 进 `~/.claude/skills/<name>`。以下均为第三方，不进 git。

| 来源仓库 | 本地 skill |
|---|---|
| addyosmani/agent-skills | api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, observability-and-instrumentation, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, using-agent-skills |
| kangarooking/first-principles-skill | axiomatic-thinking, contrarian-decision, implicit-assumption, logic-triple-check, multi-mental-models, organizational-refresh, reductionism-deconstruction（critical-thinking 已被用户认定为自建，入 git） |
| Yeadon8888（仓颉生态） | cangjie-skill, nuwa-skill, darwin-skill |
| KKKKhazix/khazix-skills | hv-analysis, leader, neat-freak, storage-analyzer |
| emilkowalski/skills | emil-design-eng, animation-vocabulary, review-animations, improve-animations, find-animation-opportunities, apple-design, ~~pick-ui-library~~（2026-08-18 归档 `~/.claude/archive/pick-ui-library`，wayfinder ticket 02 拍板：未接路由+原生可覆盖） |

> 2026-08-18 归档登记（wayfinder ticket 02「coding 域深耕判定」）：`design`（来源待补）、`pick-ui-library`（emilkowalski/skills）移入 `~/.claude/archive/`，可逆；判据=未接 frontend-visual 路由且模型原生可覆盖。
| alvinunreal/oh-my-opencode-slim | worktrees, codemap, clonedeps, deepwork, simplify, reflect |
| mattpocock/skills（插件外裸名） | to-prd, to-issues, request-refactor-plan, qa, design-an-interface, zoom-out |
| abhigyanpatwari/GitNexus（`npx gitnexus analyze` 自动装） | gitnexus-cli, gitnexus-debugging, gitnexus-exploring, gitnexus-guide, gitnexus-impact-analysis, gitnexus-pdg-query, gitnexus-pr-review, gitnexus-refactoring, gitnexus-taint-analysis |
| 单件 | agent-reach=Panniantong/Agent-Reach（外部，非自建，https://github.com/Panniantong/Agent-Reach/tree/main）, douyin-video-summary=liu-wei-ai, shuorenhua=MrGeDiao/shuorenhua, find-skills=vercel-labs/skills, lean-ctx=yvgude/lean-ctx, hatch-pet=openai/skills, officecli=officecli/officecli, markdown-viewer=markdown-viewer/skills, ~~bili-note~~（用户确认自建，移至 custom-setup.md） |

插件匹配直接定第三方（不再逐个验证）：Matt 插件 25 裸名、test-driven-development（superpowers）、caveman 套件 7、understand-anything 8。

仍未锁定来源（公网搜不到且非用户自建）：human-writing、qiaomu-ai-prd、remotion、ruthless-review、writing-great-skills、doc-finder 之外的 review/slop-review/design/apikey-image-gen/grok-image-to-video/hyperframes/github-task/loop-engineering 等——以磁盘现状为用，重装时按名再查。`ppt-master`、`playwright`、`impeccable` 已转 Claude Code 插件；`hallmark`、`kimi-webbridge` 的第三方来源与兼容性见 2026-08-26 清理批次。

### ~~skill-slimming（LearnPrompt/carl-skills）~~（2026-08-14 已吸收后卸载）
- 来源：https://github.com/LearnPrompt/carl-skills
- 安装日期：2026-08-14；卸载日期：2026-08-14（`npx skills remove skill-slimming -g`，官方命令清理 universal store + 各宿主 symlink，验证 0 残留）
- 安装方法：`npx skills add LearnPrompt/carl-skills --skill skill-slimming -g`（skills CLI v1.5.22）
- 曾装到哪：`~/.agents/skills/skill-slimming/` + `~/.claude/skills/skill-slimming` symlink
- 依赖：python3 + webbrowser（loopback HTTP 服务，无第三方包）
- **处置：吸收式合并进 skill-trimmer（2026-08-14，用户拍板）**。复用资产已收编进 `~/.claude/skills/skill-trimmer/`：`scripts/review_server.py`（1069 行，品牌已归并 skill-slimming→skill-trimmer，状态目录 `~/.skill-trimmer/`）+ `assets/review.html` + `references/audit-contract.md`；scan_skills.py 新增输出 `inventory-review.json`（review 契约）。SKILL.md 接入：网页复审页（§4.5）、触发空壳合同、三维 token 模型、测量标签纪律。未吸收（有意）：多宿主/插件/MCP 审计、apply/delete 阶段+verification_receipt、recheck 漂移复查、agents/openai.yaml（Codex 专属）、probe 子命令（本机 settings.json 无 skillOverrides，空转）。判定基准不吸收（slimming 判据浅，仅 global/project/trigger 三值）。安全面已核：仅绑 127.0.0.1 随机端口、随机 token、无 subprocess/shell/网络、只写自己状态目录、不读密钥。端到端验证通过：scan→validate→serve 冒烟（health 200 / 页面 200 / 无 token 401 / 坏 Host 400 / bootstrap 69 skills）。可逆：`npx skills add LearnPrompt/carl-skills --skill skill-slimming -g` 重装。

### taste-skill 插件版（Leonxlnx/taste-skill）
- 来源：https://github.com/Leonxlnx/taste-skill
- 安装日期：2026-08-13
- 安装方法：用户手动安装插件（命令原文未提供，待补；结果经 `installed_plugins.json` 实测确认）
- 装到哪：`~/.claude/plugins/cache/taste-skill/taste-skill/1.0.0`（插件 `taste-skill@taste-skill`，scope=user，version 1.0.0，commit `e988add20dab0fa97d7a76781c48961c8184288e`，installedAt 2026-08-13T02:21）
- 依赖：无
- 备注：与上方反查表「leonxlnx/taste-skill」裸名散件同源双形态。插件版自带 13 个 skill，前缀 `taste-skill:`（brandkit / brutalist-skill / gpt-tasteskill / image-to-code-skill / imagegen-frontend-mobile / imagegen-frontend-web / minimalist-skill / output-skill / redesign-skill / soft-skill / stitch-skill / taste-skill / taste-skill-v1）。当日确认本会话可用。

## 待补来源（安装时没记，回溯困难——以后装完当轮登记）
- 除 last30days/hallmark 外，以上散件的逐仓库 GitHub 地址与安装日期均未记录；需要重装时按名字在对应作者仓库检索（cc-switch 侧镜像源 2026-08-13 已删）。
- **cram-engine / edit-article**（2026-08-11 移入本类）：原在 Git 白名单当自建追踪，2026-08-11 用户逐个复核时未认领为自建 → 按「非自定义进 installing」规则移出白名单（磁盘目录保留）。cram-engine 来源已锁定：https://github.com/liuliu667/cram-engine（README 实锤，`npx skills add liuliu667/cram-engine`）；edit-article 来源仍待补。注：二者仍被 tracked 路由器引用（learning-guide / article-writing-guide / deep-learn / tutorial-maker）——本机可用，clean clone 后需按来源重装。
- 2026-08-11 用户复核全量结论：skills/ 下 187 目录 = 31 自定义（已全入 Git 白名单）+ 154 非自定义（本台账管辖，来源大多待补）+ learned 空目录 + .ruff_cache。用户标记待删：darwin-weekly-audit、learned、obsidian-vault——**均已于 2026-08-11 物理删除并验证**（均未入 Git，无 git 历史残留）。

## 已卸载/备份
- `_weak-model-backup/`：2026-07-28 Carl 文章二轮精简移入 16 个（memory `skill-trim-carl-article-2026-07-28`）；判定原则见 skill-trimmer。**2026-08-13 随 cc-switch skills 域全清物理删除**，仅剩记录。
- E 类 5 份移备份夹（memory `skill-slim-audit-2026-07`）。**2026-08-13 备份夹已随 cc-switch skills 域清除**。
- **2026-08-13 插件同名冗余清理**：55 个裸技能（`~/.claude/skills/`）与已启用插件同名 → 判定冗余，移入 `_weak-model-backup/`（原备份夹 README 2026-08-13 追加一行，备份夹已随 cc-switch skills 域清除）。来源=5 插件：caveman 7（裸名同名，插件版 dmi=0 模型可调）、mattpocock 28（其中 15 个插件版 dmi=true 仅手动：ask-matt/grill-me/grill-with-docs/handoff/teach/implement/improve-codebase-architecture/setup-matt-pocock-skills/to-spec/to-tickets/triage/wayfinder/writing-beats/writing-fragments/writing-shape；删裸名后模型调不到仅手敲）、taste-skill 13（dmi=0）、superpowers 1（test-driven-development）、understand-anything 8（dmi=0）。**可逆**：该批唯一副本已随备份夹清除，恢复=重装对应插件（见上方套件记录），不再有裸名副本可移回。判定依据=「插件已有则 skills/ 副本冗余」（用户 2026-08-13 拍板「全部 55 个」）。

### 第三方插件化清理批次（2026-08-25）
- **last30days**：来源 `https://github.com/mvanhorn/last30days-skill.git`；版本 `3.21.1`；插件 `last30days@last30days-skill`；安装命令：`claude plugin marketplace add --scope user https://github.com/mvanhorn/last30days-skill.git`，`claude plugin install --scope user --yes last30days@last30days-skill`；安装位置：`~/.claude/plugins/cache/last30days-skill/last30days/3.21.1`；依赖：Node/Python，运行时按上游配置可选数据源凭据；备注：官方版本替代本地 v3.18.4。
- **officecli**：来源 `https://github.com/officecli/officecli.git`；版本 `0.1.0`；插件 `officecli@officecli`；安装命令：`claude plugin marketplace add --scope user https://github.com/officecli/officecli.git`，`claude plugin install --scope user --yes officecli@officecli`；安装位置：`~/.claude/plugins/cache/officecli/officecli/0.1.0`；依赖：officecli CLI 及其自身认证/运行时配置；备注：替代本地 `officecli`。
- **gitnexus**：来源 `https://github.com/abhigyanpatwari/GitNexus.git`；版本 `1.6.9`；插件 `gitnexus@gitnexus-marketplace`；安装命令：`claude plugin marketplace add --scope user https://github.com/abhigyanpatwari/GitNexus.git`，`claude plugin install --scope user --yes gitnexus@gitnexus-marketplace`；安装位置：`~/.claude/plugins/cache/gitnexus-marketplace/gitnexus/1.6.9`；依赖：Node/GitNexus CLI；备注：替代本地 9 个旧 `gitnexus-*` skill，`gitnexus-pr-review` 对应官方 `gitnexus-review`。

### 第三方插件/skill 清理批次（2026-08-26）
- **impeccable**：来源 `https://github.com/pbakaus/impeccable`；版本 `4.1.1`；Claude Code 插件 `impeccable@impeccable`；安装命令原文：`claude plugin marketplace add pbakaus/impeccable --scope user`，`claude plugin install impeccable@impeccable --scope user --yes`；安装位置：`~/.claude/plugins/cache/impeccable/impeccable/4.1.1`；依赖：无；证据：上游 `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`；已删除 `~/.claude/skills/impeccable` 裸副本。
- **ppt-master**：来源 `https://github.com/hugohe3/ppt-master`；版本 `ebd74d1f1d61-32c1cf49`；Claude Code 插件 `ppt-master@ppt-master`；安装命令原文：`claude plugin marketplace add hugohe3/ppt-master --scope user`，`claude plugin install ppt-master@ppt-master --scope user --yes`；安装位置：`~/.claude/plugins/cache/ppt-master/ppt-master/ebd74d1f1d61-32c1cf49`；依赖：按上游 skill 配置；证据：上游 `skills/.claude-plugin/plugin.json`；已删除 `~/.claude/skills/ppt-master` 裸副本。
- **playwright**：来源 `https://github.com/anthropics/claude-plugins-official`；版本 `b819188d2eea`；插件 `playwright@claude-plugins-official` 已存在并启用，本轮未重复安装；安装位置：`~/.claude/plugins/cache/claude-plugins-official/playwright/b819188d2eea`；证据：上游 `external_plugins/playwright/.claude-plugin/plugin.json`；已删除 `~/.claude/skills/playwright` 裸副本。
- **hallmark**：来源 `https://github.com/Nutlope/hallmark`；上游仅提供 `skills/hallmark/SKILL.md`，未提供 Claude Code `.claude-plugin/plugin.json`；本轮不伪装为插件、不改装法，保留现有 `~/.claude/skills/hallmark` 作为第三方裸 skill；上游重装命令：`npx skills add nutlope/hallmark`；不进自建 skill 白名单。
- **kimi-webbridge**：官方来源 `https://github.com/MoonshotAI/kimi-code`；上游文件 `plugins/official/kimi-webbridge/kimi.plugin.json`（v1.11.3）是 Kimi 原生插件格式，不是 Claude Code manifest；本轮不伪装为 Claude 插件，保留现有第三方 skill 与 daemon，详细安装记录见 `tool-install.md`；不进自建 skill 白名单。
- **处置**：已按用户确认永久删除 `impeccable`、`playwright`、`ppt-master` 三个 `~/.claude/skills/` 裸副本；插件 cache 保留为唯一 Claude Code 来源。

### pi.dev 侧插件技能平移植入（2026-08-23，CC→pi 迁移批次）
- 来源（5 插件 cache 源目录）：mattpocock/mattpocock-skills/1.2.3 + caveman（最新 sha aa7b94ae0fa8）+ ponytail/4.8.3 + open-code-review/1.0.0 + taste-skill/1.0.0
- 原因：插件自带 52 个 skill 在 CC cache 里是完整仓库副本（frontmatter name+description 与 pi 加载协议同构），无需 transskill 转换 → 直接 `cp -r` 整个 skill 目录（**附随文件完整保留**：FORMAT.md/LOGIC.md/UI.md/tracker docs/agents/）
- 安装日期：2026-08-23；安装命令：`cp -r <plugin>/skills/<name>/ ~/.pi/agent/skills/<name>/`（52 目录一轮完成，脚本在 `lab-area/exp/2026-08-23-plugin-migrate/convert-plugins.sh`）
- 装到哪：`~/.pi/agent/skills/`（52 个：mattpocock 25 + caveman 7 + ponytail 6 + open-code-review 1 + taste-skill 13）
- 依赖：无（pi 加载协议原生支持裸 SKILL.md + 附随相对引用；解析规则见 pi `dist/core/skills.js`：name=frontmatter.name||目录名，description 必填，冲突后到先占）
- 备注：**注意 taste-skill 源目录名≠frontmatter name**（如 output-skill→full-output-enforcement、taste-skill→design-taste-frontend）——pi 按 frontmatter name 索引故无冲突，但 `/skill:输出名` 与 `/skill:目录名` 可能不一致，用 frontmatter name。caveman 在 cache 存 28 个内容重复的 sha，只取最新。含 `agents/` 子目录的（domain-modeling/teach/prototype/setup-matt-pocock-skills）是 CC subagent 定义，pi 端不加载，属携带保留。遗留：pi 端 `/reload` 后验证 52 个可见 + 抽查附随引用链。

### 项目级安装：rohitg00/ai-engineering-from-scratch
- 来源：https://github.com/rohitg00/ai-engineering-from-scratch
- 安装日期：2026-08-31
- 安装命令原文：`npx skills add rohitg00/ai-engineering-from-scratch`
- 装到哪：`C:\\ZYS\\Tutorial\\AI\\ai-engineering-from-scratch\\.agents\\skills\\` 下 8 个 skill；CLI 同时为 Claude Code 等宿主创建 symlink
- 依赖：Node.js / npx；本次自动安装 `skills@1.5.23`
- 内容：check-understanding、claude-certification、course-guide、find-your-level、learn、learn-agent-skills、learn-mcp、start-learning
- 备注：CLI 安全评估标记 `claude-certification` 为 Critical Risk，`learn-agent-skills` 有 1 alert；使用前需人工审阅。项目新增 `skills-lock.json`。

### Skill 库精简（2026-09-03，skill-trimmer 流程 + 用户逐项拍板）
- **卸载（移入备份，非真删）**：learning-guide、article-writing-guide（纯域路由器砍除，下游直达）、lean-ctx、learning-personas、deep-learn、tech-learning-roadmap、expose-unknowns、preflight-check（预检清单并入 code-change-workflow §1.1）、tutorial-maker、ai-coding-coach（学习域收敛用户拍板）、hallmark（与插件 impeccable 重叠，归档 60 天观察至 2026-11-02）、generic-course-tutor-workspace（产物目录挪出）、wiki-skill（lab-area 项目级，与全局 improver-skill 重复）
- **备份位置**：`~/.claude/backups/skill-trim-20260903/`（含 README.md 判定理由+恢复方式，恢复 = `mv` 回 `~/.claude/skills/`）
- **改写**：generic-course-tutor / article-writer / bili-note / content-to-note / wiki-sediment 描述去路由转介自包含；parallel-delegation / bidirectional-steelman / leader 触发面收窄；code-change-workflow 并入 5 项环境预检清单
- **插件**：`enabledPlugins.open-code-review → false`（review 三重撞车，留 official code-review + matt code-review + ponytail-review），已同步 cc-switch DB common_config_claude（backup: sync-backup-20260903_235738.json），providers commonConfigEnabled 均 True
- **库规模**：32 目录 → 20 skill
- **pi 侧退役（2026-09-04）**：用户拍板弃用 pi。`~/.pi/agent/skills/` + `skills-sync/`（185M，27+20 目录）移入 `~/.claude/backups/skill-trim-20260903/pi-side/`。~/.pi 其余（auth.json/memory/sessions/settings/台账/github-sync 脚本）保留未动，pi-stack git 仓库完好。恢复 = mv 回原位。
- **插件卸载（2026-09-04）**：彻底卸载 ppt-master（缓存 102M）、officecli、taste-skill、frontend-design（均为长期禁用态）——settings.json enabledPlugins/extraKnownMarketplaces、installed_plugins.json、known_marketplaces.json、plugins/cache/ 四处同步清理。open-code-review 维持禁用未卸。playwright 禁用（浏览器自动化二选一，留 chrome-devtools MCP）。同步 cc-switch DB 完成。
- **历史会话清理（2026-09-04）**：~/.claude/projects 清 3 天前 transcript（uuid 条目，memory 保留），释放 1.4G（2.2G→419M）。
- **cc-switch-setting-sync 自动化（2026-09-04）**：新增 hooks/settings-sync-auto.py（PostToolUse Edit|Write，命中 settings.json 即自动同步 cc-switch DB，幂等 NO-OP），skill 降级为排查/修复/验证文档。同轮：skill_ledger.py 接线 PostToolUse matcher=Skill（skill-usage.log 记账恢复）；chrome-devtools-mcp 固定 1.8.0；hooks/ 清残留（HOOKS_BACKUP.md/debug.log/__pycache__）。
- **存储自动化+清理（2026-09-04）**：settings.json 加 cleanupPeriodDays=7（transcript 自动滚动清理，替代手动清）；better-harness 8 个 2026-08-05 旧 run 目录（24M）与 archive/ 旧归档（30M）清空。
- **install-ledger 自动化（2026-09-04）**：新增 hooks/install-ledger-reminder.py（PostToolUse Bash，匹配 claude plugin/mcp、npm -g、pip/pipx/uv/cargo/winget/scoop、npx skills add 等 10 类安装/卸载命令 → 追加 installing/auto-log.jsonl 兜底 + additionalContext 提醒模型按 §7 正式登记）。自检 tests/test_install_ledger_reminder.py（10 hit + 5 quiet 全过）。skill_ledger（Skill 调用记账）+ 本 hook（安装动作记账）+ ccswitch 自动同步三件齐。
