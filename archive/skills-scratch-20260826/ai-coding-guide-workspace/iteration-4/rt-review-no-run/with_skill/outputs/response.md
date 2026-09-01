触发门禁：

- **域归属**：编码（审查代码）
- **ai-coding-guide 在当前会话**：YES
- **非编码域**：否，留在本路由

---

**分类**：审查代码  
**主路径**：`code-review`（审当前 diff）  
**组合**：`security-review` + 通用 Code Reviewer agent（auth 变更属高风险域，双审防盲区）  
**闸门**：security-review + Code Reviewer 双审；不运行程序、不提交、不改代码  
**下一步**：直接执行 review，先定位当前 diff 范围，再分安全与一般正确性两条线审

---

**关键一句**：auth 变更按 `routing.md` 风险矩阵进高闸门，必须叠加 `security-review`；用户已明确「不要运行程序」，故跳过横切收尾的 verify/run。
