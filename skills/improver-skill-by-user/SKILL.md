---
name: improver-skill-by-user
description: >-
  在用户明确要求时记录可追溯 Trace、Pattern、候选 Skill 或改进 gate 结果，并用同一条件对照和安全门禁决定是否应用候选；仅手动触发，不负责 Skill 库留删、单 Skill 审计或跨文件指令审查。
disable-model-invocation: true
---

# Improver Skill

手动触发 Skill 演进闭环。只调用 Skill 根目录中的 `wikiskill.py`；不自动调用模型或外部演进服务，只写入用户明确指定的 workspace。

## 引擎

```text
wikiskill.py 位于当前 Skill 根目录
```

以下命令以 `python` 表示宿主或用户已配置的 Python 解释器；命令在 Skill 根目录执行。

```powershell
python wikiskill.py
```

Workspace 必须由用户明确指定，不默认写入固定项目或宿主目录。

## 触发分流

- “记录这次执行”“保存 Trace” → `record`
- “沉淀失败经验”“整理 Pattern” → `maintain`
- “根据 Pattern 改 Skill”“提议 Skill” → `propose`
- “比较新旧 Skill”“门控”“是否应用” → `gate`
- 只说“进化一下” → 缺少目标 Skill、Workspace 或当前阶段时标记 `blocked`，先列出缺口；不自行猜测目标，不直接 apply

## 操作流程

### 初始化

```powershell
python wikiskill.py `
  init "<workspace>" `
  --skill-id "<skill-id>" `
  --skill-file "<seed-skill.md>" `
  --purpose "<skill-purpose>"
```

### record

需要用户提供 Trace JSON 或明确指定现有文件：

```powershell
python wikiskill.py `
  record "<workspace>" `
  --input "<trace.json>" `
  --trace-id "<trace-id>" `
  --source "<source>"
```

Raw Trace 只创建不覆盖，疑似密钥会脱敏。

### maintain

Maintainer 输入必须包含：

```json
{
  "id": "pattern-id",
  "kind": "failure",
  "title": "Pattern 标题",
  "summary": "观察到的现象",
  "root_cause": "根因",
  "recommendation": "建议动作",
  "trace_ids": ["trace-id"]
}
```

执行：

```powershell
python wikiskill.py `
  maintain "<workspace>" `
  --analysis "<maintainer.json>"
```

### propose

候选 Skill 必须关联至少一个 Pattern，并提供 PURPOSE：

```powershell
python wikiskill.py `
  propose "<workspace>" `
  --skill-id "<skill-id>" `
  --version "<version>" `
  --skill-file "<candidate.md>" `
  --purpose "<why-this-change>" `
  --pattern-id "<pattern-id>"
```

候选只写入 `skills/candidates/`，不更新 active Skill。

### gate

轻量报告格式：

```json
{
  "schema_version": 1,
  "baseline": {
    "score": 0.50,
    "status": "passed",
    "observed": "4/8 cases meet completion criteria",
    "evidence": ["run-id:baseline-001"]
  },
  "candidate": {
    "score": 0.62,
    "status": "passed",
    "observed": "5/8 cases meet completion criteria",
    "evidence": ["run-id:candidate-001"]
  },
  "target": {
    "status": "passed",
    "observed": "primary completion criterion passed",
    "evidence": ["run-id:candidate-001/target"]
  },
  "guardrail": {
    "status": "passed",
    "observed": "no protected behavior regressed",
    "evidence": ["run-id:candidate-001/guardrail"]
  },
  "holdout": {
    "status": "passed",
    "observed": "holdout criteria passed",
    "evidence": ["run-id:candidate-001/holdout"]
  },
  "comparison": {
    "same_cases": true,
    "same_model": true,
    "same_runs": true,
    "same_timeout": true,
    "same_grader": true
  }
}
```

gate 输出必须包含整体 `status` 和各检查项；`passed` 才表示可进入用户确认，`failed` 表示结果或门禁失败，`blocked` 表示缺权限/输入/用户决策，`not-run` 表示尚未运行，不得互相替代。

