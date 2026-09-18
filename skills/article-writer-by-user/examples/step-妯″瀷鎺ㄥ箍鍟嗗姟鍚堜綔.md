
大家好，我是 Guide。最近我越来越明显地感觉到，AI 工作流真正难啃的地方，已经从“让模型帮我写代码”往外扩了。

很多信息一开始就不在代码里。

它在一次架构评审的录音里，在需求会上产品临时补充的那几句话里，在故障复盘时大家来回确认的口头结论里。会开完了，录音躺在群里，真正要落地的人还得重新听、重新摘、重新确认行动项。

和朋友讨论，我俩最近很想验证的是：**一套开发者工作流，能不能同时处理代码、语音和结构化总结？**

比如，把一段技术复盘录音转成纪要和行动项，再生成一段能发给同事听的语音摘要。

这次我用 Step Plan 跑了一轮。选它的原因很简单：同一套 API 里有 Agent / Coding，也有 ASR 和 TTS，刚好能把这个流程跑通。

所以这篇不围着“怎么接 Claude Code”打转。我会把它放进两个任务里看：一个是代码审查，一个是会议转写和语音摘要。

## 这次为什么用 Step Plan

先说我关心的点。Step Plan 不能只按“Coding 套餐”理解，它还把 ASR、TTS、路由等能力放在同一套 API 里。

模型清单不用展开太久。对读者更有用的，是看它接进工作流以后，会产出什么东西，哪些地方还需要人工兜底。

先说费用。

套餐按月计费，采用“5 小时限额 + 周限额”的双重约束。拿 Flash Plus 套餐来说，99 元/月，周限额约 1600 次 Prompt，5 小时限额约 400 次 Prompt。这些数字对判断使用边界有帮助，所以我会把它们放在前面。

不过这里有个坑：Step Plan 有专用的 API 地址，不能跟普通 API 混用。

再看模型覆盖和路由。

从能力覆盖上看，这次会用到下面几类模型：

| 模型 | 这篇文章里的用途 |
| --- | --- |
| `step-3.5-flash-2603` | 代码审查、多文件理解、复盘纪要整理 |
| `step-router-v1` | 观察简单任务和复杂任务的路由体感 |
| `stepaudio-2.5-tts` | 生成模拟会议录音和语音摘要 |
| `stepaudio-2.5-asr` | 把会议音频转成文本 |
| `step-image-edit-2` | 本文没有展开，只在能力覆盖里带到 |

不过这篇不准备把每个模型都拉出来念一遍参数。参数表留给文档，我更想看两个具体工作流：一个偏 Coding，一个偏语音应用。

step-router-v1 是我比较感兴趣的一个点。它主打按任务复杂度自动调度模型。这里我不会把它当成性能结论来讲，只看它放进实际任务后的体感。

最后是工具链接入。

Step Plan 可以接入 OpenClaw、Claude Code、Cline、Roo Code 这类 AI 工具。对已有工具链的团队来说，它更像一个可替换的模型后端，而不是一套需要重新学习的新工具。

## 环境准备：把 Step Plan 接入 AI Coding 工具

### API Key 获取

先去阶跃官网完成订阅并获取 API Key：

https://platform.stepfun.com/step-plan

订阅完成后，在控制台创建 API Key，妥善保管。

![创建 API Key](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/create-api-key.png)

### Base URL 配置

这是最容易踩坑的地方。

Step Plan 有专用的 API 地址：`https://api.stepfun.com/step_plan/v1`

而阶跃的普通 API 地址是：`https://api.stepfun.com/v1`

很多人配置失败就是因为把 Base URL 写成了普通地址，结果模型调用全走了另一个计费体系。这里别省事，Step Plan 必须用专用地址。

### Claude Code 接入方式

Claude Code 支持通过环境变量切换底层模型。接入 Step Plan 有两种方式：配置文件法和 CC Switch 可视化切换。只想稳定使用 Step Plan，直接写配置文件就行；经常在 Claude、DeepSeek、MiniMax、Step Plan 之间切换，再考虑 CC Switch。

#### 方式一：配置文件法（推荐）

