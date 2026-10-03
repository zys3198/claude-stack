# 协议总表

每个领域一份协议，各管各的。领域按触发场景切——触发场景不同就分开，同一场景的不同侧面合成一份。协议正文落在 `~/.claude/docs/` 下（多数在 `docs/protocols/`，会话生命周期在 `docs/` 顶层），本表只做索引：哪份协议在哪、怎么校验。

新增一份协议时，在本表加一行；新建流程与判据见 `~/.claude/skills/asset-guide/SKILL.md` 的八步。

| 领域 | 协议在哪 | 校验或执行者 | 状态 |
|---|---|---|---|
| 台账 | `~/.claude/docs/protocols/ledger/ledger.md` | `python ~/.claude/hooks/scripts/ledger_check.py` | **已落** |
| 任务笔记 | `~/.claude/docs/protocols/task-notes/task-notes.md` + `task-notes/` | — | **已落** |
| 执行环境 | `~/.claude/docs/protocols/execution-env/execution-env.md` | `~/.claude/hooks/scripts/pretool-guard.py`（PreToolUse 合并入口，内跑 `product-guard.py` 与 `resource-guard.py`） | **已落** |
| 会话生命周期 | `~/.claude/docs/session-lifecycle.md` | `~/.claude/hooks/scripts/session-guard.py`（SessionStart／SessionEnd） | **已落** |
| 记忆 | `~/.claude/docs/protocols/memory/memory.md` | `protocol-report.py`（内含 `protocol_check.py`） | **已落** |
| 委派 | `~/.claude/docs/protocols/delegation/delegation.md` + `delegation/` | — | **已落** |
| 门禁 | `~/.claude/docs/protocols/gate/gate.md`（操作规则留在 `~/.claude/CLAUDE.md` §1.3） | `python ~/.claude/hooks/scripts/protocol_check.py`；运行时经 `pretool-guard.py` 内跑 `product-guard.py`（产物／工作树守卫）与 `resource-guard.py`（资源守卫，内载入 `authorization_scope.py` 做授权范围匹配） | **已落** |
| 协作 | `~/.claude/docs/protocols/collaboration/collaboration.md` | — | **已落** |
| 执行纪律 | `~/.claude/docs/protocols/execution-discipline/execution-discipline.md` | — | **已落** |
| 证据与交付 | `~/.claude/docs/protocols/evidence/evidence.md` | — | **已落** |
| 表达 | `~/.claude/docs/protocols/expression/expression.md` | — | **已落** |
| 指令资产 | `~/.claude/docs/protocols/instruction-assets/instruction-assets.md` + `instruction-assets/` | `protocol-report.py`（内含 `protocol_check.py`） | **已落** |

「校验或执行者」列两种含义：`*_check.py`、`protocol_check.py`（含经 `protocol-report.py` 调用）是对文档的只读校验；`pretool-guard.py`（PreToolUse 合并入口，内跑 `product-guard.py`、`resource-guard.py`）、`session-guard.py`（SessionStart／SessionEnd）是运行时执行该协议的 hook。门禁与记忆共用一个脚本，两者分开报，退出码 0 才算全过。`任务笔记`、`委派`、`协作`、`证据与交付`、`表达`、`执行纪律` 的校验留 `—`：前两者的产物是各项目仓库里自由形态的记录与 prompt 模板，后三者判的是问不问、证据够不够、措辞准不准，`执行纪律` 的输入是执行者在运行时产出的基线数字与实测输出，磁盘上都没有可判的固定形态。`指令资产` 的正文由 `protocol_check.py` 的体积、重复、生命周期三项覆盖。源路径已删的项目的记忆不再被加载，脚本把它们单独分组计数、不细查。

## 共同要求

协议之间可以不一样，但每条都要满足，且每条都要有能当场判的判法：

1. **有固定落点** — 写在哪、读哪一份，不含糊。判法：能指出一个唯一路径。
2. **有固定字段** — 顺序和取值枚举写死，不靠自由发挥。判法：字段有名字、取值有集合，枚举项能穷举。
3. **有判据** — 什么进、什么不进，用一句话能判。判法：拿一条待定项，照这句话能当场判进或出。
4. **可机械校验** — 能写成一个只读检查的，就该有。判法：给出脚本命令，或写 `—` 并说明为何判不了。
5. **渐进式披露** — 每次触发都要用的留在主文件，只在特定情形用的下沉到 `references/`。判法：主文件里找不出只在部分情形才用的段落。
6. **有维护条款** — 正文写本文件的可变区与只增区分界。判法：正文有「维护条款」节，且引本节。
7. **落点与命名可机械判** — 判法：`python ~/.claude/hooks/scripts/protocol_check.py` 的「命名」与「顶层文档」两项。
8. **指针强度一致** — 必读的引用写「**必须读取**」，仅供参考的写裸「见 `X`」；这一条对 skill 与协议同样适用，不因来源不同而变。

### 协议模板

