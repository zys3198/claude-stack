# ai-readable-project 设计文档

> 设计来源：微信文章《从胡言乱语到精准改代码：我是如何让 AI 读懂老项目的》（腾讯技术工程，2026-08-07）
> 原文链接：https://mp.weixin.qq.com/s/acuC164Eh_5bfQJfS8hOXg

## 一、目标

让一个项目能被 AI 看懂：产出「AI 上下文工程」静态上下文（CLAUDE.md + AGENTS.md 知识索引 + 模块领域说明），并沉淀长期维护规则，使项目能持续被 AI 维护。

## 二、决策记录

| 决策点 | 结论 | 依据 |
|--------|------|------|
| 目标范围 | 静态上下文 + 长期维护 | 用户选择；文章 §从 AGENTS.md 开始 + §知识落盘规范 |
| 交付形态 | 输出分析 + 草稿，不直接改项目 | 用户选择 |
| 触发方式 | 显式触发 | 用户选择 |
| 面向项目 | 通用优先（新旧项目） | 用户选择 |
| 挂靠方式 | 纯独立 skill，不接 guide 路由 | 用户选择 |
| 问答强度 | 强约束问答：未确认项标记「未验证」 | 用户选择 |
| 文件策略 | CLAUDE.md 用 @AGENTS.md 导入，单源双生态 | 官方文档：Claude Code 不读 AGENTS.md，只读 CLAUDE.md，官方推荐 @ 导入 |
| 模块落盘 | 草稿集中产出 `docs/ai-context/modules/`，落地时就近放置到模块目录 | 审查修正：调和「集中产出」与「就近落盘」 |

## 三、产物结构

```
docs/ai-context/                 # 产出目录（不污染项目）
  CLAUDE.md 草稿                  # 壳：@AGENTS.md 导入 + Claude Code 特有内容
  AGENTS.md 草稿                  # 源：知识索引 + 项目规范
  analysis-report.md              # 分析报告：模块切分、依赖、真实运行链路、债务观察
  modules/                       # 模块说明（可选，按需生成）
    <module>-AGENTS.md
```

落地：用户审阅后自行将 AGENTS.md/CLAUDE.md 放置到根目录。

## 四、执行流程

1. **摸底**：目录树、语言/框架、构建配置、README
2. **模块切分**：核心模块 + 依赖关系
3. **真实链路识别**：入口/路由/构建产物，区分活代码 vs 死代码（引用 ≠ 运行）
4. **领域知识提炼**：业务背景、架构、规范、三方对接
5. **强约束问答**：向负责人确认运行真相、债务、文档位置；未确认项标记「未验证」
6. **产出**：报告 + CLAUDE.md/AGENTS.md/模块草稿

## 五、维护规则（写入 AGENTS.md 草稿）

- 根目录 AGENTS.md 和 CLAUDE.md 只保留索引概要（路径 + 1~2 句摘要），不堆细节
- 对话中出现可复用的规则/兼容性/排障结论/项目知识时，就近落盘到对应模块 AGENTS.md，并同步更新根目录索引（以模块内容为准）
- 索引过期或不准确时主动修改

## 六、边界（YAGNI）

不做：
- 删除死代码、架构简化、定规范、建测试（文章四、五步是重构动作，非"看懂"；模板仅记录已有规范，不新制定）
- 知识库/图谱、直接改项目文件
- CLAUDE.md 壳内不堆 AGENTS.md 已有内容；不双写同内容（单源 @ 导入）

## 七、事实查证

Claude Code 内存系统读取：CLAUDE.md / CLAUDE.local.md / ~/.claude/CLAUDE.md / .claude/rules/*.md / 受管策略文件（macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`，Windows `C:\Program Files\ClaudeCode\CLAUDE.md`）/ 自动记忆 `~/.claude/projects/<project>/memory/`。**不读 AGENTS.md**。官方推荐用 `@AGENTS.md` 导入实现双生态兼容，而非双写或 symlink（Windows 上 symlink 需管理员权限或开启开发者模式）。
来源：https://code.claude.com/docs/en/memory.md
