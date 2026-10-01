# Matt Pocock skills 1.3 待并清单

**状态：暂缓，等 1.3 正式发布。** 2026-10-02 记录。本地副本保持 v1.2.3 不动。

## 为什么暂缓

上游 `origin/main`（`d81f3a1`，2026-09-29）已含 1.3 的全部改动，但 `.claude-plugin/plugin.json` 仍是 `1.2.3`，14 个 changeset 挂在 `.changeset/` 待发布。此时 port 的是**未发布内容**，上游随时可能改，发布后需再对一次。

## 取数

本地 fork 基线 = 插件缓存 `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/`（commit `84fdeff`）。
marketplace clone `~/.claude/plugins/marketplaces/mattpocock/` 是 shallow clone，需先 fetch 才有新内容：

```bash
git -C ~/.claude/plugins/marketplaces/mattpocock fetch origin main
git -C ~/.claude/plugins/marketplaces/mattpocock diff --stat HEAD origin/main -- skills/
```

发布后改看 tag 或 CHANGELOG 顶版号，别再拿 `origin/main` 当基线。

## 本地化约定（每份都要做）

上游正文是英文，本地副本的既定处理是：

1. frontmatter 加 `version:` 字段记来源版本（1.2.3 → 1.3.0）。
2. `description` 改写成中文，**英文触发词原词保留**（`"diagnose"`、`"red-green-refactor"`、`"review since X"`、`"grill"` 等），上游术语保留原词并就地加中文解释，否定句改肯定句，「代理」统一写「Agent」，模型可见与仅 `/` 菜单两类详略都写全。
3. 正文保持英文，除下方「本地例外」列出的那份。

## 13 条待并

