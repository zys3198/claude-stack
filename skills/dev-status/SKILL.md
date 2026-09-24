---
name: dev-status
description: 仓库状态：活跃会话、工作树、stash、端口与容器占用。
argument-hint: "[仓库路径，留空取当前目录]"
---

运行下面这条命令：

```
C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe "C:/Users/zys31/.claude/hooks/scripts/session-status.py" $ARGUMENTS
```

输出已经分好组（活跃会话 / 工作树四类 / 孤儿目录 / stash / 主检出 / 上次会话遗留 / 仓库根散落文件 / 登记端口 / 容器）。

把输出原样呈现给用户，不加评价。解读和清理建议留到用户追问时。
