# 公司电脑 Codex 配置迁移（速查）

公司电脑不用 cc-switch，配置直接放 `~/.codex/` 目录。完整执行指南见 MIGRATE.md。

## 1. clone 仓库
```powershell
gh auth login  # 首次
gh repo clone zys3198/claude-stack "$env:USERPROFILE\claude-stack"
```

## 2. 放 instructions.md
```powershell
Copy-Item "$env:USERPROFILE\claude-stack\codex\instructions.md" "$env:USERPROFILE\.codex\instructions.md" -Force
```

## 3. 放 skills（只迁开发相关）
从本机 `~/.cc-switch/skills/` 挑开发相关 skill（ai-coding-guide、code-change-workflow、debugging-and-error-recovery、tdd、git-workflow-and-versioning、leader、lean-ctx、expose-unknowns、frontend-guide 等），公司电脑解压到 `~/.codex/skills/`。与开发无关的（营销/设计/内容/Office/动画/图片）不用迁。完整推荐清单见 MIGRATE.md。

## 4. 合并 config 自定义片段（非 provider）
公司电脑 config.toml 的 provider/model/auth 由 Codex app 登录自配。本模板只合并非 provider 片段：
```powershell
cd "$env:USERPROFILE\claude-stack\codex"
.\setup.ps1 -CodexHome "$env:USERPROFILE\.codex"
```

## 5. 装 MCP servers
playwright/context7（npx）、douyin（pipx）、github-mcp（环境变量）。详见 MIGRATE.md。

## 变量回填
`{{USERNAME}}` `{{CODEX_HOME}}` `{{PIPX_VENV_PYTHON}}` `{{CODE_SPEC_PLUGIN_PATH}}` 见 setup.ps1。

## 已知限制
Mac 另写；provider/model/auth 公司电脑自配（不走 cc-switch）；只迁开发相关 skill；auth 公司电脑重登 Codex app；i-have-adhd/minimalist-entrepreneur/better-harness 三个 marketplace 单独拉。
