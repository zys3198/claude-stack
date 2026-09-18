---
name: content-to-note-by-user
description: >-
  把公众号/B站/抖音链接提取整理成结构化、学习型 Markdown 笔记，落盘到调用时指定的目录。
  用户分享 mp.weixin.qq.com / bilibili.com / b23.tv / v.douyin.com / douyin.com
  链接，或说「提取/整理/做笔记/存一下这篇/记成笔记」时触发。纯网页文章（Jina Reader
  路线）、只要口头摘要不落盘、本地已有内容不触发。
---
# content-to-note-by-user

把内容链接（公众号 / B站 / 抖音）提取并整理成可学习、可检索、可回查证据的 Markdown 笔记，落盘到调用时指定的目录。

## 何时用

- 用户给内容链接 + 想要笔记（提取/整理/总结/做笔记/存一下）
- 链接来自：mp.weixin.qq.com（公众号）、bilibili.com / b23.tv / BV…（B站）、v.douyin.com / douyin.com（抖音）

不用：纯网页文章（走 Jina Reader）、只要一句话口头摘要不要落盘、本地已有内容。

## 路径约定

- **skill 根目录**（下文 `$skill`）：`C:\Users\zys31\.claude\skills\content-to-note-by-user`
- **笔记落盘**：调用时由用户指定目录；未指定就先问，仍不指定则不落盘，笔记直接输出到对话
- **原始材料归档**：默认放在笔记目录下的 `.archive\<笔记slug>\`，用户另行指定就按用户的；用户不需要留档时跳过归档
- B站笔记 slug：`bili-<BVID>-<短标题>`，归档目录同名
- frontmatter 与骨架见 [references/note-template.md](references/note-template.md)

## 路由

按 URL 域名识别来源 → 走对应提取引擎 → 按统一规范整理 → 落盘到指定目录。

| 来源 | URL 模式 | 提取引擎 |
|------|---------|---------|
| 微信公众号 | mp.weixin.qq.com | `$skill\scripts\wechat\run.js` |
| B站视频/图文 | bilibili.com, b23.tv, BV… | `$skill\scripts\run_bili_note.py` 等本目录 Python 脚本，原始材料另归档 |
| 抖音 | v.douyin.com, douyin.com/video | `agent-reach`（公开内容）+ 手动 fallback |

本 skill 只路由 + 统一笔记规范，不重写提取逻辑。当前不可用的来源走明确 fallback 并说明覆盖范围。

## 微信公众号

脚本 `$skill\scripts\wechat\run.js`。它集成了 [wechat-article-extractor](https://github.com/freestylefly/wechat-article-extractor-skill) 的 `extract.js`（完整解析：标题/作者/摘要/正文/封面/版权/类型/迁移检测/标签/内嵌公众号链接/错误码 1000-2016）。

```powershell
node "$skill\scripts\wechat\run.js" "<mp-url>" "<笔记目录>\YYYY-MM-DD-标题.md"
```

`$skill` 和 `<笔记目录>` 都要替换为实际绝对路径。

原理：**直连抓取**（微信 UA + 跟随 302 + UTF-8 Buffer）→ `extract(html, {url})` 解析。绕过 extractor 自带的 request-promise 抓取路径（微信会挡），复用它的成熟解析。

依赖装在该目录 `node_modules`（cheerio / dayjs / qs / lodash.unescape；node_modules 不入 git，换机在 `$skill\scripts\wechat` 跑 `npm install` 恢复）。request-promise 故意不装（惰性 require，HTML 解析路径用不到）。

坑（已验证）：
- Exa MCP 抓不到**未索引**的公众号文章（contents/livecrawl 均返回空），公众号只能直连抓，不靠 Exa。
- 抓取必须带微信 UA + 跟随 302，否则被重定向到验证页。
- PowerShell 默认按 GBK 读 UTF-8 文件会显示乱码，文件本身没坏；用 `[System.Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($f))` 读。

## B站

把 B站视频和图文动态变成可检索、可复用的 Markdown 知识笔记。视频优先拿字幕；字幕拿不到时再转写音频；图文优先抓正文、图片和代码块；用户要评论区时抓取评论并过滤无关讨论。

联网或登录态操作必须走本地 CDP 代理（本机为 `http://localhost:3456`，提供 `/targets` 与 `/eval` 接口），由它驱动已登录的 Chrome 页面。

