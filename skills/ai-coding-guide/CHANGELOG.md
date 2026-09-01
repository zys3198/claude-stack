# Changelog

本文件记录 ai-coding-guide 路由层和 DevFlow 入口的可审计变更。日期采用 YYYY-MM-DD。

## [Unreleased] - 2026-08-31

### Added

- 接入已审计的模型无关 `parallel-delegation` 全局 skill，作为编码主分类之后的可组合执行层：仅在独立且可验收子任务存在时并行，并保留隔离、主代理验收和失败降级。
- 在 `routing.md` / `ecosystems.md` 登记与 `/to-tickets`、交付状态机的边界，新增触发与不触发路由回归用例。

### Rationale

- 来源：用户提供的文章 https://mp.weixin.qq.com/s?__biz=MzE5ODc3Njc0NQ==&mid=2247484429&idx=1&sn=1cb67d6c6baa4f7f12a11710e7b5e623&chksm=9701ac8f1625d8eb8116f3752109735f119d89b2badacb8f648938228efc300e57be9bc8e6f5&mpshare=1&scene=1&srcid=0831RMVutN6h4pVnxAhC0ON6&sharer_shareinfo=fb8307e673915c06c1ce7c6d2eb36718&sharer_shareinfo_first=fb8307e673915c06c1ce7c6d2eb36718#rd；实验评测已将固定模型提示词抽象为运行时无关契约。

### Unchanged

- 未修改 `ai-coding-guide/SKILL.md` description、交付状态机或 `settings.json`；该能力属于组合执行层，不新增主分类或触发前门。

## [v2.4.0] - 2026-08-31

### Added

- 增加最小可审计路由契约：`分类`、`主路径`、`组合`、`闸门`、`下一步`；按条件追加 `参与度` 与 `Matt提示`。
- 强调标准分类名、`guide-skill-auditor` 维护路径、可验证 `eval` 和 `small/medium/large` 交付档位。

### Fixed

- 对齐 `SKILL.md` 与 `references/routing.md` 的代码理解顺序：日常结构先用 `lean-ctx`，调用链或影响范围使用 `gitnexus-exploring`，组合请求按 `lean-ctx` → `gitnexus-exploring`。

### Evidence

- WikiSkill 登记 iteration-1 至 iteration-10，并从 `route-contract-drift` Pattern 提取重复回归。
- 9-case gate 套件：target 由 `0.50` 提升至 `0.75`，完整套件由 `7/9` 提升至 `8/9`；guardrail `4/4`、holdout `1/1` 保持通过。
- 评测执行错误单独归入 `benchmark-runtime-noise`，未与模型输出失败混算。

### Unchanged

- 保留原始 34 个 YAML 用例与 Raw Trace；当前 runner 验证使用隔离的 9-case 转换套件。
- 未修改 `settings.json`、`skill-up`、`C:\ZYS\Wiki`，未覆盖 Raw Trace、自动 commit 或 push。


## [v2.3.0] - 2026-08-20

### Fixed

- 明确 user-invoked skill 只能由用户逐个手动调用，不能静默串联另一个 user-invoked skill。
- 将调试、重构和需要改代码的构建修复纳入 `/grill-with-docs` 默认第一跳；纯诊断/解释仍可直接走对应路径。
- 将 `/implement` 的 `/code-review` 收尾从“按需”收紧为提交前必须完成；`/tdd` 仍按预先约定的 seam 使用。
- 放宽 `/to-tickets` 触发条件：需要显式阻塞关系时，即使不是跨会话、并行或多人任务也可使用。

### Added

- `test-prompts.json` 新增 5 个场景，覆盖修复型调试、重构、构建修复、显式阻塞拆票和 user-invoked 串联门禁。

### Evidence

- 官方仓库 `README.md:103`：建议每次变更前使用 `/grill-with-docs`。
- 官方仓库 `README.md:186`：user-invoked 不能调用另一个 user-invoked。
- 官方仓库 `README.md:200-201`：`to-tickets` 的适用能力、`implement` 的 TDD seam 和提交前 code-review。

