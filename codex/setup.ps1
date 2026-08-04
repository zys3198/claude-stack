# Codex config 模板变量回填 + 合并脚本
# 用法：.\setup.ps1 [-CodexHome <path>]
# 把 config.template.toml 变量回填，合并到 ~/.codex/config.toml
# 不覆盖 marketplaces/notify/runtime/hooks.state/projects 字段（这些由 Codex app 自管）

param(
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"
$templatePath = Join-Path $PSScriptRoot "config.template.toml"
$targetConfig = Join-Path $CodexHome "config.toml"

if (-not (Test-Path $templatePath)) { throw "模板不存在: $templatePath" }

# 变量回填
$content = Get-Content $templatePath -Raw -Encoding UTF8
$replacements = @{
    '{{USERNAME}}'              = $env:USERNAME
    '{{CODEX_HOME}}'            = $CodexHome
    '{{PROXY_BASE_URL}}'        = 'http://127.0.0.1:15721/v1'
    '{{OPENAI_BASE_URL}}'       = 'http://127.0.0.1:4444/v1'
    '{{PIPX_VENV_PYTHON}}'      = "$env:USERPROFILE\pipx\venvs\douyin-mcp-server\Scripts\python.exe"
    '{{CODE_SPEC_PLUGIN_PATH}}' = "C:\ZYS\Code\Code-Spec-Plugin\src\cli.ts"
}
foreach ($k in $replacements.Keys) {
    $content = $content -replace [regex]::Escape($k), [System.Text.RegularExpressions.Regex]::Escape($replacements[$k])
}

# 合并策略：目标不存在直接写；存在则备份后追加（用户手动去重 marketplaces 等重复段）
if (-not (Test-Path $targetConfig)) {
    Set-Content -Path $targetConfig -Value $content -Encoding UTF8
    Write-Host "已创建 $targetConfig"
} else {
    $backup = "$targetConfig.bak.$(Get-Date -Format yyyyMMddHHmmss)"
    Copy-Item $targetConfig $backup
    Add-Content -Path $targetConfig -Value "`n# ----- 迁移合并 $(Get-Date -Format 'yyyy-MM-dd') -----" -Encoding UTF8
    Add-Content -Path $targetConfig -Value $content -Encoding UTF8
    Write-Host "已合并到 $targetConfig（备份: $backup）"
    Write-Host "注意：marketplaces/notify/runtime/hooks.state/projects 段可能重复，手动保留 app 生成的那份，删迁移进来的重复段。"
}

Write-Host "完成。记得复制 instructions.md 到 $CodexHome\"
