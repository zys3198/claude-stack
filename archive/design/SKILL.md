---
name: design
description: >
  Inject a brand's DESIGN.md design system so the agent generates UI matching
  that brand's visual language (colors, typography, components, layout).
  Use when user says "use design X", "build page looks like X", "style like X",
  "design system for X", or invokes /design <brand>. Also auto-suggest when
  user names a brand while requesting UI/frontend work.
---

# /design <brand>

Load `DESIGN.md` from VoltAgent awesome-design-md library and apply as the
active design system for any UI generated this conversation.

## Location

`~/.claude/lib/awesome-design-md/design-md/<brand-slug>/DESIGN.md`

74 brands available (sample): linear.app, stripe, apple, vercel, claude,
cursor, supabase, figma, framer, nvidia, spotify, tesla, airbnb, coinbase,
notion, sentry, posthog, clickhouse.

## Resolution (happy path)

1. Lowercase user's brand arg, strip spaces/hyphens → candidate slug.
2. `ls ~/.claude/lib/awesome-design-md/design-md/` to list actual folders.
3. Match candidate against folder names. Match order: exact → prefix →
   substring → Levenshtein ≤ 2. First hit wins.
   - `linear` → `linear.app` (substring), `dell` → `dell-1996` (prefix),
     `bmwm` → `bmw-m` (Levenshtein 1), `stripe` → `stripe` (exact).

## Failure Modes

if-then-then 三段式 fallback。任一触发先告知用户，不静默跳过。🛑 = 必须停下等用户决策，禁止自主默认；⚠️ = 降级但可继续。

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| `/design` 无 brand 参 | 走「No arg or `list`」流程，列 74 品牌问选 | ⚠️ 用户仍不给 → 停 skill，等下轮明确 brand |
| slug 匹配 0 文件夹 | Levenshtein ≤ 3 模糊搜，列 top-5 候选问用户 | 🛠 候选也无 → 报「`<brand>` 不在库」+ 建议 `git pull` 更新或 PR 新增 |
| 🛑 匹配 ≥2 等近文件夹（如 `bmw` 同时命中 `bmw`/`bmw-m`） | 列所有命中，问用户选 | 🛑 **禁止默认**——必须等用户明确选 X，不静默取字母序首个 |
| 🛑 库目录不存在（`ls design-md/` 报 No such file） | 提示用户跑安装：`git clone --depth 1 https://github.com/VoltAgent/awesome-design-md.git ~/.claude/lib/awesome-design-md` | 🛑 用户不想装 → 停 skill，**禁止**回退训练知识冒充官方 token |
| 文件夹存在但无 `DESIGN.md` | `ls <folder>/` 看有无 `README.md`/其他 `.md`，Read 代替 | 🛠 全空 → 报「`<brand>` 文件夹损坏」，跳过该 brand |
| 🛑 `Read DESIGN.md` 报错（IO/权限） | 重试 1 次（排除瞬时） | 🛑 仍失败 → 报路径 + 权限提示，**禁止幻觉 token**，跳过该 brand |
| `DESIGN.md` 内容残缺（缺 colors/typography 段） | Read 同目录 `README.md` 补 | ⚠️ 都缺 → 用已有段 + 训练知识补，**必须明标**「token 不全，X 段为推断」 |

## After match

1. `Read` the matched `DESIGN.md` (and `README.md` if present for extra
   context — optional, only if DESIGN.md feels thin).
2. 🔴 **CHECKPOINT** — state brand loaded in one line: `Design system: <brand>`
   before generating any UI. If user supplied the brand implicitly (no `/design`
   prefix, auto-suggested from brand name + UI request), confirm intent first:
   `Will apply <brand> design system — OK?` and wait for yes/silent-accept.
3. Apply tokens (color palette, type scale, spacing, components, elevation,
   do/don'ts) to every UI artifact this turn and onward until user switches
   brand or says "stop design".
4. If generating frontend code, also follow any user-named framework
   (shadcn/ui default per CLAUDE.md §6); brand tokens override defaults.

## No arg or `list`

`ls ~/.claude/lib/awesome-design-md/design-md/` → show all 74 brands grouped
by category (AI/LLM, DevTools, Backend, SaaS, Design, Fintech, Commerce,
Media, Automotive, Retro). Source: README.md category headings.

## Anti-patterns (禁止)

| # | 反模式 | 为什么禁止 | 正确做法 |
|---|---|---|---|
| 1 | 幻觉 brand token（DESIGN.md 缺失时编造颜色/字体） | 产出看似对实则错的 UI，用户难察觉 | 走 Failure Modes 表，🛑 停 + 告知用户，宁可不输出也不编 |
| 2 | 把 brand token 用到非 UI 任务（API/config/数据 schema/纯文案） | design system 只管视觉层，跨界污染 | skill 只在前端/UI 产物激活；后端/数据/配置不注入 |
| 3 | 混多个 brand 的 token 到同一产物（Linear 配色 + Stripe 字体） | 视觉混乱，违背「单一 design system」契约 | 一次只用一个 brand；用户要混 → 显式分两段产物，各标来源 |
| 4 | 读 `preview.html` / `preview-dark.html` 除非用户明要视觉目录 | 浪费 context（HTML 重），DESIGN.md 是权威源 | 默认只读 DESIGN.md + 可选 README.md |
| 5 | 跨会话默认 brand 或覆盖用户明指框架 | 用户意图 > skill 默认（上次 Linear ≠ 这次默认 Linear；用户说 Material UI ≠ 强推 shadcn） | 每会话首次显式确认 brand；用户 framework 选择 > CLAUDE.md §6 默认 > skill 默认 |

## Update library

`cd ~/.claude/lib/awesome-design-md && git pull` — user runs this, not the
agent (per CLAUDE.md §1.3 人工确认线).