如果你本机没有安装 Claude Code，先运行下面这行命令安装（Node.js 18+）：

```bash
npm install -g @anthropic-ai/claude-code
```

编辑或新增 Claude Code 配置文件 `~/.claude/settings.json`，添加 `env` 字段，把 Step Plan 的后端地址、模型和 API Key 都写进去：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_step_plan_api_key",
    "ANTHROPIC_BASE_URL": "https://api.stepfun.com/step_plan",
    "ANTHROPIC_MODEL": "step-3.5-flash-2603",
    "ANTHROPIC_SMALL_FAST_MODEL": "step-3.5-flash",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

注意替换 `your_step_plan_api_key` 为你的 Step Plan API Key。这里我把主模型配置为 `step-3.5-flash-2603`，把小模型配置为 `step-3.5-flash`。如果你想直接体验智能路由，把 `ANTHROPIC_MODEL` 改成 `step-router-v1` 即可。

配置完成后启动 Claude Code：

```bash
claude
```

首次启动需要选择信任当前文件夹。

#### 方式二：CC Switch（可视化切换）

如果你经常在多个 Provider 之间切换，可以用 CC Switch 管理 Claude Code 的模型配置。

![CC 选择 StepFun](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/cc-chose-step.png)

这里不展开安装过程，核心配置还是那几个字段：Provider 名称填 Step Plan，Base URL 填 `https://api.stepfun.com/step_plan`，主模型填 `step-3.5-flash-2603`。如果要测试 Router，就单独建一个配置，把主模型改成 `step-router-v1`。

#### 验证是否生效

直接在命令行输入 `claude`，或者进入 Claude Code 界面后输入 `/status` 确认当前模型。如果 model 显示为 `step-3.5-flash-2603` 或 `step-router-v1`，就说明接入成功。

![验证是否生效](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/verify-model-status.png)

到这里，Claude Code 就会走 Step Plan 的后端，后续的代码阅读、代码审查、重构和文档生成都会用这套配置。

如果你用的是 Cline、Roo Code 或 OpenClaw，操作方式类似——在设置中找到 `Custom API Endpoint` 或 `Base URL` 选项，填入 `https://api.stepfun.com/step_plan/v1`，然后填入对应的模型名称即可。

## 实战一：用 Step 3.5 Flash 2603 做代码审查 Agent

代码审查拿来试 Agent 很合适，因为它既要读文件，也要做判断，还不能乱改代码。

一次像样的审查，通常要理解 Controller、Service、工具类、前端页面之间的联动；中间还会穿插搜索、文件读取、测试扫描和构建验证。输出如果只有一句“代码有问题”，基本没法用，最好能落到问题分类、严重程度和修复建议。

这类任务不花哨，但很接近真实开发。

这里用我正在写的一个多智能体股票项目`agent-invest`做验证，技术栈是 Java 21 + Spring Boot 4 + AgentScope Java + Vue 3 。

我选的是其中的预警模块。这个模块刚好横跨后端 Controller、Service、技术指标判断和前端条件枚举。只要漏一个点，就可能出现前后端不一致、预警误触发或漏触发。

我给这次任务加了两个约束：

1. 第一轮只读审查，不允许改代码；
2. 第二轮最多只修一个问题，不让 Agent 一口气大改。

代码审查最怕模型兴奋起来顺手重构了太多内容，看起来做了很多事情，最后 Review 成本反而更高。

实际工作场景使用 Agent，核心考量是让它在可控范围内把事情做完。

这是我向 Claude Code 下达的第一条指令：

![代码审查指令](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/code-review-instruction.png)

它先读了 6 个核心文件，又继续搜了表单校验类、测试目录和回测服务。

这样做事合理的，因为预警模块的问题往往不在单个文件里，而在前后端枚举、白名单和触发逻辑的联动里。

第一轮，它先把预警条件捋了一遍。  

价格预警这边有 7 个条件，比如 `ABOVE`、`BELOW`、`CROSS_UP`、`VOLUME_SURGE`。  

技术预警这边更多，一共有 14 个条件，比如 `RSI_OVERBOUGHT`、`MACD_GOLDEN_CROSS`、`BOLL_BREAK_LOWER`。  

