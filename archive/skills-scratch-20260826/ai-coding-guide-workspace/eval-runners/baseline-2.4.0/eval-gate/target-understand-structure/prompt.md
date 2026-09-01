---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

请用 ai-coding-guide 做开工路由判断：只输出「分类 / 主路径 / 组合 / 闸门 / 下一步」，不要执行任务本身。
请求：我只想快速看一个类内部的实现结构，不查引用、不查调用链，也不修改代码。应该先用什么？