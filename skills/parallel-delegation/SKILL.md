---
name: parallel-delegation
description: 规划边界清楚、可独立验收的单个或并行子代理任务；涉及模型、effort、并发或隔离时先走确认门禁。
compatibility: 需要宿主提供 agent/subagent 调度能力；模型、effort、并发和隔离能力以运行时实际暴露为准。
---

# 子代理委派

本 Skill 只保留触发面。命中它意味着：**接下来要派子代理**。

规划前**必须读取 `~/.claude/docs/protocols/delegation.md`**——Route、留在主代理的活、Boundaries、Configuration gate 和失败判据都在那里，本文件不复述。启动前的配置展示与确认是硬门禁：常规单个委派也不豁免。
