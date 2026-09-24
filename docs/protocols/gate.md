# 门禁协议

管哪些动作要先经用户确认，以及确认在 hook 层怎么落地。

操作规则（分档、确认清单、确认前说明）在 `~/.claude/CLAUDE.md` §1.3，本文件只放 §1.3 里读不到的机制部分。

## 落点

| 内容 | 在哪 |
|---|---|
| 分档 R0-R4、必须确认清单、确认前说明 | `~/.claude/CLAUDE.md` §1.3 |
| hook 分工、授权范围字段、授权登记命令、hook 结论、被分类器拦下的处置 | 本文件 |
| 授权范围的字段清单与匹配规则 | `~/.claude/hooks/scripts/authorization_scope.py`（唯一来源） |

字段不在本文件抄第二遍；要改字段先改脚本。

## 判据

什么进 R3/R4 以 `CLAUDE.md` §1.3 的表为准，本文件不另立一套。

## 固定字段

授权范围的 JSON 由 `authorization_scope.py` 校验，只认四个键：

| 键 | 含义 |
|---|---|
| `targets` | 目标集合（路径、仓库、容器名等） |
| `operation_family` | 操作族（删、推、迁移等） |
| `critical_params` | 关键参数 |
| `impact_ceiling` | 影响上限 |

复用已有授权时四条都要相等或更宽：`targets`、`operation_family`、`critical_params` 必须完全相同，`impact_ceiling` 必须不小于请求值，且 `task_id` 是当前有效任务。任何一条放宽都算新动作，重新进入确认线——这就是 §1.3 `子代理授权不得扩大目标、操作族、关键参数或影响上限` 的机械含义。

## 授权登记

需要精确授权的动作（远程 Git、生产或真实数据变更、独占容器）被 hook 转入确认线时，ask 消息末尾带一段 `精确授权范围：<JSON>`。用户批准后：

```
python ~/.claude/hooks/scripts/authorization_scope.py set-task --session-id <id> --task-id <本任务的固定 id>
python ~/.claude/hooks/scripts/authorization_scope.py grant --session-id <id> --task-id <同上> --scope-json '<那段 JSON 原样>'
```

`task_id` 在任务内定下后保持固定——改 id 会清空此前全部授权。

其余子命令：`revoke` 撤单条或整任务，`cleanup` 清整个会话，`match` 是只读探针，用来验某段 scope 当前是否已获授权。

## hook 分工

主模型直接识别目标、分类 R0-R4 并判断授权。Hook 只做客观资源守卫、确定性硬阻断，以及高风险状态无法确认时进入确认线；不新增第二模型、分类器或常驻服务。

Hook 结论固定为：确定硬违规或高影响动作无法安全解析时 `deny`；共享资源冲突或高风险状态无法确认时 `ask`；低风险且明确放行时无输出。

## 被 auto mode 拦下时

改 `~/.claude/CLAUDE.md`、`settings.json` 或 hook 接线时被拦下（`[Self-Modification]`、`[Security Weaken]` 一类），按下面走：

1. 读拒绝文案，区分**瞬时无法评估**与**判定性拒绝**。前者原样重试一次即过。
2. 判定性拒绝再看这次编辑是**收紧、中性还是放松**。
3. 收紧（加要求）与中性（改条件式）可再试一次；**放松类**（扩权限白名单、删禁令）交回用户，不反复试。

「别处还有同一条」在单次编辑里无法验证，不构成删禁令的理由。需在单次编辑内做等价替换时用原子替换。

## 校验

```
python ~/.claude/hooks/scripts/authorization_scope.py --help
python ~/.claude/hooks/scripts/authorization_scope.py match --session-id <id> --scope-json '<JSON>'
```

`match` 只读、不改状态；未命中即该 scope 当前无授权。

## 维护条款

**一、分界。** 落点表、字段表、子命令列表、hook 分工与结论会变，整体重写。「被 auto mode 拦下时」一节与「历史」只追加，写完不改。

**二、删除判据。** 满足其一即删：内容已在 `authorization_scope.py` 或 hook 代码里 → 删（是缓存，会过期）；被本文件后面条目覆盖 → 删旧条；只在特定情形用到 → 下沉 `references/`；指向的目标已不存在 → 删引用，或改指向。

**三、触发点。** 每次编辑本文件时顺手做一遍，不设「定期整理」。正文逼近 20 KB 强制复核，先删再加。

## 历史

- 2026-09-24 成立。`CLAUDE.md` §1.3 原有的 1,624 B 机制段（hook 分工、授权来源、授权登记命令、hook 结论、分类器自改规则）下沉到本文件，§1.3 只留一行指名指针。理由是这五条只在「接 hook」或「被 hook 求授权」时才用到，属渐进式披露里该下沉的部分。
