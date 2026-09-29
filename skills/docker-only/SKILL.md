---
name: docker-only
description: 构建、测试、安装依赖、运行脚本或启动服务时，使用受限容器流程；宿主机仅做只读查看、Git 和 Docker 管理。
---

# Docker 执行环境

本 Skill 只保留触发面。命中它意味着：**宿主机不跑构建、测试与脚本**。

动手前**必须读取 `~/.claude/docs/protocols/execution-env.md`**——容器去处选择、`docker run` 资源上限模板、可销毁边界、已确认的授权范围、收尾清理与 hook 行为全在那里，本文件不复述。