后端白名单一共 21 个，数量和前端条件列表能对上。

不过 Agent 也指出了一个架构层面的隐患：前端枚举和后端白名单是两份手写列表，后续新增条件时如果漏改某一侧，就可能出现“后端支持但前端不可选”或“前端可选但后端拒绝”的问题。

这个判断很像真实 Review：当前不是 Bug，但它是一个容易复发的维护风险。

然后才开始列问题。

Agent 输出了一份很长的结构化报告，覆盖了技术指标空值保护、冷却时间、重复触发、参数校验、交易时段判断、异常日志和测试覆盖。

![Agent 输出了一份很长的结构化报告](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/agent-review-report.png)

比如交易时段判断这一条，代码里是这样写的：

```java
private boolean isMarketOpen() {
    LocalDateTime now = LocalDateTime.now();
    int dayOfWeek = now.getDayOfWeek().getValue();
    if (dayOfWeek > 5) {
        return false;
    }

    int timeValue = now.getHour() * 100 + now.getMinute();
    return (timeValue >= 930 && timeValue <= 1130) || (timeValue >= 1300 && timeValue <= 1500);
}
```

对于 A 股来说，交易时间应该按北京时间判断。如果应用部署在非 `Asia/Shanghai` 时区的服务器上，`LocalDateTime.now()` 就会使用服务器默认时区，预警扫描可能在错误时间运行。

这类问题交给 Agent 扫一遍有收益。它不是语法错误，也不一定会在本地开发暴露，但一旦部署环境时区不一致，影响的是整条预警流程。

报告出来之后，我先人工复核。

这里我想强调一句：Agent 的 Review 报告不能直接照单全收。

这次 Step 3.5 Flash 2603 的报告里，有几个结论很有价值，也出现了两三处误判。

举两个例子。它一开始把“重复触发”判断成高风险，但这块代码里已经有冷却时间控制，只是实现方式不够直观；它还建议把一段参数校验前移到 Controller，我最后没有采纳，因为现有 Service 层校验更接近项目里的其他写法。这里不能怪模型“错得离谱”，更像是它没完全吃透项目里的约定。

AI 代码审查的价值不在于“模型说什么都对”，更现实的价值是帮你把搜索范围从几十个文件收敛到几个高风险点。

我们作为 Reviewer 仍然要做最后判断，尤其是并发语义、数据库原子更新、框架校验规则这类地方。

最后只挑一个问题让它修。

这里我们选择了一个比较具体的修复目标：交易时段判断显式使用 `Asia/Shanghai` 时区。

![交易时段判断显式使用 `Asia/Shanghai` 时区](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/timezone-fix.png)

大概一分多钟之后，修复就完成了。

修复方向是正确的，交易时段改为按 Asia/Shanghai 判断。并且，新增测试类，共 11 个用例，覆盖开盘、休市、午间、周末和边界值。


![修复方向正确](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/fix-completed.png)


## 实战二：用 Step Plan 做会议转写与播客摘要 Agent

代码审查已经覆盖了 Agent / Coding 方向，第二个 Demo 如果继续做文字整理，会和前面有点重叠。我更想试的是另一个方向：把一次技术复盘会议录音，自动转成会议纪要、行动项和可播放的语音摘要。

这个场景很常见。线上故障复盘、架构评审、需求澄清会，大家聊的时候信息密度很高，但会后整理经常没人愿意做。手动听录音、补上下文、提炼决策和风险点，费时间，还容易漏掉关键动作。

更麻烦的是，录音本身很难进入工程协作流程。你不能指望每个没参会的人都把 30 分钟录音从头听一遍，也不能把“会议里好像说过”当成行动项依据。

所以这次不再铺概念，直接跑一个可以复现的最小 Demo：先用 TTS 生成一段模拟会议录音，再用 ASR 转写，接着让文本模型整理纪要，最后再用 TTS 生成 60 秒语音播报。

这个方案会用到三个模型：`stepaudio-2.5-tts` 先生成一段可控的模拟会议录音，`stepaudio-2.5-asr` 负责转写，`step-3.5-flash-2603` 再把转写内容整理成复盘纪要。最后再回到 TTS，生成一段可以直接发给同事听的音频摘要。