| # | changeset | 类型 | 触及本地 skill | 要点 |
|---|---|---|---|---|
| 1 | `rename-context-to-glossary` | minor | domain-modeling、grill-with-docs、improve-codebase-architecture、setup-matt-pocock-skills、triage、tdd、diagnosing-bugs、ask-matt、codebase-design、wait-what、pr | `CONTEXT.md`／`CONTEXT-MAP.md` 全仓改名 `GLOSSARY.md`／`GLOSSARY-MAP.md`。**牵连本机**：`C:\ZYS\Workspace\CLAUDE.md` 的「Domain docs」一节与 `docs/agents/domain.md` 都写着 `CONTEXT.md`，要同改。上游只认新名，老文件要 `git mv`。 |
| 2 | `user-invoked-skill-invocation` | patch | to-spec、wayfinder、to-tickets、triage、code-review、diagnosing-bugs | 修 bug #453：skill 试图用 Skill tool 调 user-invoked skill（调不动）。`setup-matt-pocock-skills` 的五处前置条件改写成「让用户自己去跑」；`diagnosing-bugs` Phase 6 对 `improve-codebase-architecture` 的交接直接删掉，Phase 6 变成纯 Cleanup。**本地有其中 2 份**：code-review、diagnosing-bugs。 |
| 3 | `skill-tool-invocation-terminology` | patch | code-review、diagnosing-bugs、grill-with-docs、grill-me、improve-codebase-architecture、tdd、to-spec、to-tickets、triage、wayfinder | 跨 skill 引用统一成 `Call the Skill tool with "X"`，不再用裸 `/skill` 散文（散文式引用不保证加载，是 `grill-with-docs` 最常被报的问题的成因）。**本地有 4 份**：code-review、diagnosing-bugs、tdd、grill-me。注意与 #2 的边界：这条只适用于 model-invoked skill。 |
| 4 | `graduate-implement-spec` | minor | 新增 | `implement-spec`（user-invoked）进插件：整份 spec 一把跑，把 ticket 当任务图，在 ready frontier 上并行开 implementer subagent（各自 worktree），全部落到一条 integration branch，收尾走 code-review。与本地的 implement／to-spec／wayfinder／triage 路线配套，值得并。 |
| 5 | `graduate-pr` | minor | 新增 | `pr`（model-invoked）进插件：PR 正文结构——summary 用最小可视化说清改动（伪代码／调用树／文件树／Mermaid／diff）、改动前后证据、合并危险判断（单向门／双向门 + 爆炸半径）。Summary 部分致谢 Dex Horthy 的 `show-me`，skill 内有 `CREDITS.md`。 |
| 6 | `graduate-retro` | minor | 新增 | `retro`（user-invoked）进插件：复盘一次编码会话，改的是 Agent 的环境而非代码——导航指针、自动检查、编码规范、steering 文件、工具经济、信息可达。编码规范类发现先分类：机械违规给确定性检查（linter 规则／pre-commit／CI），真需要判断的才进 `CODING_STANDARDS.md`；仓库毫无护栏本身就是一个发现。与本机 9 月那轮 skill/hook 审计同类，可能有增量。 |
| 7 | `domain-modeling-trigger-context-adr` | patch | domain-modeling | description 改为「讨论代码库术语」「直接写或改 `GLOSSARY.md`／ADR」时也触发，替掉原来更窄的措辞；删掉「另一个 skill 需要维护领域模型」这句 caveat。 |
| 8 | `wait-what-context-map` | patch | wait-what | 多 context 仓库按 `GLOSSARY-MAP.md` 找对应的 `GLOSSARY.md`，不再死守根目录单份。 |
| 9 | `grilling-add-hr-between-questions` | patch | grilling | 轮次模板里连续问题之间加 `---` 分隔线，不再糊成一片。**直接影响本地化模板**：本地 grilling 的问题块格式（`❓ **Q1**` / `➡️ 建议`）要跟着加分隔线。 |
| 10 | `remove-em-dashes-repo-wide` | patch | 全部 | 全仓散文去 em-dash，逐句手改成逗号／冒号／句号／括号／连词，不是机械替换；`CLAUDE.md`／`AGENTS.md` 加「不得再引入」。**纯风格，优先级最低**；本地正文是英文，量最大而收益最小，可整条跳过。 |
| 11 | `grilling-remove-em-dashes` | patch | grilling | grilling 的 `SKILL.md` 单独去 em-dash。跟 #10 重叠。 |
| 12 | `fix-yaml-frontmatter-colons` | patch | to-spec、code-review、setup-matt-pocock-skills、wait-what | #905 的 em-dash 清除在 `description` 里留下裸的「冒号+空格」，六个 frontmatter 成了非法 YAML，`skills.sh` 发现阶段直接跳过，装不上。**注意**：本地化时 description 已是中文并加引号，本地不容易踩；但若照抄上游英文 description 就会踩。 |
| 13 | ~~`remove-resolving-merge-conflicts`~~ | minor | — | **已执行 2026-10-02**：真身移入 `~/.claude/archive-skills/resolving-merge-conflicts/`，符号链接已摘除。 |

## 本地例外

- **handoff**：正文的落点句与 `description` 已偏离上游（指向 `notes/<任务名>/handoff/<日期>-<短名>.md`，无任务笔记时退系统临时目录）。port 时除这一份外逐字节照搬，这份要手工合。

## port 时的检查清单

- [ ] 逐份改 `version:` 1.2.3 → 1.3.0
- [ ] 逐份重写 `description`（中文 + 保留英文触发词），照抄上游英文的必须加引号
- [ ] handoff 单独手工合，不覆盖落点句
- [ ] `C:\ZYS\Workspace\CLAUDE.md` 与 `docs/agents/domain.md` 的 `CONTEXT.md` → `GLOSSARY.md`
- [ ] 新增 3 份（implement-spec、pr、retro）按同一约定本地化后建符号链接
- [ ] `~/.claude/skills/` 下补符号链接指向 `~/.config/magpie/library/skills/`
- [ ] 改前给 `~/.config/magpie/library/skills/` 整库打快照（该库不在 git 内，无回滚网）
- [ ] 改完在本文件顶部把「暂缓」改成完成日期，并把台账 [skill-install.md](skill-install.md) 的版本与份数更新