网页 AI 字幕当前只支持 Chrome + CDP 代理路线：让已登录的 B站页面自己请求字幕接口。不要把 Edge、Playwright 临时浏览器或原生 CDP 端口当成等价替代，除非脚本已经明确支持。

### 依赖与环境检查

默认路线尽量零第三方 Python 依赖：视频元数据、公开字幕、图文正文、图片清单、评论、归档、证据索引和笔记预算都用标准库完成。网页 AI 字幕和音频 ASR 是增强路线，不是启动门槛。

第一次使用、换机器、用户怀疑依赖不全，或准备使用网页 AI 字幕 / ASR 兜底时，先运行：

```powershell
$py = "python"
& $py "$skill\scripts\check_environment.py"
```

根据检查结果选择路线：

- `public_subtitles_comments_archive=OK`：优先走默认字幕/图文、评论和归档流程。
- `browser_ai_subtitles=OK`：当公开接口只有 `ai-zh` 且 `subtitle_url` 为空时，走 Chrome + CDP 代理的网页 AI 字幕。
- `audio_asr_fallback=OK`：只有字幕和网页 AI 字幕都不可得、且用户确实需要完整转写时，才走音频 ASR。
- 某个增强能力缺失时，只说明该路线暂不可用；不要把它说成整个 skill 不可用。
- 网页登录态只通过 CDP 代理连到的、已授权的 Chrome 页面使用；不要读取或复制 Cookie/profile，不要强制结束用户浏览器进程。没有 Chrome 与 CDP 代理时就跳过网页 AI 字幕并说明覆盖范围。

### 默认流程

1. 读清用户要什么：视频或图文链接、是否要评论区、保存路径、是否需要全文材料或只要提炼。
2. 如果是首次使用、依赖状态不明、字幕抓取失败或用户要求 ASR，先用 `check_environment.py` 判断当前可走路线。
3. 优先用 `run_bili_note.py` 一键完成可自动化部分。它会自动识别 `/video/BV...`、`/opus/...`、`/dynamic/...` 或纯 opus id。
4. 如果是图文/动态，走 `extract_bilibili_opus.py` 路线：抓正文、标题、作者、发布时间、图片、代码块、图文证据索引；用户加 `--comments` 时抓图文评论。
5. 如果是视频，优先下载字幕：
   - 普通字幕 URL 可用时，直接用 `--download-subtitles`。
   - 如果普通接口显示 `ai-zh` 但 `subtitle_url` 为空，不要说“没有字幕”；改走“网页 AI 字幕”流程。
   - 如果字幕仍不可得，再按需要下载音频并用 ASR 转写。
6. 用户要求评论区时，用 `--comments` 抓取主评论和子评论；写入笔记时过滤打卡、求资料、广告、闲聊等技术无关内容。
7. 归档原始材料：把完整字幕或图文正文、图片、完整评论、元数据和 JSONL 索引存到 `<归档目录>\bili-<BVID>-<短标题>\`。用户不要留档时跳过本步。
8. 写前定标：必须先读取归档目录 `metadata\note_budget.json`，把推荐字数区间、压缩比目标、写作粒度、互动质量倍率和证据块数量作为本次笔记的写作目标。视频按时长、字幕字数、证据块、评论量和互动质量定标；图文按正文长度、图片/代码/证据块、评论量和互动质量定标。
9. 按预算写 Markdown：默认写成“学习型笔记”，目标是让人或 Agent 像学完一节课或读完一篇教程一样获得概念、方法、判断标准、实践步骤和自测题；根据预算决定详略，不要把长课和短视频写成差不多字数。来源、覆盖范围和归档路径放到后半部分。正文证据默认用论文式编号 `[1][2]`，不直接堆长证据 ID。
10. 写后验收：用 `score_bili_note.py` 校验笔记字数、压缩比、每分钟/每篇笔记密度和证据引用比例。评分只做 QA 和微调，不代替写前定标；太短时优先补“学习收获、知识地图、概念卡、实战流程、坑点、自测题”，不要只堆分P摘要或段落摘要。

### 常用命令

以下示例以 `BVxxxx` / `O119...` 为占位，`<笔记目录>` 与 `<归档目录>` 替换为本次实际使用的目录；work 目录是可丢弃的临时目录（加 `tmp_` 前缀）。

#### 0. 检查依赖和可用路线

```powershell
& $py "$skill\scripts\check_environment.py"          # 人读
& $py "$skill\scripts\check_environment.py" --json   # 给其他脚本读
```

#### 1. 一键提取和归档（默认入口，自动跳过已有输出，适合断点续跑）

```powershell
& $py "$skill\scripts\run_bili_note.py" "https://www.bilibili.com/video/BVxxxx/" `
  --work-dir ".\tmp_bili_extract" `
  --archive-dir "<归档目录>\bili-BVxxxx-视频短标题" `
  --comments
```