### 一个简单的能直接跑通的 Demo

为了能够让感兴趣的朋友快速本地跑起来，我写了一个只依赖 Node.js 18+ 的例子。你只需要按照前面的提到的方法准备一个  Step Plan API Key 就可以了。

先创建一个目录：

```bash
mkdir step-audio-demo
cd step-audio-demo
npm init -y
npm pkg set type=module
```

然后新建 `demo.mjs`：

```js
import fs from "node:fs/promises";
import path from "node:path";

const apiKey = process.env.STEP_API_KEY;
const baseUrl = "https://api.stepfun.com/step_plan/v1";
const outputDir = path.resolve("output");

if (!apiKey) {
  console.error("请先执行：export STEP_API_KEY=你的 Step Plan API Key");
  process.exit(1);
}

await fs.mkdir(outputDir, { recursive: true });

const meetingScript = [
  "各位同步一下昨晚的订单查询接口超时问题。",
  "从监控看，二十一点四十分开始，订单详情页 P95 延迟从二百毫秒升到了三点二秒。",
  "日志里 Redis 读取多次超过一秒，OrderQueryService 当前没有明确的缓存降级逻辑。",
  "临时处理是把 Redis 读取超时调到三百毫秒，并打开本地兜底缓存。",
  "后续需要三件事：第一，梳理缓存调用链路；第二，补充 Redis 连接池监控；第三，给订单查询接口加降级测试。",
  "根因现在还不能完全下结论，需要结合追踪和 Redis 客户端指标再确认。"
].join("");

async function requestJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${await response.text()}`);
  }

  return response.json();
}

async function textToSpeech(input, fileName, instruction) {
  const response = await fetch(`${baseUrl}/audio/speech`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "stepaudio-2.5-tts",
      voice: "cixingnansheng",
      input,
      instruction,
      response_format: "mp3"
    })
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${await response.text()}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  const filePath = path.join(outputDir, fileName);
  await fs.writeFile(filePath, buffer);
  return filePath;
}

function pickTextFromAsrEvent(event) {
  return event?.text
    ?? event?.result?.text
    ?? event?.data?.text
    ?? event?.choices?.[0]?.delta?.content
    ?? "";
}

