---
name: asset-auditor
description: 审计 ~/.claude 资产库的留存、收窄、归档或新增决策，覆盖映射表中的全部资产类型；只出建议，不执行删除、迁移或改路由。
disable-model-invocation: true
---
# Asset Auditor — 资产库留存判定

本 Skill 只做**库级**存在性、留删、收窄、归档和生命周期评估，不先假定候选应保留。判定对象是资产原则文件映射表里的**每一类资产**，不止 skill。判据来源分为 `【本机】`、`【外部】`、`【工具】`，出处与轻量数据证据见 [references/evidence-sources.md](references/evidence-sources.md)；详细留存分类见 [references/retention-rubric.md](references/retention-rubric.md)。

## 0. 资产类型映射表（换资产类时唯一要改的地方）

资产类目、加载形态、L0 入口以 `~/.claude/rules/principles.md` 的「资产 → 形态 → L0」表为单一事实源，此处不复制。本表只补审计特有的两列。机械判据（命名／frontmatter／索引／体积／重复／密钥／生命周期／映射表）一律跑 `hooks/scripts/protocol_check.py`——它是唯一检查实现；本 Skill 不复制判据，只做需要判断的部分（存在性、归属、生命周期、留删建议）。

| 资产类 | 候选全集怎么拿 | 判定基准 |
|---|---|---|
| skill | `scripts/scan_skills.py` → 安装根目录旁 `skill-trimmer-workspace/inventory.json` | `retention-rubric.md` 全表（含触发面、描述预算、套件时机这些 skill 专项档） |
| 常驻指令 `CLAUDE.md`、`rules/*.md` | 直接读文件与其索引指向的文件 | 归属分层（rubric 三节）：该常驻、该条件加载，还是该挪进 skill |
| `docs/protocols/*.md` | 枚举目录 + 与 `protocols-index.md` 对账 | 四问 + 生命周期（rubric 一、九节） |
| memory | 枚举 `projects/*/memory/` + `MEMORY.md` | 四问 + 索引一致性 |
| `notes/<任务名>/` | 枚举目录 | 不审留删——证据区，只审「该不该进 notes」 |
| hook | `settings.json` 各事件 + `hooks/` | 触发契约与失败模式；判定细则借 `skill-auditor` 十查 |
| 台账／备份／授权记录 | 目录名 | 不适用「只放必要」，见原则文件「边界」一节 |

skill 类独有的两样东西：网页复审通道（第 4 节，复审运行时只吃 `skills` 数组），以及触发面／描述预算判据。其他资产类走第 3 节的报告表。

## 1. 存在性门禁

逐个候选按固定顺序判断：

1. **反向测试**：不使用候选资产裸跑同一目标；若不能安全裸跑，记 `not-run`，不得据此判冗余。
2. **增量证据**：只有反复出现且代价高的失误，或模型稳定猜不到的判断、脚本、模板、资料、固定偏好，才支持独立保留。
3. **替代与生命周期**：检查模型、宿主文件、hook/CI/linter 和其他资产是否已覆盖，以及近期使用和复现问题信号。

存在性结论只有：**保留独立资产**、**不需要独立资产**、**证据不足待验证**。静态规范、文件存在或成功加载不等于收益；拿不准必须补运行验证。

## 本机边界

安装根目录由本 Skill 自身所在的 `skills/asset-auditor/scripts/` 推导，脱离标准目录时用 `SKILL_TRIMMER_HOME`；状态目录名 `skill-trimmer`／`skill-trimmer-workspace` 与日志前缀 `[skill-trimmer]` 是**内部程序标识，不随 skill 改名**（改了已有状态数据会失联）。`skills/` 下的候选都是实际目录；插件 Skill 由插件控制面管理，不在本 Skill 的逐个判定范围内。

## 1.1 用户确认与安全门禁