图文/动态同一个入口：

```powershell
& $py "$skill\scripts\run_bili_note.py" "https://www.bilibili.com/opus/1194341967364882439" `
  --work-dir ".\tmp_bili_opus" `
  --archive-dir "<归档目录>\bili-O1194341967364882439-图文短标题" `
  --comments
```

只存图文正文和图片 URL、不下载图片文件：加 `--no-download-images`。

普通接口没有字幕、但网页播放器能拿到 AI 字幕时：先用 CDP 代理打开已登录 Chrome 里的视频页并取得 target id，再加 `--browser-target "CDP_TARGET_ID"`。

运行后先看：

- `bili_note_run_report.md`：本次跑了什么、跳过了什么、下一步读哪里。
- `<archive>\indexes\证据索引.jsonl`：写总结时可引用的图文/字幕/评论证据块。
- `<archive>\indexes\图文全集.md` / `\字幕全集.md`：完整正文合集。
- `<archive>\metadata\note_budget.json`：推荐笔记字数、压缩比和写作粒度。

#### 2. 抓元数据和分P目录

```powershell
& $py "$skill\scripts\extract_bilibili.py" "BVxxxx" --out ".\tmp_bili_extract"
```

#### 3. 下载普通公开字幕

```powershell
& $py "$skill\scripts\extract_bilibili.py" "BVxxxx" --out ".\tmp_bili_extract" --parts all --download-subtitles
```

#### 4. 下载网页 AI 字幕

当 `subtitle_probe.json` 里有 `ai-zh` 但 `subtitle_url` 为空时使用。脚本需要一个提供 `/targets` 和 `/eval` 的本地 CDP 代理配合 Chrome；原生 Edge/Chrome DevTools 端口不能直接传给这个脚本。

1. 用 CDP 代理打开已登录 Chrome 中的 B站视频页，确认页面已加载。
2. 查看浏览器 target id：`curl.exe -s http://localhost:3456/targets`
3. 下载 AI 字幕：

```powershell
& $py "$skill\scripts\fetch_browser_ai_subtitles.py" --target "CDP_TARGET_ID" --out ".\tmp_bili_extract"
```

输出：`browser_ai_subtitle_urls.json`、`browser_ai_subtitle_manifest.json`、`browser_ai_subtitles\*.txt|*.srt|*.subtitle.json`。

这条路线让 B站页面自己用登录态请求 `/x/player/wbi/v2`，不读取、不打印浏览器 cookie。

如果下载到的 AI 字幕明显乱码、内容与标题或课程主题不相干，不要把它当作可靠全文。优先标注“AI 字幕质量不可用”，再考虑 ASR 兜底；若 ASR 也不可用，只能基于分P标题、简介、评论和元数据生成有限学习指南，并明确局限。

#### 5. 抓评论区

```powershell
& $py "$skill\scripts\extract_bilibili.py" "BVxxxx" --out ".\tmp_bili_extract" --comments
& $py "$skill\scripts\extract_bilibili_opus.py" "https://www.bilibili.com/opus/1194341967364882439" --out ".\tmp_bili_opus" --comments
```

图文评论对象不是 opus id，而是页面数据里的 `basic.comment_type` 和 `basic.comment_id_str`；抓评论时不要硬套视频的 `type=1/oid=aid`。检查 `comments.md` 和 `comments_raw.json`；写笔记时只保留与主题相关的评论、纠错、技术补充、实践经验和有价值问题。

#### 6. 音频 ASR 兜底

只有字幕和网页 AI 字幕都不可用时才用 ASR。长视频不要默认全量转写，除非用户明确要求。

```powershell
& $py "$skill\scripts\extract_bilibili.py" "BVxxxx" --out ".\tmp_bili_extract" --parts "1,10,38" --download-audio --transcribe --asr-backend auto --asr-model base
```

中文视频优先：`--asr-backend funasr --asr-model "iic/SenseVoiceSmall"`。

#### 7. 归档完整材料（总入口已内置；单独重跑用）

