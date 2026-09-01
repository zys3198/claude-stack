开工路由判断如下（仅路由，不执行）。

## 路由契约

**触发门禁**
- article-writing-guide 相关？**YES（次级）** —— 请求含「教程/沉淀成文章」的写作产出成分，但主诉求是「给自己学会 + 边做边学」，属学习域
- 主域 skill：`learning-guide`（本会话 available，可委派）

---

### ① 分类
- **主域：学习域（learning-guide）**，非写作域主任务
- **教程裁决**：「给自己学会/作为学习产物」→ 明确命中 `learning-guide`；「面向读者发布的教程文章」才是 `tutorial-maker`
- 写作成分：仅当学习后要**沉淀成可读文章**时，才作为下游承接走写作域「边学边写」

### ② 主路径
- `learning-guide`（先学：产出学习路径 + 关键心智模型）→ **学习完成后**，若要把成果写成文章/教程：article-writing-guide §3 边学边写 pipeline（`agent-reach` 收集权威材料 → 轻量学习路径 → 对话增量初稿 → 用户确认 → `edit-article` 落盘）
- **不走** `tutorial-maker`（那是对外发布系列课的路径）；**不走** `article-writer` 直接起草（尚无学习记录可作现稿）

### ③ 组合
- 主：`learning-guide`（学习路径规划）
- 可选下游（按产出形态叠加）：边学边写写作流 → `tech-article-review`（事实核查，产出文章时）→ `chinese-markdown-normalizer`（排版）→ `publish-final-check`（仅对外发布时）
- **不组合**：`tutorial-maker`（除非你改口说「要对外发布」）、JavaGuide 模式（见闸门）

### ④ 闸门
| 闸门 | 状态 |
|------|------|
| 教程裁决门 | 已过：明确「给自己」→ learning-guide |
| **JavaGuide 模式门** | 你说了「Java 教程」但**未含「JavaGuide」关键词**，不触发 JavaGuide 模式——提醒防误判 |
| 写入闸门 | 边学边写落盘前，先在对话给增量初稿，你确认后才写文件 |
| 交付物形态分叉 | 需你定：纯学习路径（自用） vs 学习 + 沉淀成对外教程（后者才接写作域全链） |
| 学习角色门（CLAUDE.md） | 学习时刻先问学习角色：peer 对练 / teacher 苏格拉底 / research 查证，带推荐 |

### ⑤ 下一步
只做一件事：**确认交付物形态 + 学习者背景**——① 你是零基础还是已有编程经验？② Java 学习目标（找工作/看懂项目/写业务）？③ 学完是否要沉淀成对外教程？
你答完这三点，我据此开 `learning-guide` 的开工问询，不再继续往下。

---
