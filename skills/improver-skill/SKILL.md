---
name: improver-skill
description: 手动驱动本地 Improver Skill：记录 Raw Trace、沉淀 Wiki Pattern、保存候选 Skill，并通过轻量 gate 控制是否应用。
---

# Improver Skill

手动触发本地 Improver Skill 闭环。只调用同目录 Python CLI，不调用 `skill-up`，不修改全局 Claude 配置。

## 引擎

```text
C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py
```

所有命令使用：

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py"
```

Workspace 使用用户指定目录，不默认写入 `C:\ZYS\Wiki`。

## 触发分流

- “记录这次执行”“保存 Trace” → `record`
- “沉淀失败经验”“整理 Pattern” → `maintain`
- “根据 Pattern 改 Skill”“提议 Skill” → `propose`
- “比较新旧 Skill”“门控”“是否应用” → `gate`
- 只说“进化一下” → 先确认目标 Skill、Workspace 和当前阶段，不直接 apply

## 操作流程

### 初始化

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
  init "<workspace>" `
  --skill-id "<skill-id>" `
  --skill-file "<seed-skill.md>" `
  --purpose "<skill-purpose>"
```

### record

需要用户提供 Trace JSON 或明确指定现有文件：

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
  record "<workspace>" `
  --input "<trace.json>" `
  --trace-id "<trace-id>" `
  --source "claude"
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
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
  maintain "<workspace>" `
  --analysis "<maintainer.json>"
```

### propose

候选 Skill 必须关联至少一个 Pattern，并提供 PURPOSE：

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
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
  "baseline": 0.50,
  "candidate": 0.62,
  "target": true,
  "guardrail": true,
  "holdout": true
}
```

先不应用：

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
  gate "<workspace>" `
  --candidate "<skill-id>/<version>" `
  --report "<report.json>"
```

只有用户明确要求应用候选 Skill，且所有 gate 通过，才追加 `--apply`：

```powershell
python312 "C:\Users\zys31\.claude\skills\improver-skill\wikiskill.py" `
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

- apply 后检查 active 内容 hash、Skill 版本、CHANGELOG 和引用文件是否一致。
- workspace active 与全局 active 分开确认；未收到明确应用授权时只保留 candidate，不覆盖全局 Skill。
- 用最小 target、guardrail、holdout smoke test 验证实际加载的 active，不以文件存在或命令返回成功代替行为验证。

## 约束

- 不自动调用模型；模型输出通过 JSON、Skill 文件或 stdin 接入。
- 不调用或修改 `skill-up`。
- 不安装 Hook，不修改 `C:\Users\zys31\.claude\settings.json`。
- 不把完整 Trace 上传外部服务。
- 不自动修改 `C:\ZYS\Wiki`。
- 不自动 commit、push、删除文件或覆盖 Raw Trace。
- 缺少 Trace、Pattern、候选 Skill 或 gate 报告时，停止并说明缺口，不猜测结果。
- gate 拒绝时保留候选、Pattern、日志和 diff；不回滚 Wiki。
