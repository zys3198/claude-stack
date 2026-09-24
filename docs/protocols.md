# 协议总表

每个领域一份协议，各管各的。协议写在对应 skill 里（固定小节或 `references/`），本表只做索引：哪份协议在哪、怎么校验。

新增一份协议时，在本表加一行。

| 领域 | 协议在哪 | 校验 | 状态 |
|---|---|---|---|
| 台账 | `~/.claude/skills/install-ledger/references/ledger-protocol.md` | `python ~/.claude/skills/install-ledger/scripts/ledger_check.py` | **已落** |
| 任务笔记 | `~/.claude/skills/task-notes/SKILL.md` | — | **已落** |
| 执行环境 | `~/.claude/skills/docker-only/SKILL.md` | `~/.claude/hooks/scripts/resource-guard.py`（PreToolUse） | **已落** |
| 记忆 | `~/.claude/docs/protocols/memory.md` | `python ~/.claude/hooks/scripts/protocol_check.py` | **已落** |
| 委派 | `~/.claude/skills/parallel-delegation/SKILL.md` + `references/` | — | **已落** |
| 门禁 | `~/.claude/docs/protocols/gate.md`（操作规则留在 `~/.claude/CLAUDE.md` §1.3） | `python ~/.claude/hooks/scripts/protocol_check.py` | **已落** |

门禁与记忆共用一个脚本，两者分开报，退出码 0 才算全过。`任务笔记` 与 `委派` 的校验留 `—`：前者的产物是各项目仓库里自由形态的记录，后者是 prompt 模板，磁盘上都没有可判的固定形态。源路径已删的项目的记忆不再被加载，脚本把它们单独分组计数、不细查。

## 共同要求

协议之间可以不一样，但每条都要满足：

1. **有固定落点** — 写在哪、读哪一份，不含糊。
2. **有固定字段** — 顺序和取值枚举写死，不靠自由发挥。
3. **有判据** — 什么进、什么不进，用一句话能判。
4. **可机械校验** — 能写成一个只读检查的，就该有；没有就写 `—`。
5. **渐进式披露** — 每次触发都要用的留在主文件，只在特定情形用的下沉到 `references/`。
6. **有维护条款** — 写清可变区与只增区的分界、删除判据、整理触发点。见下。

## 维护条款

文档只增不整理就会沉积，沉积到最后不敢删——因为分不清哪条还活着。每份协议正文里要写明三条：

**一、分界。** 会变的（现状、清单、规则）必须能整体重写；只增的（依据、历史）只追加，写完不改。混在一起就没法整理。

**二、删除判据。** 满足其一即删：

| 情形 | 动作 |
|---|---|
| 内容已在环境里（配置文件、代码、`--help` 输出） | 删——它是缓存，会过期 |
| 被本文档后面的条目覆盖 | 删旧条——两条并存会让新旧规则同时生效 |
| 只在部分情形才用到 | 下沉 `references/`，不删 |
| 指向的目标已不存在 | 删引用，或改指向 |

**三、触发点。** 每次编辑这份协议时顺手做一遍，不设「定期整理」（定期整理不会发生）。另加体量硬触发：正文逼近上限（默认 20 KB，可由协议自定）就强制复核，先删再加。
