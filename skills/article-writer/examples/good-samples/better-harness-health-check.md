> 出处 微信公众号「JavaGuide」2026-09-10《阿里又开源了一个专门给 Claude Code、Codex 做“体检”的项目》｜https://mp.weixin.qq.com/s/MZAi896T1KjVYkDFoomNJA

# 阿里又开源了一个专门给 Claude Code、Codex 做“体检”的项目

> JavaGuide / 小G | 2026/09/10 07:19:57

出差已经快一周了。。。最近有好几个读者反馈，在用 Claude Code、Codex 写代码的时候，经常会遇到很多问题，例如：需求理解偏了，Agent 还是能很快交出一堆改动；测试命令明明写在项目里，这次却没跑；同一个坑已经踩过两遍，下一次换个会话还会再来一遍。
只看最终 Diff，很多时候都看不出问题到底出在哪。到底是 AGENTS.md 没写清楚，还是 Skill 没有接到任务里，或者是其他问题？
昨晚，我在 GitHub 上发现了阿里 Qoder 刚开源的 Better Harness，刚好能够解决这个问题。
它会顺着一次 Agent 任务往回查，把项目规则、Skill、脚本、测试、CI 和宿主能够提供的会话证据放在一起看，再指出哪一环缺了证据、该从哪里改。

Better Harness 官网首页Better Harness 采用 MIT 协议，截至发文，已经有约 2.2K Star。

Better Harness 是什么？
Harness 放到 AI 编程里，可以把它理解成 Agent 身边那套配套设施：任务开始前有哪些项目规则和验收条件，执行时能调用哪些 Skill、命令和 MCP，改完后要跑什么测试，最终又要经过谁的审核和哪条 CI。

Better Harness 检查的就是这套配套设施。它在现有 Coding Agent 中运行，收集项目证据，以及宿主能够提供的会话证据，然后生成一份带来源的检查报告。你不用为了它再换一个 Agent，Claude Code、Codex、Qoder 等宿主都有各自的接入方式。

一份报告会列出当前项目的 Agent 配置、工作流中缺少的环节、修改范围和验收方式。官方把这个过程称为 Harness Engineering。落到日常开发里，其实就是查清楚：Agent 为什么又漏了同一件事，这次该改哪份规则或哪条自动化检查。
它解决了什么问题？
这些配套设施平时散落在不同位置。AGENTS.md 里写了一句“提交前检查文档链接”，不代表 Agent 真找得到检查命令；仓库里有测试，也不代表这次改动跑过。任务交付后只看 Diff，看到的只是结果，很难还原中间哪一步断了。
Better Harness 把一项任务分成五段来检查：
检查维度
它在追问什么
常见证据
Task Understanding
Agent 是否知道目标和完成标准
规则、AGENTS.md、Spec、DESIGN.md
Controlled Execution
执行方式能否复现，边界是否明确
Skill、命令、MCP、沙箱
Change Validation
改动是否经过验证
测试、Lint、Hook、诊断信息
Reliable Delivery
审核和交付检查有没有被绕过
人工 Review、审批、CI/CD、恢复流程
Learning Capture
这次经验能否留给后续任务
可复用 Skill、Memory、Loop Discovery

Better Harness 的五段式 Agent Work Loop这五段对应的正是常见的几类麻烦：需求写了，完成标准没写；命令有了，Agent 不知道什么时候调用；测试放在仓库里，却没接进这次任务；改动很快合并，Review 和 CI 被绕过；上次踩过的坑，只留在已经结束的聊天里。
图里的 Learning Capture 我比较在意。很多团队遇到一次 Agent 失误，第一反应是继续往规则文件里加文字。规则越积越长，重要要求反而更难被看到。Better Harness 会继续追问这次问题该落到哪里：只是偶发失误，还是应该补一条规则、一个 Skill、一段脚本，或者干脆交给 Hook 和 CI 强制执行。
有什么亮点？
从现有文档和样例看，我最看重的是它对证据的处理。发现某个配置文件存在，只能说明 Present；已经接入工作流是 Wired；这次任务确实调用过，才算 Exercised；要证明调整改善了结果，还得等后续相近任务给出可比较的数据。
没有观察到的行为会直接标出来。仓库里躺着一个测试文件，不会自动换来“验证已经完成”的结论。这能挡住一种很常见的误判：工具和规则都装了，看起来很全，Agent 实际执行时却一次也没用上。
每条发现都会带上证据、影响、期望结果、建议修复范围和验收方式，不会只留一句“建议完善测试流程”。
官方样例报告里就有这样一个问题：一个 Skill 同时声称支持 Qoder 和 Codex，但现有的前向测试只覆盖了 Qoder。报告没有直接断言 Codex 已经失败，而是把缺口限定为“缺少 Codex 侧的发现、触发和输出校验”，随后给出补测范围与验收命令。

