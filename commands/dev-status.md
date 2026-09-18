---
description: 列出当前仓库的活跃会话、工作树、stash、端口与容器状态
argument-hint: "[仓库路径，留空取当前目录]"
---

运行下面这条命令，把输出原样呈现给用户：

```
C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe "C:/Users/zys31/.claude/hooks/scripts/session-status.py" $ARGUMENTS
```

输出已经分好组（活跃会话 / 工作树四类 / 孤儿目录 / stash / 主检出 / 仓库根散落文件 / 登记端口 / 容器）。

直接呈现，不要添加评价，不要主动建议清理。用户接着问再解读。