先不应用：

```powershell
python wikiskill.py `
  gate "<workspace>" `
  --candidate "<skill-id>/<version>" `
  --report "<report.json>"
```

只有用户明确要求应用候选 Skill，且所有 gate 通过，才追加 `--apply`：

```powershell
python wikiskill.py `
  gate "<workspace>" `
  --candidate "<skill-id>/<version>" `
  --report "<report.json>" `
  --apply
```

### 评测前置

- 先固定 `baseline`、`candidate`、`target`、`guardrail`、`holdout` 的路径、版本和内容 hash；两组必须使用同一套用例、模型、`runs`、超时和 grader。
- 优先复用 runner 能发现的 `case.yaml` 或 `prompt.md + graders/*.md`；旧格式只作原始证据保留，不把手工转换结果冒充完整套件。
- legacy `output_contains.all` 必须拆成多个 `regex` grader，保留 AND 语义；不要用更严格的 LLM criteria 替代原始规则。
- 运行时 `ERROR`、超时和环境阻塞单独记为 `not-run`，不计入模型 `FAIL`，也不填入通过 gate 所需的布尔证据。
- 评测报告必须记录实际 `runsPerCase`、用例映射和各分组分数；命令参数与报告不一致时停止 gate。

### apply 后校验

- apply 后检查 active 内容 hash、candidate metadata、impact log、Skill 版本和引用文件是否一致。
- workspace active 与全局 active 分开确认；未收到明确应用授权时只保留 candidate，不覆盖全局 Skill。
- 用最小 target、guardrail、holdout smoke test 验证实际加载的 active，不以文件存在或命令返回成功代替行为验证。

## 完成条件与停止点

每次操作先确定目标 Skill、workspace、当前阶段、完成标准和停止点；缺少必需输入、实际运行输出或用户授权时停止，不用猜测补齐。

| 阶段 | 完成证据 | 停止状态 |
|---|---|---|
| `record` | 新 Trace id、不可覆盖的文件路径、redaction 结果 | 缺输入、JSON 无效或疑似密钥 → `blocked` / `failed` |
| `maintain` | Pattern 文件、根因、建议和关联 Trace | 缺 Trace 或根因证据 → `blocked` |
| `propose` | 隔离 candidate、PURPOSE、Pattern 关联和 metadata | 缺 Pattern、候选为空或疑似密钥 → `blocked` / `failed` |
| `gate` | baseline/candidate 实际输出、同条件比较、target、guardrail、holdout 和 diff | 任何证据缺失、状态为 `blocked` / `not-run` 或 gate 未通过 → 停止，不 apply |
| `apply` | 用户明确授权、全部 gate 通过、active hash 和 impact log 已复核 | 任一条件不满足 → 保留 candidate，不改 active |

证据分三层记录：静态内容与 hash、运行输出与命令、任务结果与使用信号。文件存在、配置声明、成功加载或命令返回成功都不能替代结果证据。`passed`、`failed`、`blocked`、`not-run` 必须分别记录；未知状态不填成 `passed`。

## 约束

只有三类不可逆动作必须先确认：推生产（部署/发布/对真实用户生效）、删数据（不可恢复删除：数据库、文件、外部数据）、外发（对外发送/发布：邮件、消息、公开渠道）。密钥修改、数据库迁移、生产脚本执行并入对应三类。


- 不自动调用模型；模型输出通过 JSON、Skill 文件或 stdin 接入。
- 不调用或修改 `skill-up`。
- 不安装 Hook，不修改宿主配置或运行时设置。
- 不把完整 Trace 上传外部服务。
- 不自动修改 workspace 之外的项目、Wiki 或其他文件。
- 不自动 commit、push、删除文件或覆盖 Raw Trace。
- 缺少 Trace、Pattern、候选 Skill 或 gate 报告时，停止并说明缺口，不猜测结果。
- gate 拒绝时保留候选、Pattern、日志和 diff；不回滚 Wiki。