Better Harness 官方样例中的问题与修复建议比如你想查“为什么文档改动经常漏掉链接验证”，Better Harness 会去找规则有没有提到、检查命令是否存在、是否接到了 Hook 或 CI、相关任务里到底有没有执行记录。结果可能只需要补一条 CI 检查，也可能是 Agent 根本不知道该调用哪段脚本。
仓库里还带了一个 Harness Inspector。它把用户意图、Agent 的中间过程、工具调用、文件和提交串起来，适合回看一项改动是怎么走到最终结果的。Inspector 使用只读工作区；官网公开演示使用的是虚构数据，不会读取本地项目。

Harness Inspector 会话视图历史报告还能按五个维度查看变化。不过项目方给这项功能留了限制：趋势只说明记录发生了变化，单凭一条上升曲线不能证明某次调整带来了提升。真要验证，还得在后续相近任务里重新跑一遍。
怎么用？
Better Harness 没有给所有编程 Agent 硬套同一个入口。它目前列出了 10 个 Host Adapter，其中 6 个有经过验证的安装路径；不同宿主能拿到的会话证据和报告形式也不完全一样。下手之前，最好先看项目维护的 Host Adapter Matrix。
我更建议从自己正在使用的宿主装起。以 Codex Desktop 为例，进入 Settings > Plugins，选择 + Add > From Marketplace，填入下面的仓库地址，Git ref 使用 main，Sparse paths 留空：
https://github.com/QoderAI/better-harness.git

在 Codex Desktop 中添加 Better Harness Marketplace安装完成后开一个新任务，再输入一个具体问题。不要一上来让它“全面优化工作流”，范围太大，报告也容易散。比如：
@better-harness 检查为什么这个项目的文档修改经常漏掉链接验证，
生成带证据、修复范围和验收步骤的报告。
Codex CLI 的安装命令是：
codex plugin marketplace add \
  'https://github.com/QoderAI/better-harness.git' \
  --ref main
codex plugin list --marketplace better-harness
codex plugin add better-harness@better-harness
新任务里通过下面的入口调用：
$better-harness:better-harness 检查为什么这个项目的文档修改经常漏掉链接验证，生成带证据的报告。
Claude Code 则通过插件市场安装：
/plugin marketplace add QoderAI/better-harness
/plugin install better-harness@better-harness
安装后可以先在终端运行 claude plugin details better-harness@better-harness，确认详情里出现 Skills (1) better-harness，随后新开会话，通过 /better-harness 调用。默认报告会写到项目的 .claude/better-harness/ 目录，包括 HTML、Markdown 和 findings.json。

Qoder Desktop 已经内置 Better Harness，不需要再装插件。打开要检查的仓库，新建会话后运行 /better-harness 即可；Qoder 1.18.0 及以上版本也可以从 Quest 左侧进入 Better Harness（Beta）。

其他适配还包括 GitHub Copilot CLI、Qwen Code、Pi、Kimi Code、WorkBuddy、Grok 和 Cursor。这些平台的安装状态并不一样。
Better Harness 产出的修复建议更适合先审一遍，再放到单独任务里执行。它会读取项目文件，以及宿主能够提供的相关会话证据；涉及公司仓库时，权限范围和最终报告里包含的内容也得自己确认。
总结
Better Harness  是 QoderAI 开源的 Harness Engineering 工具。
它不评估代码，核心是用 Agent Work Loop 五维度（目标理解、受控执行、变更验证、可靠交付、经验沉淀）给你的 Claude Code、Codex 等 AI 编码工作流做体检，输出证据支撑的报告，缺失证据保持“未观察到”而不编造。
项目地址： https://github.com/QoderAI/better-harness

⭐️推荐阅读:
AIGuide：AI 应用开发、AI 编程实战与面试指南（对标 JavaGuide，完全开源免费）
JavaGuide： Java 面试指南和后端通用面试复习资料（Github 157k+ Star）
《SpringAI 智能面试平台》（2.0 版本已开源）(Star 数量 3k+)