## [v2.2.0] - 2026-08-20

### Changed

- 根据 Matt 官方 README 的“每次变更先使用 `/grill-with-docs`”建议，将非机械代码变更的默认第一跳提升为 `/grill-with-docs`。
- 保留 1-2 步单文件机械改动的精简路径，避免把文案、格式和明确小修强行套进访谈流程。
- 明确非机械变更讨论后按需要进入 `/to-spec`；跨会话、并行或多人协作时再加入 `/to-tickets`。

### Evidence

- 官方仓库 `README.md`：`Why These Skills Exist`、`Reference`；官方建议每次代码变更前使用 `/grill-with-docs`。
- 本地插件 `mattpocock-skills` v1.2.3 的 manifest、README 和 skill frontmatter；未将官方 `main` 中 README 未列出的实验/杂项 skill 纳入当前路由。



### Added

- 为 Matt 路由增加统一调用提示：输出具体 `/skill` 命令、自动/手动模式和下一步，不再只写“使用 Matt”。
- 明确 user-invoked skill 必须由用户手动调用并等待；model-invoked skill 可自动调用，但路由始终显示手动命令，用户明确要自己练时才等待。
- 补齐 Matt 主流程、条件跳步、单环路径、triage、wayfinder、prototype、handoff 和插件不可用时的降级边界。
- `test-prompts.json` 新增 14 个场景，覆盖手动入口、自动入口、主流程顺序、领域边界和 commit 确认。

### Fixed

- 修正 `code-review` 的 invocation 分类：当前 Matt v1.2.3 为 model-invoked，不再误标为 user-invoked。
- 修正 `to-tickets` 语义：只在跨会话、并行或多人协作时加入，不作为单会话主流程必经步骤。
- 修正 `tdd` 语义：`implement` 内部按需驱动；独立测试先行时才作为单独手动入口提醒。

### Evidence

- 当前插件事实：`mattpocock-skills` v1.2.3 的 plugin manifest、README invocation 分类和相关 `SKILL.md` frontmatter。
- 本地教程核对：`71-公众号文章/2026-08-07-全网爆火的-Matt-Pocock-Skills-保姆级教程-vibe-coding的最佳选择.md:95-103,112-181,290-306,345-347`；`71-公众号文章/2026-07-23-Matt-Pocock-skills-新手完整教程.md:33-75`。

### Unchanged

- 未修改 `settings.json`、插件缓存、DevFlow 状态机、权限判定和三域边界；未把 Matt skill 正文复制进 guide。

## [v2.0.0] - 2026-08-20

### Fixed

- 恢复 `references/fallback-template.md`，修复 `article-writing-guide/SKILL.md:196` 与 `learning-guide/SKILL.md:85` 指向活动目录不存在文件的问题。
- 统一 `inspect_context.py` 与 `workflow_state.py resume` 的对外相对路径为 POSIX `/`，修复 Windows 回归基线的 2 个失败。
- 将 GateGuard 恢复提示中的 Glob/Grep 改为当前工具链可用的 `ctx_tree`/`ctx_search`，不改变 gate 判定逻辑。

### Added

- 为路由器补充 `test-prompts.json`，覆盖域边界、前端视觉、高风险编码、快速改动、重任务、三域外独立工具等关键场景。
- 为 guide description 补充角色定位、触发条件和版本戳；保留现有 `evals/eval.yaml` 作为完整评测入口。

### Rationale

- 依据：2026-08-20 预修复基线 `20 passed, 2 failed`、活动 guide 的死引用、GateGuard 文案与 `settings.json:41-45` 的工具权限冲突。
- 未动：`references/routing.md` 未暴露新的路由误判；现有 34 个 `evals/cases` 保留，避免重复维护两套完整评测。