协议本体照这个骨架写，节名可改，骨架不省：

````markdown
# <领域>协议

管<一句话职责>。

## <按需的小节>

## 校验
<脚本命令；判不了的写 `—` 并说明为什么>

## 维护条款
**分界。** 会变的（…）整体重写。只增的：（…）只追加，写完不改。
删除判据与整理触发点各协议通用，见 `~/.claude/docs/protocols-index.md` 的「维护条款」。
````

## 维护条款

文档只增不整理就会沉积，沉积到最后不敢删——因为分不清哪条还活着。三条里只有「分界」因文件而异，写在协议正文；删除判据与触发点各协议逐字相同，只写在本节，正文引指针不重抄。

**一、分界。** 会变的（现状、清单、规则）必须能整体重写；只增的（依据、历史）只追加，写完不改。混在一起就没法整理。每份协议在正文的「维护条款」里写自己的分界，本节只给这条通用原则。

**二、删除判据。** 满足其一即删：

| 情形 | 动作 |
|---|---|
| 内容已在环境里（配置文件、代码、`--help` 输出） | 删——它是缓存，会过期 |
| 被本文档后面的条目覆盖 | 删旧条——两条并存会让新旧规则同时生效 |
| 只在部分情形才用到 | 下沉 `references/`，不删 |
| 指向的目标已不存在 | 删引用，或改指向 |

**三、触发点。** 每次编辑这份协议时顺手做一遍，不设「定期整理」（定期整理不会发生）。另加体量硬触发：正文逼近上限（默认 20 KB，可由协议自定）就强制复核，先删再加。

## 落点与命名

产物位置按**可重建性**分，不按类型分：先问一句「没了要不要重做」。可重新生成的（构建缓存、下载的中间文件、临时脚本与草稿）放临时目录（`.claude/tmp/`、`$CLAUDE_JOB_DIR/tmp`）；不可重新生成的（证据、报告、笔记、决定）放持久目录，且**必须被 git 追踪或进入备份范围**。不确定时按持久处理——误判成持久只浪费空间，误判成临时不可逆。

持久落点：正式文档与架构决定放 `docs/`（架构决定另见 `docs/adr/`）、任务笔记与状态放 `notes/<任务名>/`（会话出口落在其中的 `handoff/`）、截图与验收证据放 `output/`、术语表放 `CONTEXT.md`、源码放对应模块目录；跨会话事实与经验放获授权的 auto-memory。**以上目录在首次写入时创建。**

仓库根目录不新建其他文件或目录；同类产物只保留一处（一个事实只有一处）；中间结果目录加入 Git 忽略。

### 堆积时的组织

产物多起来后要能一眼区分、按主题找到。

1. **粒度**：一个文件装一件事，细到一个文件名能说清为止。一个文件塞三件事，名字只能含糊。
2. **路径载分类，轴取主题**：目录名取人找东西会走的轴——主题或板块；会话号与纯日期不进目录名。
3. **文件名载身份**：见名知意的短名，一眼看出是该板块的哪一部分。
4. **索引独立且同轴**：索引单独成文件，按同一主题轴切分（`ITEMS/<主题>-items.md`），不堆成一份；行式 `- [标题](../<主题>/<短名>.md) — <结论照抄>`。
5. **标识即短名**：不发不透明编号；索引与跨引用都用短名或路径。

会变的就地覆盖、只增的追加，分界见「维护条款」。

### 命名

名字分三段，一段载一类信息：

| 段 | 载什么 | 例 |
|---|---|---|
| 目录 | 主题或板块 | `hooks/`、`installing/`、`backups/` |
| 文件名 | 见名知意的身份 | `hook-dead-binding.md`、`skill-install.md` |
| 日期词或状态词 | 时间与状态 | `2026-09-25`、`-v1`、`.bak` |

判据只有一条：**这段信息会不会被机械使用**——排序、过滤、清除、按名寻址。会，就写成机器直接可判的形式；不会，就留在文件内容里。

**目录取主题轴。** 会话号、纯日期与状态都不进目录名：状态归现状表的状态列，目录名里再写一遍就是两处真相。

**日期一律 `YYYY-MM-DD`。** 粒度到天，同一天多次加 `-2` 序号。混用会排错序：`2026-09-21` 排在全部 `202609xx` 之前（`-` 是 0x2D，数字从 0x30 起）。

**名字一律 ASCII**，中文原名留在内容里。

**只管我们自己创建或命名的对象。** 第三方工具与 CLI 自己写的（`~/.cc-switch/backups/`、`.claude.json.backup.*`）保持原样。

工作树名同属本节：kebab-case、2～4 个词，能看懂在做什么；禁用 hash、纯日期、`tmp`、`test` 与 `agent-`／`worktree-` 开头。词数不作拦截。拦截的实现与边界见 `~/.claude/docs/session-lifecycle.md` 第七节。

校验：`python ~/.claude/hooks/scripts/protocol_check.py` 的「命名」一项。
