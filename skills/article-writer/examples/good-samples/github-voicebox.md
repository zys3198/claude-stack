
想要克隆自己的声音做配音，ElevenLabs 当属首选，它这个功能做的的确不错。

但每月几十刀的费用，加上音频数据要上传到他们服务器，对不少人来说都是个门槛。

对于语音输入也有不错的工具，比如 WisprFlow，可同样要付费，隐私同样存疑。

今天在 GitHub 上发现一个名叫 **Voicebox** 的开源项目，狂揽了 28000+ Star。

![image-20260524173756834](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQonDAbO90wuIicOdCBEfbcQvf1Fcu8JOnxmdZloy7RQAqf6tR3uYFSmsanmqlXa0KxBuicuu1YZMicCDOXFbysiacso6icv3ibWpEzEXo/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=0)

它的核心定位是 ElevenLabs 和 WisprFlow 的开源平替，以本地优先的 AI 语音工作室。

在语音市场上，ElevenLabs 主攻语音输出，WisprFlow 主攻语音输入，它两算是各占一边。

这一次 Voicebox 把两边都做了，额外还用一个本地 LLM 把中间的改写、人格化环节串了起来。

也就是说，我们克隆出来的声音、录下的语音片段，全程不会离开自己的电脑，数据隐私安全。

![image-20260524173906368](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQom97PB0eicMvsfxF5tZicEFNsJXks43K66g9uYBLshHianX8z2P1bCHtWZn9wGO1Tuiau3mOUXZGJux7XdWtpF1c9BXZ4z8SuVJoWI/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=1)

先来说说工具的声音克隆这块。

只需要我们提供几秒钟的参考音频，就能生成一个属于我们自己的声音模型。

覆盖 23 种语言，从英语、中文到阿拉伯语、印地语、斯瓦希里语，主流语言都支持。

内置 7 个 TTS 引擎，包括 Qwen3-TTS、Chatterbox、LuxTTS、Kokoro 等。

不同引擎各有作用，比如 Chatterbox Turbo 支持 `[laugh]`、`[sigh]` 这类情绪标签，能让生成的语音带笑声、叹气等真实情绪。

而 Qwen3-TTS 则擅长多语言克隆，还能听懂「慢一点说」「用耳语」这种自然语言指令。

至于没有独立显卡的同学，可以选 Kokoro，模型只有 82M，CPU 也能跑得动。

![image-20260524173936464](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQomoRMTR1L0XK6WvxdXmviaHCHfCiaqY5mGm1BeiczXgKJ2qOuRibwcW7Nu7Bl6IGc2HYyTo1gK2kxFdxnQtkgF6yu9iaxQTEwencLG0/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=2)

如果不想克隆自己的声音，项目也内置了 50 多个预设音色，可以直接开箱可用。

生成出来的音频还能进行编辑，调音、混响、延迟、压缩这些参数都能实时预览。

接下来要说的，这个项目另一个让我觉得挺有意思的功能，那就是可以给 Agent 工具配音。

Voicebox 提供一个 MCP 服务器协议，任何支持 MCP 的 Agent 工具，都能调用它来发声。

比如将其接入到 Claude Code，只需要一行命令：

```
claude mcp add voicebox \
```

添加完成后，Claude Code 就能直接用我们克隆的声音说一句「测试通过，可以合并」。

![image-20260524174109292](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQolbgacibibdvibbWNQ4kJqAy0iaJoicZ62kRufv4icjNx76hPPxXdx6UJGOxlkQ5Hr2VG4fNYZ09wUluuXOgVytAgiagWJEEzwL7hgUho/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=3)

我们还能在设置里给不同的 Agent 绑定不同的声音，听声音就能分辨是哪个 Agent 在报告。

这样我们在写代码的间隙，就能听到熟悉的声音报告进度，让我们的开发体验更上一个台阶。

另外 Voicebox 还有一个更进阶的玩法，叫人格化。

我们可以给每个声音绑一段自由格式的人设描述，比如「冷静的工程师」「毒舌的代码审查官」。

之后无论是手动生成，还是 Agent 通过 MCP 调用，文本都会先经过本地 LLM 按人设改写，再合成语音。

也就是说，Agent 说出来的话不只是声音由你定的，连说话风格也可以自由设定。

不止于此，还提供一个全局快捷键听写功能，按住热键说话，松开后文字会自动粘贴到当前聚焦的输入框。

在 macOS 上的体验做得不错，会通过辅助功能 API 精确识别目标文本框，粘贴过程不会污染剪贴板。

![image-20260524174149896](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQon76fzAbOiaYKoFdNso9mT62CichnX1tJoA9oeRcsMz1lLuic80lzqPKhS7kgIqKib9vEwn0XiaicMAcrTx82q6UbdgvzEQic8rq3w5Eg/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=4)

至于安装，项目提供了 macOS、Windows 的安装包，可到官网或 Releases 页面下载。

首次使用会自动下载模型权重，Kokoro 只有 82M，Qwen3-TTS 要几个 G，可按需下载。

再提一句，在苹果 M 芯片上跑，速度比通用方案快不少，NVIDIA 显卡则会自动走 CUDA。

至于 REST API 和 MCP Server 默认监听本地 17493 端口，文档地址在 `http://127.0.0.1:17493/docs`，对接自己的脚本和工具非常方便。

![image-20260524174408561](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQolJPMYyibRHrc8eibBhw5BkenA2sdoZLibicic1cxZVfsdmRfZCBSTMHRjtp2h1yiabw7LXzRgqoOSO4vCfuJmTWqpAWiclbr3OSgic3JY/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=5)

#### 写在最后

讲真的，在我看来，语音 I/O 的本地化是一件迟早要发生的事。

但也不得不承认，云端在便利性上确实有优势，可订阅成本和数据隐私这两道坎一直在。

我们的声音特征数据，真要是被泄露或者被滥用，后果可能跟密码泄露差不多严重。

这也是为什么语音本地方案的需求，越来越被重视的原因之一。

好在这两年，开源模型的不断迭代更新，基本是肉眼可见地速度在追平闭源模型的效果。

再加上也可在苹果 MLX、NVIDIA CUDA 这些消费级硬件，本地跑 TTS、STT、LLM。

而 Voicebox 的价值，我觉得不止在功能上的实用，更给我们提供一个新的可能。

以后使用 Agen，我们不一定非得对着一个冰冷的对话框，也可以让它说话、有情绪、有名字。

未来很快 AI Agent 即将从纯文本输出工具，逐渐演化成有声音、有人设的协作伙伴。

至于会不会成为主流，我们就拭目以待吧。

GitHub 项目地址：https://github.com/jamiepine/voicebox

今天的分享到此结束，感谢大家抽空阅读，我们下期再见，Respect！