路由判断如下：

- **分类**：非交付型内容审查任务（中文技术文章审校 / 事实与表达纠错），**不属于编码交付**，因此 ai-coding-guide 仅作入口分诊，不进入其"必须执行"状态机。
- **主路径**：由 ai-coding-guide 分诊至 `tech-article-review`（技术文章审校）或 `article-writing-guide`（中文技术写作流程），二者均以内容质量、技术准确性和表达规范为审查目标。
- **组合**：基础审查用 `tech-article-review`；若文章中包含代码示例、API 用法或框架声明，可叠加 `plugin:context7:context7` 或 `claude-api` 做事实核验。
- **闸门**：当前缺少**文章原文或文件路径**，无法执行审查。
- **下一步**：请用户粘贴待审文章全文，或提供本地文件路径；确认内容后，再调用 `tech-article-review` / `article-writing-guide` 进入实际审查。
