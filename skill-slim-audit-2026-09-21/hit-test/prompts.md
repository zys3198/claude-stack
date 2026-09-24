# 第一跳命中测试集

对每条请求，判定「只看 skill 列表（name + description）时，第一跳会选谁」。可选答案是下面 10 个之一，或 `NOTHING`（现有 skill 都不该命中，模型直接处理）。

判定只看 description 里的措辞信号，不借助你对这些 skill 具体内容的先验印象。若两条都说得通，选信号更贴的那条，并在「歧义」列标出另一条。

固定清单（两版共有，顺序也一致）：

- dev-status-by-user
- dev-clean-by-user
- bidirectional-steelman-by-user
- toolchain-pitfalls-by-user
- parallel-delegation-by-user
- docker-only-by-user
- install-ledger-by-user
- task-notes-by-user
- article-writer-by-user
- coding-workflow-by-user

## 请求清单

| # | 用户请求原文 |
|---|---|
| 1 | 看看这个仓库现在什么情况，有哪些会话在工作 |
| 2 | 现在哪些端口被占用了 |
| 3 | 清理一下那些没用的空工作树 |
| 4 | lab-area 里散落的临时文件清一下 |
| 5 | 我准备写个脚本批量处理这些文件，先帮我看看有没有坑 |
| 6 | 派几个子代理去查这几个模块 |
| 7 | 这三块任务能不能并行做 |
| 8 | 我要装个依赖跑测试 |
| 9 | 在容器里跑一下这个服务 |
| 10 | 刚装了个插件，帮我记录一下 |
| 11 | 这个 skill 是从哪来的，台账里有吗 |
| 12 | 我要装一个新插件，教我怎么装 |
| 13 | 接着上次的任务继续做 |
| 14 | 帮我把这个任务的接续状态记一下 |
| 15 | 帮我写一篇公众号文章 |
| 16 | 把这段技术方案改写成博客 |
| 17 | 帮我写个 Python 从零入门的系列教程 |
| 18 | 这段代码有 bug，帮我修一下 |
| 19 | 重构一下这个模块 |
| 20 | 帮我 review 一下这个 PR |
| 21 | 我这个方案该不该上 |
| 22 | 帮我从反面想想这个决定 |
| 23 | 1+1 等于几 |
| 24 | 帮我查一下 Python 的 asyncio 怎么用 |
| 25 | 把这段会议记录整理成一句话 |
| 26 | 这个报错是什么意思，帮我看看 |
| 27 | 帮我写一篇讲 React Hooks 的深度文章 |
