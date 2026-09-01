域归属：编码（开发新功能 + 工具选型）/ ai-coding-guide 在当前会话：YES

按 routing.md Step 1，命中「开发新功能」信号；附带「用 SP 还是 ponytail」属于工具选型，按规则先给 A/B/C 而非泛泛介绍。

---

**分类：** 开发新功能（登录 / auth / 高风险域）  
**主路径：** `superpowers:writing-plans` → 先出登录实现计划（范围、栈、安全边界、接口/状态/错误处理）  
**组合：** `ponytail:ponytail`（计划确认后做最小实现）+ `security-review`（auth 必须专项审查）+ `verification-before-completion`（条件路径，会话可见）  
**闸门：** 设计确认 → 失败测试/TDD → 安全审查 → verify（登录属于 auth，按 Step 0.6 走高风险闸门）  
**下一步：** 先确认两个问题再推进——①「SP」是否指 `superpowers`？② 登录范围是「前端登录页」「后端认证 API」还是「完整前后端认证流」？确认后可直接进 `superpowers:writing-plans`。
