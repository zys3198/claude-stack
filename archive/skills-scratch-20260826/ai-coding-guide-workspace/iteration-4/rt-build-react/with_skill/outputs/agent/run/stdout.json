路由判断如下：

- **分类**：构建错误（React 项目 build 失败）
- **主路径**：直接排查——先以 `python3 <SKILL_ROOT>/scripts/inspect_context.py .` 读取项目约定（package scripts / 依赖 / 框架版本），再执行项目既有 build 命令并按完整错误日志定位根因。
- **组合**：需要时 `lean-ctx` 定位报错源码；条件路径 `plugin:context7:context7` 查 React 官方文档（当前会话已连接）。当前无 React 专项 resolver skill，不走其他条件路径。
- **闸门**：中风险——必须拿到「build 命令 + 完整错误原文 + 最近改动」才修；修复后必须重新 build 通过，否则不得交付。
- **下一步**：用户提供 build 命令、完整错误日志和最近改动；或授权我在当前目录执行 build 抓取日志后，再进入排查。
