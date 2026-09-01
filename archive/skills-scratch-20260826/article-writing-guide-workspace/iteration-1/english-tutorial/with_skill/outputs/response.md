# 路由契约

## 触发门禁
- **article-writing-guide 相关？** YES —— 写作任务（英文教程）且未点名具体 skill，需路由分发
- **目标 skill 在当前会话？** YES —— `article-writer`、`edit-article` 均在可用列表
- 替代：无需

## 分类
**跨阶段写作任务（起草 + 编辑）｜ 英文 ｜ 单篇教程（非系列课，不走 `tutorial-maker`）｜ 教程裁决：面向读者发布的教程文章 → 写作域**

## 主路径
- **起草** → `article-writer`（默认通用模式，单篇教程适用；英文可走）
- **编辑** → `edit-article`（结构/逻辑改写；英文可走）
- **明确跳过**：`human-writing`（去 AI 味）、`chinese-markdown-normalizer`（排版）——语言边界：英文文章跳过中文专用 skill

## 组合
`article-writer`（起草）→ `edit-article`（编辑）
可选尾环（本次未点名，可后续加）：`drawio-article-illustration` 配图 → `tech-article-review`/`multi-review-pipeline` 审校 → `publish-final-check` 发布闸

## 闸门
1. **跨阶段 CHECKPOINT**（§4 规则3）：写+编为跨阶段，需先确认「跑全链路 / 只跑写+编 / 单点」——你已点名两阶段，需再确认是否含配图/审校/发布尾环
2. **写入闸门**（§4 规则4）：起草与改写先给对话预览，你确认后才落盘
3. **写作纪律**：Docker networking 属事实性内容，须附**依据表 + basis map**（依据优先 Docker 官方文档/实测，缺失标 `needs evidence`，不得装成事实）
4. **决策点先问**（§4.5）：文体已定（tutorial），但**读者/深度/篇幅/是否有参考**未明，开工前补齐

## 下一步
确认两件事即可开工委派 `article-writer`：① CHECKPOINT 范围（只写+编，还是含尾环）；② 三要素补全（目标读者、覆盖深度——如 bridge/overlay/DNS/端口映射，篇幅）。本次仅路由判断，未执行任务。