- AI 只出建议，分类和移除由用户逐项拍板；移动是移目录到 `archive/_weak-model-backup/` 或实验目录，不等于纯删除。
- 含危险命令、过宽权限、外部副作用或安全性不明的候选，先隔离并进入「删前用户确认」，不因看似有用默认放行。
- 被 router 引用的 D 类按本机决议列为「移除+改路由」并同步消除死引用；流程型/E 类保留弱模型复杂任务兜底，只有纯 D 类、零引用、无资产才进入移除候选；同能力多个只留 router 指定主路径。

## 2. 判定流程

1. **定范围与停止点**：先写候选、目标资产类和本轮停止条件；证据足够归类就停，不扩成全库审查。
2. **盘点**：按第 0 节映射表取候选全集。skill 类在宿主 `skills/` 目录执行 `python asset-auditor/scripts/scan_skills.py`，它生成安装根目录旁的 `skill-trimmer-workspace/inventory.json`；其他资产类直接枚举目录或读索引。来源、使用、mtime、上下文成本和测量等级读取 `references/evidence-sources.md`，不把不可用写成 0。
3. **装前评估**：问「模型原本会吗、是否反复翻车、是否有脚本/模板/资料/偏好、过期能否发现」；先读候选本体，存在 `scripts/`、`references/`、权限或外部副作用时再读相关材料，安全不明就停。
4. **引用扫描**：记录每个候选被 router、其他 Skill、`CLAUDE.md` 或项目引用的方；引用是改路由清单，不是免删名单。
5. **逐个判定**：按 Expert / Activation / Redundant、资产、偏好/方向、使用面、生命周期和运行验证分类；详细表见 `references/retention-rubric.md`。套件时机、触发面、描述预算三档是 skill 专项，其他资产类跳过。
6. **验证差异**：轻量验证用同任务 baseline/candidate，记录输入、环境、实际输出、完成标准和 `passed` / `failed` / `blocked` / `not-run`；结果将决定留删或不确定时，才进入正式 target/guardrail/holdout 验证。

## 3. 报告与拍板

每组最多五项，输出：

```text
| 资产 | 类型 | 存在性结论 | 分类/动作 | 范围/停止点 | 关键理由 | 引用情况 | 运行证据 | 生命周期 |
```

另列静态检查、运行验证、使用信号三层证据；缺失写「未验证」。报告不自动执行移动、删除或改路由。用户拍板后，才可按确认范围同步路由和归档；生产、权限、外发、不可恢复删除仍遵守更高确认线。

## 4. 可选网页复审（skill 类）

需要用户在本地页面拍板时，先校验再启动，停止后读取决定：

```bash
python asset-auditor/scripts/review_server.py validate --inventory ../skill-trimmer-workspace/inventory-review.json
python asset-auditor/scripts/review_server.py serve --inventory ../skill-trimmer-workspace/inventory-review.json --profile "local"
python asset-auditor/scripts/review_server.py read --require-complete
```

契约见 `references/audit-contract.md`，实现为本目录 `scripts/review_server.py` 与 `assets/review.html`。页面只存 `global` / `project` / `trigger` 决定，不自动执行移动；`trigger` 需 2–5 个自然语言短语，`RARE_CRITICAL` 需二次确认。契约的 inventory 只认 `skills` 数组，其他资产类不走这条通道。

## 5. 触发空壳合同

`移入备份`、`移除+改路由`、`移除-被覆盖`、`移入 CLAUDE.md` 等归档动作保留触发空壳：名称、一句话能力摘要、2–5 个触发词、归档位置、项目恢复方式和观察截止日。命中只提示已归档，未经明确同意不恢复、不复制、不执行；观察期 60 天，`RARE_CRITICAL` 不因低频自动删除。

## 数据驱动

当前没有遥测时只使用可核的 mtime、引用方、台账、用户实测和运行输出；状态标为 `active`、`stale` 或 `archived`。机械判据跑 `protocol_check.py`，不在本 Skill 重写。单个 Skill 的设计/运行审计转 `skill-auditor`；跨指令文件审查转 `instruction-engineering`。
