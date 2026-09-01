域归属：编码（bug 修复后的验证与提交收尾）  
ai-coding-guide 在当前会话：YES

路由契约：

- **分类**：横切收尾（bug 修复后的完工验证 + 提交确认）
- **主路径**：先跑项目已有验证命令（test / lint / build / run），通过后进入 git 提交确认
- **组合**：`superpowers:verification-before-completion`（当前会话可用）+ 内置 `code-review` 轻量审当前 diff
- **闸门**：相关测试/构建/类型检查通过；`git diff --cached --stat` 确认改动范围；用户明确确认后才执行 commit
- **下一步**：直接执行验证与提交前检查；若验证命令或提交范围不明，先问「跑哪个命令验证 + 是否 push / 目标分支」
