---
name: preflight-check
description: 多步任务/命令序列开工前环境预检——验证 repo root、目标路径存在性、文件编码、容器路径、shell 引号易碎点。触发：多步任务、跨目录、涉及容器路径/编码/shell 引号假设时。只验证不执行，猜错即停。
---

# 环境预检

多步任务开工先验证环境假设，不猜。来源：/insights 2026-08-14 friction #1（git add 错 repo root / JSON 引号断裂 / GBK 乱码）。

## 何时跑

- 多步任务开工前
- 首次涉及路径/编码/容器/shell 引号假设时

## 检查清单

每项 = 一条命令 = 一个可见输出。

1. **repo root**：`git rev-parse --show-toplevel`；非 repo 用 `pwd` 确认当前目录。拿相对路径前先确认 root。
2. **目标路径存在性**：`Test-Path <dir>`（PowerShell）/ `ls <dir>` 关键目录存在，再操作。不拿相对路径猜。
3. **文件编码**：写文件强制 `encoding='utf-8'`；读未知来源文件先探测——BOM 检查或用 python 探测实际编码，不假设 UTF-8 无 BOM。
4. **容器路径**：docker 场景先 `docker exec <容器> ls <容器内路径>` 验证存在，不猜容器内路径。
5. **shell 引号**：JSON/复杂参数写临时文件传递，不内联嵌套转义。引号易碎即换文件。

## 纪律

- 每次检查结果一句话汇报：`root=… / 编码=utf-8 / 路径存在`，不展开。
- 连续 2 次同方式失败 → 停止，换方案（CLAUDE.md §6.2），不反复盲改路径/引号/转义。

## Windows 注意

- `Test-Path` 验证路径；`pathlib` 处理路径；Windows 下不 symlink（copy）。
- 防 GBK 乱码：`os.environ` 合并 `PYTHONIOENCODING=utf-8`，子进程读取显式指定编码（CLAUDE.md §6.1）。
