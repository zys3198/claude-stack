# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。权威源 = `~/.claude/skills/<name>/`（真目录本体，禁 symlink 指向外部）。**2026-08-13 起 cc-switch 不再管理 skills**（镜像/skill-backups/repos 已全清，见 memory `skill-mgmt-cc-switch-only`），装法统一为 clone/copy 进 skills/。不用 agent-skills CLI 跨工具同步。

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

### Superpowers（备用套件）
- 来源：https://github.com/obra/superpowers
- 安装日期：2026-06/07（待补）
- 安装方法：clone/copy 进 `~/.claude/skills/` + 插件版 `superpowers@claude-plugins-official` 启用
- 装到哪：`~/.claude/skills/`（brainstorming、systematic-debugging、test-driven-development、writing-plans、worktrees 等）
- 备注：定位=备用（流程类与 Matt 重叠时以 Matt 优先，画像匹配见选型 memory）。

### ~~anthropic 官方 example-skills~~（2026-08-13 卸载）
- 来源：https://github.com/anthropics/skills
- 安装日期：待补
- 安装方法：clone/copy 进 `~/.claude/skills/` + 插件版 `example-skills@anthropic-agent-skills`
- 装到哪：`~/.claude/skills/`（docx / pptx / xlsx / pdf / canvas-design / theme-factory / web-artifacts-builder / skill-creator 等）
- 卸载：`claude plugin uninstall example-skills@anthropic-agent-skills`；原因=17 个官方教学示例与 `claude-plugins-official` 重复（frontend-design/skill-creator），全局 skills 无同名备份；cc-switch `common_config_claude` 已同步去该条目。可逆：`claude plugin install example-skills@anthropic-agent-skills`

### 仓颉 cangjie-skill + first-principles pack
- 来源：https://github.com/Yeadon8888/cangjie-skill（仓颉）+ https://github.com/kangarooking/first-principles-skill（第一性原理 pack；2026-08-11 公网反查锁定）
- 安装日期：2026-07（采用记录见 memory `cangjie-skill-adoption-2026-07`）
- 安装方法：clone/copy 进 `~/.claude/skills/`
- 装到哪：`~/.claude/skills/cangjie-skill` + first-principles pack 7 个在案（axiomatic-thinking / contrarian-decision / implicit-assumption / logic-triple-check / multi-mental-models / organizational-refresh / reductionism-deconstruction）
- 备注：RIA++ 质量扎实；20+ pack 可用性分级见该 memory。更正 2026-08-11：critical-thinking 经用户人工复核认定为自建，已入 git 白名单；zoom-out 实为 mattpocock/skills 成员，不属此 pack；founder-cognitive-boundary 磁盘已不在。

### ECC（重型套件）
- 来源：https://github.com/affaan-m/ECC
- 安装日期：待补
- 安装方法：插件 marketplace（`/plugin marketplace add affaan-m/ECC`）+ 全插件启用；部分资产（statusline）已剥离（memory `statusline-independent-of-ecc`）
- 装到哪：插件 `ecc@ecc`；hooks（Fact-Forcing Gate / GateGuard 等）；cc-switch 侧裸名 skill 已随 skills 域清除（2026-08-13）
- 备注：用户拍板插件全开不关（memory `ecc-plugin-evaluation`）。升级会重置 settings 路径需留意。

### ~~LoopForge devflow~~ → 已 fork 脱轨为自有系统 ai-coding-guide（2026-08-18）
- 来源：https://github.com/Tencent/LoopForge（上游 clone 在 `C:\ZYS\Code\loopforge`，HEAD 09c7652，仅作「看官方更新」参考窗口，**不再 pull 升级**，好更新人工挑拣吸收）
- 安装日期：2026-08（fork 脱轨定案 2026-08-18，用户拍板）
- 现状：`~/.claude/skills/ai-coding-guide/` = devflow 官方骨架彻底 fork + 旧 ai-coding-guide v1.9.0（散文路由器）退役并入，CLAUDE.md §2.1 入口行不变；旧 guide 归档 `~/.claude/archive/ai-coding-guide-v1.9.0/`（git 保留，Phase 2 路由吸收源料）。已入 git 白名单（`!skills/ai-coding-guide/` + `!skills/manifest.json`）
- 装到哪/构成：状态机骨架（scripts/templates/rules/agents/adapters=仅 claude+shared）+ `references/clarify-requirements.md`（2026-08-18 起顶层 `devflow-clarify-requirements/` skill 吸收入本体，原目录已删）+ 根级 `manifest.json`（adapter_registry.py 依赖，load-bearing）
- 定制点：SKILL.md 名前/描述/标题 + 编码路由 stopgap 段、`commands/ai-coding-guide.md`（claude 化重写）、`references/routing-stopgap.md`（新建）、`references/runtime-core.md` 适配器段改 claude、`rules/stages/summary.md` 第 4 条（82-能力沉淀证据草稿）；删 `adapters/{codebuddy,codex,cursor}` + `agents/openai.yaml`；tests 删 7 个 codebuddy 专项、4 个适配 claude
- 依赖：Python 3.8+ 标准库
- 测试基线：**20 passed / 2 failed**（2 失败 = Windows 路径分隔符断言，平台差异勿修）；`scripts/validate_config.py` OK（adapters=1）。注意：跑 pytest 先清 `PYTHONIOENCODING`/`PYTHONUTF8` 环境变量（harness 注入 utf-8 会致子进程输出被 GBK 解码假失败）
- 维护归属：自有系统，日常维护见 custom-setup.md「ai-coding-guide（编码域总入口系统）」；本条目仅留来源与 fork 前史

### 思维/写作/学习类散件
- 安装方法：clone/copy 进 `~/.claude/skills/`（`npx skills add <owner/repo>` 或手动 copy）
- **口径更正 2026-08-11**：旧「2026-08-08 实测 105 个（94 真目录 + 11 junction/symlink）」作废——当日实测 0 symlink；全量复核后 skills/ 为 184 目录 = 31 自建（入 git，见 custom-setup.md）+ 约 150 非自建（仓库级来源多已锁定，见上方「散件来源反查登记」）。原分类示例段已删（把自建误列第三方，与 custom-setup.md 冲突）。

## 单件登记（含地址/装法/位置）

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
| 单件 | agent-reach=Panniantong/Agent-Reach, douyin-video-summary=liu-wei-ai, shuorenhua=MrGeDiao/shuorenhua, find-skills=vercel-labs/skills, lean-ctx=yvgude/lean-ctx, hatch-pet=openai/skills, officecli=officecli/officecli, markdown-viewer=markdown-viewer/skills, bili-note=BiliNote 系（精确上游未锁定） |

插件匹配直接定第三方（不再逐个验证）：Matt 插件 25 裸名、test-driven-development（superpowers）、caveman 套件 7、understand-anything 8。

仍未锁定来源（公网搜不到且非用户自建）：human-writing、ppt-master、qiaomu-ai-prd、remotion、playwright（本地含 LICENSE/NOTICE）、ruthless-review、tech-learning-roadmap、writing-great-skills、doc-finder 之外的 review/slop-review/design/apikey-image-gen/grok-image-to-video/hyperframes/github-task/loop-engineering 等——以磁盘现状为用，重装时按名再查。

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