```powershell
& $py "$skill\scripts\archive_bili_materials.py" --extract-dir ".\tmp_bili_extract" --archive-dir "<归档目录>\bili-BVxxxx-视频短标题"
```

长期材料包包含：`articles\`（图文全文 md/txt）、`images\`、`subtitles\{txt,srt,json}\`、`comments\`（原始 JSON + 评论全集 md）、`indexes\`（图文/字幕/评论全集与证据索引，md + jsonl，含合并的 `证据索引.jsonl`）、`metadata\`（元数据、清单、`note_budget.json`）。

#### 8. 写前读预算，写后验收信噪比

```powershell
Get-Content -Encoding UTF8 "<归档目录>\bili-BVxxxx-视频短标题\metadata\note_budget.json"
```

重点：推荐字数区间 `recommended_note_chars_min/max`、写作粒度 `granularity` / `writing_guidance`、信息量基准（视频 `duration_minutes`/`subtitle_chars`，图文 `content_chars`/`reading_minutes_estimate`）、质量倍率 `quality_multiplier`/`quality_metrics`、证据规模 `all_evidence_blocks`。

```powershell
& $py "$skill\scripts\score_bili_note.py" `
  --archive-dir "<归档目录>\bili-BVxxxx-视频短标题" `
  --note-path "<笔记目录>\bili-BVxxxx-视频短标题.md" `
  --out "<归档目录>\bili-BVxxxx-视频短标题\metadata\note_score.json"

& $py "$skill\scripts\update_note_budget_section.py" `
  --archive-dir "<归档目录>\bili-BVxxxx-视频短标题" `
  --note-path "<笔记目录>\bili-BVxxxx-视频短标题.md"
```

重点看：`status`（`too_short` 遗漏风险高 / `too_long` 重复堆料 / `ok`）、`actual_compression_ratio`（笔记字数/字幕字数）、`note_chars_per_minute`、`evidence_reference_ratio`（关键判断要能回查图文证据 `O...`、字幕证据 `Pxx@...` 或评论证据 `C...`；正文用统一数字编号，文末脚注链接必须指向含完整证据 ID 的归档文件）。

### 笔记写法

默认输出必须是“学习型笔记”，不是目录搬运、分P流水账或证据清单。读完后应有“我真的学会了一些东西”的获得感。

推荐结构：

1. `# 标题`
2. `## 学完你应该获得什么`：5-8 条，写清学完后能理解、判断或完成什么。
3. `## 一句话总论`：最核心的判断，避免只复述标题。
4. `## 适用场景与前置知识`：适合谁、不适合谁、需要先知道什么。
5. `## 知识地图`：核心概念、模块、流程及关系。课程型视频要有模块表；短观点视频要有论证链。
6. `## 核心概念卡`：每个重要概念写“是什么、为什么重要、怎么用、常见误区、相关证据”。
7. `## 方法或流程`：操作、架构、决策流程、参数选择、评估方法抽成可复用步骤。
8. `## 关键洞察`：作者真正想表达的判断，区分“事实描述、经验判断、推荐做法、限制条件”。
9. `## 实践清单`：可照做的步骤、检查项、失败信号和排错方向。
10. `## 坑点与反例`：踩坑、争议、误区、边界条件。
11. `## 自测题`：5-10 个问题和简短答案。
12. `## 证据与原文位置`：只放关键证据的编号引用，不要让证据淹没学习内容。
13. `## 来源、覆盖与局限`：URL、BVID、UP、发布时间、字幕/评论覆盖、归档路径和局限。

写作标准：

- 先解释“为什么”和“怎么迁移使用”，再列“他说了什么”。
- 课程型长视频按学习模块组织，不按分P机械压缩；每模块至少含学习目标、核心概念、关键步骤、常见坑、可操作结论。
- 观点型短视频按“问题背景 → 作者判断 → 论据 → 适用边界 → 对用户的启发”组织。
- 技术教程和图文长文保留架构、数据流、代码思路、配置项、图片结论、评估方式和排错路径。
- 评论区只写有学习价值的内容：纠错、补充案例、实践经验、替代方案、争议点。
- 证据引用服务于学习。正文用统一论文式数字编号 `[1][2]`，图文/字幕/评论证据共用一套编号，按正文首次出现顺序递增，不在正文塞长 ID。在 `## 来源、覆盖与局限` 之前放 `## 证据脚注`：有序列表写编号和证据链接（如 `1. [图文证据 E006](<相对归档路径>/indexes/图文证据索引.md#O...-E006)`），后附 reference-style 链接定义 `[1]: <相对归档路径>/...` 让 `[1]` 可点击。`## 证据与原文位置` 总览里也只写编号。
- 写前按 `note_budget.json` 定标，再动笔；写后评分只用于验收微调，不把长度决策推迟到评分阶段。
- 预算偏短或评分过短时，优先补“概念解释、流程图式文字、实践清单、自测题、反例和边界”，不只加摘要段落。
- 热度是“值得多写”的辅助信号，不是替代证据。扩写必须来自图文正文、字幕、评论证据和内容结构。

