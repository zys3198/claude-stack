**域归属：** 编码（调试 bug 定位）/ 当前会话已启用 `ai-coding-guide` → 继续本路由  
**ai-coding-guide 在当前会话：** YES  

---

**分类：** 调试 bug（定位阶段，明确不修代码）  
**主路径：** `superpowers:systematic-debugging`（当前会话可用，专用于"定位先于修复"）  
**组合：** `code-change-workflow` §2 调试工作流作为后续修复阶段的 fallback；如需要结构化诊断可叠加 `mattpocock-skills:diagnosing-bugs`  
**闸门：** 复现证据 / 根因证据（只定位不改代码，不触发 review/verify；但必须补全失败测试或稳定复现）  
**下一步：** 先收齐 Step 0.7 调试缺口（复现步骤、期望 vs 实际、错误原文、最近改动），再启动 `systematic-debugging` 定位根因
