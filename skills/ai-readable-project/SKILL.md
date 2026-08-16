---
name: ai-readable-project
description: 让项目能被 AI 看懂——产出 AI 上下文工程静态上下文（根 CLAUDE.md + AGENTS.md 知识索引 + 模块领域说明），并沉淀长期维护规则，使项目持续被 AI 维护。触发：让 AI 看懂这个项目、梳理项目给 AI 用、引入 AI 协作、建 CLAUDE.md/AGENTS.md、项目 AI 上下文、把项目梳理成 AI 可维护、让 AI 接手老项目。<!-- v0.2.0 -->
---

# ai-readable-project

让项目能被 AI 看懂。核心思想源自腾讯技术工程《从胡言乱语到精准改代码》：AI 在老项目里「胡言乱语」，根因是**上下文不够**。AI 与开发差别不在能力，在于上下文——缺的是四类（均为原文提炼）：

1. **业务历史背景 + 整体协作方式**（与其他模块的关系）
2. **过去的需求/技术文档位置**（往往在开发或产品脑袋里）
3. **项目真实运行情况**：哪些代码真在跑、哪些只是历史兼容但跑不到（引用 ≠ 运行）
4. **架构设计 + 技术债务**：哪些改造只做了一半

本 skill 把「AI 上下文工程」静态上下文建起来，产出知识索引 + 模块说明 + 维护规范。目标（原文）：**同一件事，只需要跟 AI 强调一遍即可**——建好一次，AI 后续无需每次重建上下文。

## 何时用

- 用户说「让 AI 看懂这个项目 / 梳理项目给 AI 用 / 建 CLAUDE.md / 建 AGENTS.md / 项目 AI 上下文」
- 要在项目里引入 AI 协作、重构为 AI 可维护项目
- 老项目债务重、AI 总判断错、想给 AI 补上下文

不用：改代码/重构实现（走 code-change-workflow）、写技术文章、知识库/图谱建设。

## 产物

产出到 `docs/ai-context/`，**不直接改项目文件**，用户审阅后自行落地：

```
docs/ai-context/
  CLAUDE.md 草稿       壳：@AGENTS.md 导入 + Claude Code 特有内容
  AGENTS.md 草稿       源：知识索引 + 项目规范（Copilot/其他 agent 读）
  analysis-report.md   分析报告：模块切分、依赖、真实运行链路、债务观察
  modules/<module>-AGENTS.md   模块领域说明（就近落盘）
```

## 执行流程

1. **摸底**：目录树、语言/框架、构建配置、README；**先检查是否已有 CLAUDE.md / AGENTS.md / .claude/rules/**（增量场景先读已有内容再决定补什么）。摸底须覆盖上文四类上下文——业务背景与协作方式、文档位置、真实运行 vs 死代码、架构债务；每类记录证据来源，查不到就标「未验证」
2. **模块切分**：核心模块 + 依赖关系
3. **真实链路识别**：入口/路由/构建产物，区分活代码 vs 死代码（引用 ≠ 运行）
4. **领域知识提炼**：业务背景、架构、规范、三方对接
5. **强约束问答**：向项目负责人确认运行真相、债务、文档位置；未确认项标记「未验证」，不写"已验证"结论。**找不到负责人时：全部标「未验证」并注明证据缺口，继续产出草稿**
6. **产出**：报告 + CLAUDE.md/AGENTS.md/模块草稿

问答若推翻步骤 2-4 的结论（模块切分/链路判断），回到对应步骤修正后继续。

## 债务观察清单（分析报告 §5 用，只报告不改）

用此清单当 lens 逐项扫项目，产出到分析报告「债务观察」：

1. **死代码**：有引用但真实链路跑不到。判据：引用 ≠ 运行；运行条件藏在环境变量/配置开关时开发也难辨。典型（原文案例）：复制粘贴旧客户端兼容改造遗留的环境判断 if/else；设计了未落地的架构残留（如 OT 协同最终只是 HTTP 同步，却保留多套消息通信方式）；功能迁移新模块后旧链路未清、新旧耦合。
2. **过度设计**：为幻想未来加的复杂度——无业务诉求的协同/抽象/可配置性。原文教训：过度设计不可怕，可怕的是改造不彻底 + 几轮重构不彻底叠成债务。
3. **半成品改造**：专项改造起头未做彻底，遗留尾巴层层叠加。
4. **命名/结构混淆**：近义类名多，AI 定位易错（如 dtsf 的 Oa*Service 55 个、`OaAttendanceService` vs `OaHrAttendanceService`）。产出时把撞车清单写进对应模块说明。
5. **文档与运行脱节**：文档说在跑实际是死代码；或目录存在但无归属说明。

## 文件策略（重要）

Claude Code 不读 AGENTS.md，只读 CLAUDE.md。用 `@AGENTS.md` 导入实现单源双生态：

```markdown
<!-- CLAUDE.md -->
@AGENTS.md

## Claude Code 特定内容
...
```

AGENTS.md 是内容源（Copilot 等读），CLAUDE.md 是壳（Claude Code 读同一份）。**不双写同内容。**

## 维护规则（写入 AGENTS.md 草稿）

- 目标：「同一件事只跟 AI 强调一遍即可」——知识落盘使 AI 后续无需每次重建上下文
- 根目录只保留索引概要（路径 + 1~2 句摘要），不堆细节
- 对话中出现可复用规则/兼容性/排障结论/项目知识时，就近落盘到对应模块，并同步更新根索引
- 索引过期或不准确时主动修改
- 落地说明：草稿集中产出到 `docs/ai-context/modules/`，**落地时**将各模块说明就近放置到对应模块目录（如 `src/auth/AGENTS.md`），根索引路径同步指向实际位置

## 进阶：AI 可维护项目完整路线（可选参考）

上下文工程只是「AI 可维护项目」的第一步。原文五步清理屎山方法论完整记录在 [references/refactor-roadmap.md](references/refactor-roadmap.md)（删死代码/做减法/定规范/自动化测试/债务常态化 + AI 角色渐变）。**超出本 skill 边界**——本 skill 只产出上下文、不执行重构；用户要走上路线时，对应执行走 code-change-workflow / 自动化测试域 skill。

## 模板

- AGENTS.md 草稿模板：[references/templates/AGENTS-template.md](references/templates/AGENTS-template.md)
- CLAUDE.md 壳模板：[references/templates/CLAUDE-shell-template.md](references/templates/CLAUDE-shell-template.md)
- 分析报告模板：[references/templates/analysis-report-template.md](references/templates/analysis-report-template.md)

## 边界

不做：删死代码、架构简化、定规范、建测试（那是重构动作，非"看懂"）；知识库/图谱；自动改项目文件；双写同内容。