不合格信号：

- 开头大段来源信息，读者半天不知道学到了什么。
- 只有“核心观点/分P提炼/代表性证据”，没有概念解释、方法步骤和自测。
- 把每个分P压成一句话，长课程读完仍不知道怎么做。
- 只总结作者立场，不写适用条件、反例和失败场景。
- 评论区只是罗列热评，没有转化成纠错、补充或实践提醒。

不要把“只看了标题/目录”的内容写成“完整提取”。只抓到部分字幕或只转写了部分分P，必须明确列出覆盖范围。

### B站字幕注意事项

- 普通 `/x/player/v2` 可能只返回 `ai-zh` 字幕元信息、`subtitle_url` 为空；网页播放器接口 `/x/player/wbi/v2` 常能拿到真正的 AI 字幕 URL。
- AI 字幕常把技术词识别错：RAG→RG/ROG/rap；LangChain→non chain/long chain；reranker→“瑞 rank”。总结时结合分P标题和技术语境校正术语。

### B站图文注意事项

- 图文正文优先从页面内 `window.__INITIAL_STATE__` 读取；公开 polymer 动态接口可能返回风控错误。
- 图文正文保留标题、段落、标题层级、列表、代码块、链接卡片、图片 URL 和图片清单。
- 让你总结图文中图片含义时，先检查 `images\` 或 `images_manifest.json`；仅凭图片 URL 不足以判断内容时，说明图片视觉内容未被完整理解。

接口细节另见 [references/bilibili-api-notes.md](references/bilibili-api-notes.md)。

## 抖音

当前没有本地专用抖音提取脚本。先用 `agent-reach` 获取可访问的公开内容，再按统一规范整理；无法获取或需要完整音频转写时，说明覆盖范围并走手动 fallback。命名与 frontmatter 照 [references/note-template.md](references/note-template.md)，原始材料落 `<归档目录>\<YYYY-MM-DD>-douyin-<短标题>\`。

## 通用笔记规范

提取后按统一骨架整理：frontmatter + TLDR + 结构化正文 + 关键收获 + 来源与覆盖，详见 [references/note-template.md](references/note-template.md)。B站笔记以上文「笔记写法」13 节结构为准（比通用骨架更严格）。

## 相关文件

- `scripts\wechat\run.js`：公众号直连抓取 + 解析。
- `scripts\check_environment.py`：检查核心流程、网页 AI 字幕、音频 ASR 和测试依赖。
- `scripts\run_bili_note.py`：B站视频/图文提取、评论、归档和证据索引一键入口。
- `scripts\extract_bilibili.py`：元数据、字幕探测、普通字幕、音频、ASR、评论抓取。
- `scripts\extract_bilibili_opus.py`：B站图文/动态正文、图片、代码块和图文评论。
- `scripts\fetch_browser_ai_subtitles.py`：通过已登录网页播放器下载 B站 AI 字幕。
- `scripts\archive_bili_materials.py`：归档完整材料，生成全文索引和证据索引。
- `scripts\score_bili_note.py`：按 `note_budget.json` 验收笔记长度、压缩比和证据引用。
- `scripts\update_note_budget_section.py`：把预算、互动质量和信噪比评分写回 Markdown 笔记。
- `references\bilibili-api-notes.md`：B站接口细节与已知坑。
- `references\note-template.md`：通用笔记骨架。
- `tests\`：Python 脚本与 SKILL 关键约束的自测（`python -m pytest tests`）。

## 边界

- 不重新实现各来源提取逻辑；不处理公众号/B站/抖音之外的来源链接。
- 原始材料只进本次指定的归档目录，不进版本库、不写用户未授权的目录。
- 不在笔记里抄源全文；笔记是提炼物，正文用编号引用归档证据。
- 无法获取的内容明确标注覆盖范围与局限，不把部分提取冒充完整提取。
