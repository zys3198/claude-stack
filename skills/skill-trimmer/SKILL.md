---
name: skill-trimmer
description: 评估 Skill 库的保留、收窄、归档与新增。
disable-model-invocation: true
---
# Skill Trimmer — Skill 库精简判定

本 Skill 只做**库级**存在性、留删、收窄、归档和生命周期评估，不先假定候选应保留。判据来源分为 `【本机】`、`【外部】`、`【工具】`，出处与轻量数据证据见 [references/evidence-sources.md](references/evidence-sources.md)；详细留存分类见 [references/retention-rubric.md](references/retention-rubric.md)。

## 1. 存在性门禁

逐个候选按固定顺序判断：

1. **反向测试**：不使用候选 Skill 裸跑同一目标；若不能安全裸跑，记 `not-run`，不得据此判冗余。
2. **增量证据**：只有反复出现且代价高的失误，或模型稳定猜不到的判断、脚本、模板、资料、固定偏好，才支持独立保留。
3. **替代与生命周期**：检查模型、宿主文件、hook/CI/linter 和其他 Skill 是否已覆盖，以及近期使用和复现问题信号。

存在性结论只有：**保留独立 Skill**、**不需要独立 Skill**、**证据不足待验证**。静态规范、文件存在或成功加载不等于收益；拿不准必须补运行验证。

## 本机边界

安装根目录由本 Skill 自身所在的 `skills/skill-trimmer/scripts/` 推导，脱离标准目录时用 `SKILL_TRIMMER_HOME`；`skills/` 下的候选都是实际目录；插件 Skill 由插件控制面管理，不在本 Skill 的逐个判定范围内。

## 1.1 用户确认与安全门禁

- AI 只出建议，分类和移除由用户逐项拍板；移动是移目录到 `archive/_weak-model-backup/` 或实验目录，不等于纯删除。
- 含危险命令、过宽权限、外部副作用或安全性不明的候选，先隔离并进入「删前用户确认」，不因看似有用默认放行。
- 被 router 引用的 D 类按本机决议列为「移除+改路由」并同步消除死引用；流程型/E 类保留弱模型复杂任务兜底，只有纯 D 类、零引用、无资产才进入移除候选；同能力多个只留 router 指定主路径。

## 2. 判定流程

1. **定范围与停止点**：先写候选、目标和本轮停止条件；证据足够归类就停，不扩成全库审查。
2. **盘点**：在宿主 `skills/` 目录执行 `python skill-trimmer/scripts/scan_skills.py`；它生成安装根目录旁的 `skill-trimmer-workspace/inventory.json`。来源、使用、mtime、上下文成本和测量等级读取 `references/evidence-sources.md`，不把不可用写成 0。
3. **装前评估**：问「模型原本会吗、是否反复翻车、是否有脚本/模板/资料/偏好、过期能否发现」；先读候选 `SKILL.md`，存在 `scripts/`、`references/`、权限或外部副作用时再读相关材料，安全不明就停。
4. **引用扫描**：记录每个候选被 router、其他 Skill、`CLAUDE.md` 或项目引用的方；引用是改路由清单，不是免删名单。
5. **逐个判定**：按 Expert / Activation / Redundant、资产、偏好/方向、使用面、套件时机、工程体检、生命周期、触发面和运行验证分类；详细表见 `references/retention-rubric.md`。
6. **验证差异**：轻量验证用同任务 baseline/candidate，记录输入、环境、实际输出、完成标准和 `passed` / `failed` / `blocked` / `not-run`；结果将决定留删或不确定时，才进入正式 target/guardrail/holdout 验证。

## 3. 报告与拍板

每组最多五项，输出：

```text
| skill | 存在性结论 | 分类/动作 | 范围/停止点 | 关键理由 | 引用情况 | 运行证据 | 生命周期 |
```

另列静态检查、运行验证、使用信号三层证据；缺失写「未验证」。报告不自动执行移动、删除或改路由。用户拍板后，才可按确认范围同步路由和归档；生产、权限、外发、不可恢复删除仍遵守更高确认线。

## 4. 可选网页复审

需要用户在本地页面拍板时，先校验再启动，停止后读取决定：

```bash
python skill-trimmer/scripts/review_server.py validate --inventory ../skill-trimmer-workspace/inventory-review.json
python skill-trimmer/scripts/review_server.py serve --inventory ../skill-trimmer-workspace/inventory-review.json --profile "local"
python skill-trimmer/scripts/review_server.py read --require-complete
```

契约见 `references/audit-contract.md`，实现为本目录 `scripts/review_server.py` 与 `assets/review.html`。页面只存 `global` / `project` / `trigger` 决定，不自动执行移动；`trigger` 需 2–5 个自然语言短语，`RARE_CRITICAL` 需二次确认。

## 5. 触发空壳合同

`移入备份`、`移除+改路由`、`移除-被覆盖`、`移入 CLAUDE.md` 等归档动作保留触发空壳：名称、一句话能力摘要、2–5 个触发词、归档位置、项目恢复方式和观察截止日。命中只提示已归档，未经明确同意不恢复、不复制、不执行；观察期 60 天，`RARE_CRITICAL` 不因低频自动删除。

## 数据驱动

当前没有遥测时只使用可核的 mtime、引用方、台账、用户实测和运行输出；状态标为 `active`、`stale` 或 `archived`。单个 Skill 的设计/运行审计转 `skill-auditor`；跨指令文件审查转 `instruction-engineering`。