async function speechToText(audioFile) {
  const audioBase64 = await fs.readFile(audioFile, "base64");
  const response = await fetch(`${baseUrl}/audio/asr/sse`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "Accept": "text/event-stream"
    },
    body: JSON.stringify({
      audio: {
        data: audioBase64,
        input: {
          transcription: {
            model: "stepaudio-2.5-asr",
            language: "zh",
            hotwords: ["OrderQueryService", "Redis", "P95"],
            enable_itn: true
          },
          format: {
            type: "mp3"
          }
        }
      }
    })
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${await response.text()}`);
  }

  const streamText = await response.text();
  const events = streamText
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim())
    .filter((line) => line && line !== "[DONE]")
    .map((line) => JSON.parse(line));

  const transcript = events.map(pickTextFromAsrEvent).join("").trim();
  await fs.writeFile(path.join(outputDir, "asr-events.json"), JSON.stringify(events, null, 2));
  return transcript || streamText;
}

async function summarizeTranscript(transcript) {
  const result = await requestJson(`${baseUrl}/chat/completions`, {
    model: "step-3.5-flash-2603",
    messages: [
      {
        role: "system",
        content: "你是技术复盘助手，只能基于用户给出的会议转写整理内容。没有提到的信息必须标注为待确认。"
      },
      {
        role: "user",
        content: `请基于下面的会议转写输出技术复盘纪要，包含：已确认事实、根因方向、行动项、待确认问题、60 秒口播稿。\n\n会议转写：\n${transcript}`
      }
    ]
  });

  return result.choices?.[0]?.message?.content ?? JSON.stringify(result, null, 2);
}

console.log("1. 生成模拟会议录音");
const meetingAudio = await textToSpeech(
  meetingScript,
  "meeting-review.mp3",
  "团队技术复盘会议，语速中等，表达清楚，像真实会议同步"
);

console.log("2. 使用 ASR 转写会议录音");
const transcript = await speechToText(meetingAudio);
await fs.writeFile(path.join(outputDir, "transcript.md"), transcript);

console.log("3. 生成结构化纪要和口播稿");
const summary = await summarizeTranscript(transcript);
await fs.writeFile(path.join(outputDir, "summary.md"), summary);

const podcastScript = summary
  .split("60 秒口播稿")
  .pop()
  .replace(/^[:：\s#-]+/, "")
  .slice(0, 900);

console.log("4. 生成语音摘要");
await textToSpeech(
  podcastScript || "订单查询接口超时问题已完成初步复盘，后续需要继续确认 Redis 指标和链路追踪。",
  "incident-summary.mp3",
  "团队内部技术播报，语气克制，不夸大事故影响，语速中等"
);

console.log("完成。请查看 output 目录：");
console.log("- output/meeting-review.mp3：模拟会议录音");
console.log("- output/asr-events.json：ASR SSE 原始事件");
console.log("- output/transcript.md：ASR 转写结果");
console.log("- output/summary.md：结构化复盘纪要");
console.log("- output/incident-summary.mp3：语音摘要");
```

运行：

```bash
export STEP_API_KEY=你的 Step Plan API Key
node demo.mjs
```

跑完以后看一下 `output` 目录，里面会多出几份文件。

![跑完之后，`output` 目录会出现 5 个文件](https://oss.javaguide.cn/github/javaguide/ai/coding/step-plan-2025-05-10/demo-output-files.png)

`meeting-review.mp3` 是刚才用 TTS 生成的模拟会议录音，`transcript.md` 是 ASR 转写结果，`summary.md` 是模型整理出来的复盘纪要，`incident-summary.mp3` 是最后生成的语音摘要。

还有一个 `asr-events.json`，这个平时不用看，但建议保留。ASR SSE 解析出问题时，它能帮你确认到底是接口返回异常，还是我们自己的解析逻辑写错了。

这样设计有个好处：读者不需要先找一段真实会议录音，也不需要担心隐私问题。先用 TTS 生成一段可控音频，再用 ASR 识别它，本质上是在做一条“语音输入 → 文本理解 → 语音输出”的闭环验收。

这里也不是一次就完全顺。第一次写脚本时，我默认 ASR SSE 每条事件里都会有固定的 `text` 字段，结果不同事件结构并不完全一样。后来才加了 `pickTextFromAsrEvent` 这个兼容函数，并把 `asr-events.json` 落盘。这个文件看起来像调试垃圾，真排查转写问题时很有用。

`stepaudio-2.5-tts` 比较有意思的地方是语境控制。`instruction` 控制整段声音的表达基调，正文里的圆括号还可以做句内控制。比如：

```text
（稍微停顿）这次问题还不能直接下根因结论，需要继续看 Redis 客户端指标。
```

TTS 的 instruction 很有意思。圆括号里的内容会被当成表达指令，不会直接读出来。我们可以用它控制停顿、语速，甚至加一句“别像广告配音”。这对技术播报很有用。

ASR 的话，热词很重要。`Redis`、`P95`、`OrderQueryService` 这些专有名词，没有热词辅助容易被识别成相近的普通词。Demo 里我是这样配的：

```js
hotwords: ["OrderQueryService", "Redis", "P95"]
```

真实项目里把服务名、类名、中间件名、业务缩写都加上。这个细节不大，但转写错了后面的总结就跟着跑偏。

纪要生成最怕的是模型写得太像真的。会议录音里只说“Redis 读取耗时异常”，它不能直接给你输出“根因是 Redis 连接池耗尽”。所以 Prompt 里要卡住边界：没提到的信息标待确认。复盘不是写小说，边界要严。

### Demo 效果

来看看实际的转语音效果，还是非常不错的，语气很气然清晰：



这类语音 Agent 干的是一件具体活：把“听完才能知道发生了什么”的音频，变成“扫一眼就能执行、点一下还能听”的结构化信息。

我会先把它放在这些场景里试：

- 会议录音转写；
- 故障复盘纪要生成；
- 行动项和待确认问题提取；
- 面向未参会同事的口播摘要；
- 周会、评审会、需求会的会后同步。

但下面这些地方必须人工兜底：

- 关键结论是否真的在会议中出现；
- 负责人和截止时间是否准确；
- 根因判断是否有监控和日志支撑；
- 是否涉及敏感信息、客户信息或内部安全细节；
- 音频摘要能不能对外分发。

如果放进真实项目，我会把流程拆成几步：先把会议录音转成逐字稿，再把逐字稿、日志和复盘模板交给文本模型整理，简单摘要和复杂追问可以交给 Router 分流，最后把口播稿交给 TTS。它不能替你判断事故根因，只能把会后整理这件重复劳动压缩到更短的时间里。

## 如果引入 Step Router V1：让模型自动分流任务

### 为什么需要路由

在实际开发中，不是每个任务都需要最强的模型。

简单解释、命令生成这类任务，通常更看重响应速度；多文件代码审查、复杂重构这类任务，更依赖上下文理解和任务拆解。step-router-v1 的思路就是把这层选择交给路由，不让开发者每次手动切模型。

### Router 的工作原理

step-router-v1 会在内部自动评估任务复杂度，在 `deepseek-v4-pro` 和 `step-3.5-flash` 之间切换。切换逻辑由路由层自动完成，开发者只需要指定使用 router 模型即可。

配置方式很简单：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_step_plan_api_key",
    "ANTHROPIC_BASE_URL": "https://api.stepfun.com/step_plan",
    "ANTHROPIC_MODEL": "step-router-v1",
    "ANTHROPIC_SMALL_FAST_MODEL": "step-3.5-flash",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

如果用 CC Switch，新建一个 Step Router 配置，把主模型填成 `step-router-v1` 就行。

### 实际体验

Router 我也顺手试了下。  

我没做严格对比测试，就是拿几个常见任务跑了一圈，看它会不会明显掉链子。

**场景一，简单问答。**

```
问：Java 中 StringBuilder 和 StringBuffer 的区别是什么？
```

这类问题响应很快，答案也够用。

**场景二，多文件代码审查。**

同上的代码审查任务，Router 模式下输出没有明显缩水。这个结论只限于这次样例，我不会把它扩展成性能判断。

**场景三，复杂重构任务。**

```
请帮我评估 AlertMonitorService 中预警触发流程的重构方案，要求：
1. 拆分价格预警、技术指标预警和通知分发边界
2. 保持现有触发语义不变
3. 标注哪些改动需要人工确认
4. 输出单元测试补充清单
```

这个任务处理时间更长，输出比简单问答细很多。至于背后是不是切到了更强模型，我看不到内部路由结果，所以这里只能按体感描述。

至少在这几个样例里，Router 的自动分流思路说得通：简单任务不会被过度处理，复杂任务也没有因为模型选择过轻导致输出明显塌掉。

不过它也有一个不太舒服的地方：Router 的切换逻辑是黑盒的。你无法控制什么时候走快模型、什么时候走强模型。对需要精确控制模型选择的人来说，这个点要提前接受。

## 总结

这轮跑下来，我最关心的不是它模型列表有多长，而是能不能进日常工作流。

代码审查这块，它能帮我先把风险点扫一遍，把 Review 范围从一堆文件收窄到几个可疑位置。最后判断还是要人来做，但它确实能省掉不少前期翻代码的时间。

语音这块也比我预期更完整。会议录音可以转写成文字，再整理成纪要和行动项，最后还能生成一段语音摘要。这个链路跑通以后，就不只是“模型能不能回答问题”了，而是能不能接进真实协作流程。

当然，边界也很明显。

Agent 的报告不能照单全收，会议纪要不能把推测写成结论，Router 背后到底切到哪个模型也看不到。这些地方都需要人工兜底。

所以我的建议是：如果你只是偶尔问几句代码，没必要为了订阅制专门折腾一套配置。

但如果你本来就高频跑 Agent 任务，或者团队里经常有会议转写、故障复盘、内部语音同步这类需求，Step Plan 值得试一下。
