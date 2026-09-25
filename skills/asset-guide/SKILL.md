---
name: asset-guide
description: 新增、修改、迁移或删除 Claude Code 资产前，先确定其类型、唯一入口、元数据、索引和生命周期。
---

# 资产引导

把「资产 → 加载形态 → L0」这套机制用到具体对象上。判据不在本文件：九条原则、加载形态四格与映射表在 `~/.claude/rules/principles.md`（常驻）；文档怎么写、怎么分层、怎么剪除，动笔前**必读** `/writing-for-agents`——里面是两个负担、信息层级、正面陈述、锚定词、context pointer、拆分与剪除的判据。

## 八步

一步只做一件事，做完再进下一步。

| 步 | 动作 | 判据出处 |
|---|---|---|
| 1 | **查重**：全库检索这条知识是否已有一处权威；命中就改那一处，不新建 | `principles.md` 的 B4 引用 > 复制；`docs/protocols-index.md`「维护条款」的删除判据 |
| 2 | **定类型**：落进映射表的哪一行（skill／rules／协议文档／记忆／台账／hook／索引）；选不出类型的，通常说明它不该存在 | `principles.md` 映射表 |
| 3 | **定位 L0**：这类资产的常驻入口是谁——常驻文件、model-invocable skill 的 `description`、索引一行 | 同上，「L0 由谁提供」列 |
| 4 | **写元数据**：按类型走各自那份协议；`rules/*.md` 只写 `paths`，其余字段平台静默忽略 | `docs/protocols/memory.md`、`install-ledger`、`docs/protocols-index.md` 的共同要求 |
| 5 | **最小正文**：只留触发条件、判据与动作；概念与阶梯不在本机复述 | `/writing-for-agents` |
| 6 | **指针**：要全文时按名字引用（skill 名、协议路径），不复制正文，不写带版本号的缓存路径 | `/writing-for-agents` §Context pointers |
| 7 | **更新索引**：协议进 `docs/protocols-index.md`；路径规则进 `CLAUDE.md` §2；记忆进 `MEMORY.md`；资产进台账现状表并追加流水 | `docs/protocols-index.md`、`install-ledger` |
| 8 | **设生命周期**：命名与日期用 `YYYY-MM-DD`、写状态词、留过期与删除判据；删除动作本身走确认线 | `docs/protocols-index.md`「落点与命名」与「维护条款」 |

收尾跑一次 `python ~/.claude/hooks/scripts/protocol_check.py`——机器判据只在那一处实现。判定一条资产该留、该收窄还是该归档，用 `asset-auditor`（用户显式运行，它只出建议、不删）。

## 维护条款

**事后判据**：本正文若压到十几行以内，并入 `~/.claude/rules/principles.md`，不再独立成 skill。
