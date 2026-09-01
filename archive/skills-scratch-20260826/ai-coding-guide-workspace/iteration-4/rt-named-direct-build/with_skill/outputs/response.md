域归属：编码（React 项目 build 报错，工程排障）  
ai-coding-guide 在当前会话？YES  

**分类**：构建错误  
**主路径**：直接执行项目已有构建命令并按错误原文定位修复；React 框架可由 `inspect_context.py` 取证识别，免问语言/框架  
**组合**：当前会话无 React 专项 resolver，必要时回退到 `code-change-workflow` 调试工作流  
**闸门**：修复后 `build`（含 `lint` / `type-check`）必须通过；涉及清理/删除未跟踪文件需单独确认  
**下一步**：直接执行：取证 manifests → 跑 build → 按错误链排查修复
