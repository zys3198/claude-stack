---
name: content-to-note
description: >-
  把公众号/抖音链接提取整理成结构化 Markdown 笔记，统一落盘 wiki（公众号进
  71-公众号文章、视频进 70-视频笔记），frontmatter 统一。用户分享 mp.weixin.qq.com
  / v.douyin.com / douyin.com 链接，或说"提取/整理/做笔记/存一下这篇/记成笔记"时触发。
  纯 B站 内容直达 bili-note 不触发本 skill。底层提取调专用脚本/工具，本 skill 负责协调与统一笔记规范。
---
# content-to-note

把任意内容链接(公众号 / B站 / 抖音)提取并整理成结构化笔记,统一存进 wiki。

## 何时用

- 用户给内容链接 + 想要笔记(提取/整理/总结/做笔记/存一下)
- 链接来自:mp.weixin.qq.com(公众号)、bilibili.com / b23.tv(B站)、v.douyin.com / douyin.com(抖音)

不用:纯网页文章(走 Jina Reader)、只要一句话口头摘要不要落盘、本地已有内容。

## 路由

按 URL 域名识别来源 → 走对应提取引擎 → 按统一规范整理 → 落盘 wiki。

| 来源 | URL 模式 | 提取引擎 | 笔记目录 |
|------|---------|---------|---------|
| 微信公众号 | mp.weixin.qq.com | wechat 脚本(见下) | wiki/71-公众号文章/ |
| B站视频/图文 | bilibili.com, b23.tv, BV… | bili-note skill | wiki/70-视频笔记/bilibili/ |
| 抖音 | v.douyin.com, douyin.com/video | agent-reach（公开内容）+ 手动 fallback | wiki/70-视频笔记/douyin/ |

底层引擎按来源独立调用；当前不可用的来源走明确 fallback。本 skill 只路由 + 统一笔记规范,不重写提取逻辑。

## 各来源

### 微信公众号

脚本:本 skill 自带 `scripts/wechat/run.js`。它集成了 [wechat-article-extractor](https://github.com/freestylefly/wechat-article-extractor-skill) 的 `extract.js`(完整解析:标题/作者/摘要/正文/封面/版权/类型/迁移检测/标签/内嵌公众号链接/错误码 1000-2016)。

```powershell
node "$env:USERPROFILE\.claude\skills\content-to-note\scripts\wechat\run.js" "<mp-url>" "<wiki/71-公众号文章/YYYY-MM-DD-标题.md>"
```

原理:**直连抓取**(微信 UA + 跟随 302 + UTF-8 Buffer)→ `extract(html, {url})` 解析。绕过 extractor 自带的 request-promise 抓取路径(微信会挡),复用它的成熟解析。

依赖(已装在该目录 node_modules):cheerio / dayjs / qs / lodash.unescape。request-promise 故意不装(惰性 require,只走 HTML 解析路径用不到)。

坑(已验证):
- Exa MCP 抓不到**未索引**的公众号文章(contents/livecrawl 均返回空),公众号只能直连抓,不靠 Exa。
- 抓取必须带微信 UA + 跟随 302,否则被重定向到验证页。
- PowerShell 默认按 GBK 读 UTF-8 文件会显示乱码,文件本身没坏;用 `[System.Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($f))` 读。

用法/原理另见:wiki/71-公众号文章/README.md。

### B站

调 `bili-note` skill；它负责元数据、字幕、ASR、评论、归档、预算和评分。

边界:bili-note 的**原始材料归档**(默认 D:\knowledge\…)保持原处不动,本 skill 只把整理后的**学习型笔记**存进 wiki/70-视频笔记/。

### 抖音

当前没有本地专用抖音提取 skill。先用 `agent-reach` 获取可访问的公开内容，再按统一规范整理；无法获取或需要完整音频转写时，说明覆盖范围并走手动 fallback。

## 笔记规范

提取后按统一骨架整理成笔记。frontmatter + 结构见 [references/note-template.md](references/note-template.md)。

## 边界

不做:重新实现各来源提取、改动各 skill 原始材料归档位置、处理非三类来源链接、把重归档体系塞进 wiki。
