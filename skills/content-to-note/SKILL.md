---
name: content-to-note
description: 把公众号／B站／抖音链接提取成结构化 Markdown 笔记。
disable-model-invocation: true
---
# content-to-note

把公众号、B站或抖音内容提取成可学习、可检索、可回查证据的 Markdown 笔记，并落盘到调用时指定的目录。

## 入口契约

- 笔记目录由调用者指定；未指定先问，仍未指定则只输出对话，不落盘。
- 原始材料默认归档到笔记目录下的 `.archive\<笔记slug>\`；用户不要留档时跳过。
- B站 slug 为 `bili-<BVID>-<短标题>`；frontmatter 和通用骨架见 [references/note-template.md](references/note-template.md)。
- `$skill` 是本目录绝对路径；脚本、归档目录和输出路径都使用实际绝对路径。

## 路由

按域名识别来源，选择提取引擎，再按统一笔记契约整理并落盘。

| 来源 | URL | 默认引擎 |
|---|---|---|
| 微信公众号 | `mp.weixin.qq.com` | `$skill\scripts\wechat\run.js` |
| B站视频/图文 | `bilibili.com`、`b23.tv`、`BV…` | `$skill\scripts\run_bili_note.py` |
| 抖音 | `v.douyin.com`、`douyin.com/video` | `mcporter` 的 `douyin` server |

不支持的来源不触发；当前引擎不可用时说明覆盖范围并停在可交付的 fallback，不把局部失败说成整个 Skill 不可用。

## 最短流程

1. 确认来源链接、要视频还是图文、是否需要评论、保存目录和是否保留原始材料。
2. 选择上表引擎；首次使用、依赖不明、提取失败或请求 ASR 时，先运行相应环境检查。
3. 读取当前分支需要的参考文件：通用骨架必须读 `references/note-template.md`；B站接口、字幕、评论和图文结构读 `references/bilibili-api-notes.md`。
4. 提取并归档允许保留的原始材料，写前读取 B站 `metadata\note_budget.json`，按预算组织学习型笔记。
5. 写后运行已有评分或测试脚本；报告覆盖范围、证据位置、局限和 `passed`、`failed`、`blocked` 或 `not-run` 状态。

## 微信公众号

```powershell
node "$skill\scripts\wechat\run.js" "<mp-url>" "<笔记目录>\YYYY-MM-DD-标题.md"
```

直连抓取并复用解析器；不依赖 Exa。依赖不全时在 `$skill\scripts\wechat` 执行 `npm install`，PowerShell 读取 UTF-8 文件使用 UTF8 编码，不把显示乱码误判为内容损坏。

## B站

- 默认用 `run_bili_note.py`，它覆盖视频、`/opus/`、`/dynamic/` 和评论/归档；参数以脚本 `--help` 和上面的 API 参考为准。
- 首次使用或环境不明先运行 `$skill\scripts\check_environment.py`。公开字幕/图文是默认路线；网页 AI 字幕只走已登录 Chrome + CDP 代理；普通字幕和网页 AI 字幕都不可得、且用户确实需要全文时，才用音频 ASR。
- 使用网页 AI 字幕时只通过 CDP 代理连接已授权页面：必须保持 **Chrome + CDP 代理**，**不要读取或复制 Cookie/profile**，**不要强制结束用户浏览器进程**。
- 用户要评论时传 `--comments`；归档完整材料、证据索引和预算后再写笔记，写后用 `score_bili_note.py` 验收。字幕或转写不完整、AI 字幕质量异常时，明确覆盖范围和局限，不能冒充完整提取。

## 抖音

`mcporter` 的 `douyin` server（`douyin-mcp-server` 1.2.1）已注册但**当前不可用**，2026-09-20 实测两处失效：分享页 `window._ROUTER_DATA` 不再返回 `videoInfoRes`，`parse_douyin_video_info` 与 `get_douyin_download_link` 报 `'videoInfoRes'` KeyError；构造函数无条件调 `create_asr_instance`，未设 `DASHSCOPE_API_KEY` 时全部工具抛错。不要再走这条路。

可用路线无专用脚本，按步骤手工执行（2026-09-20 在 `C:\ZYS\Code\lab-area\exp\2026-09-20-douyin-content-notes\` 实际跑通）：

1. 用浏览器工具（`agent-browser` 或 JEV）打开分享页，读正文与作者信息存 `-page-text.txt`。
2. 从页面取 CDN 音频轨，用 `ffmpeg` 抽成 16kHz 单声道 wav。
3. 本地 FunASR 转写：`python transcribe.py <wav> <out.txt>`；脚本在 `exp\2026-09-20-douyin-content-notes\raw\transcribe.py`（SenseVoiceSmall + fsmn-vad，CPU，rtf≈0.1），模型缓存在 `~/.cache/modelscope/hub/models/iic/SenseVoiceSmall`。

页面文字或转写缺失时说明覆盖范围并走手动 fallback，不把失败说成已提取。原始材料按 `<归档目录>\<YYYY-MM-DD>-douyin-<短标题>\` 保存。

## 笔记契约

默认输出必须是**学习型笔记**，不是目录搬运、分P流水账或证据清单。正文至少能让读者获得：`学完你应该获得什么`、一句话总论、知识地图、`核心概念卡`、方法/流程、实践清单、坑点与反例、`自测题`、证据与来源覆盖。

- 视频按学习模块组织，观点按「背景 → 判断 → 论据 → 适用边界」组织；教程保留数据流、参数、评估和排错路径。
- 正文证据用统一数字编号，关键判断可回查归档；评论只保留纠错、补充、争议和实践经验。
- **不合格信号**：只有核心观点或分P摘要、没有概念/步骤/自测；只复述作者立场、不写边界和失败场景；只抓到部分字幕却未标覆盖范围。
- 通用 frontmatter、TLDR、正文、关键收获、来源与覆盖结构，以及 B站严格的 13 节学习型扩展见 [references/note-template.md](references/note-template.md)。

## 边界

不重新实现来源提取逻辑，不处理三种来源之外的链接；原始材料只写入本次指定且获授权的归档目录，不写入版本库或其他未授权目录。
