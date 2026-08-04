# Codex config 非 provider 片段合并脚本（公司电脑不用 cc-switch）
# 用法：.\setup.ps1 [-CodexHome <path>]
# 把 config.template.toml 变量回填，合并到 ~/.codex/config.toml
# 只合并 plugins/mcp/features/memories/windows/desktop 等非 provider 片段；provider/model/auth 公司电脑自配

param([string]$CodexHome = "$env:USERPROFILE\.codex")
$ErrorActionPreference = "Stop"
$templatePath = Join-Path $PSScriptRoot "config.template.toml"
$targetConfig = Join-Path $CodexHome "config.toml"
if (-not (Test-Path $templatePath)) { throw "模板不存在: $templatePath" }
$content = Get-Content $templatePath -Raw -Encoding UTF8
$replacements = @{
    '{{USERNAME}}' = $env:USERNAME
    '{{CODEX_HOME}}' = $CodexHome
    '{{PIPX_VENV_PYTHON}}' = "$env:USERPROFILE\pipx\venvs\douyin-mcp-server\Scripts\python.exe"
    '{{CODE_SPEC_PLUGIN_PATH}}' = "C:\ZYS\Code\Code-Spec-Plugin\src\cli.ts"
}
foreach ($k in $replacements.Keys) {
    $content = $content -replace [regex]::Escape($k), [System.Text.RegularExpressions.Regex]::Escape($replacements[$k])
}
if (-not (Test-Path $targetConfig)) {
    Set-Content -Path $targetConfig -Value $content -Encoding UTF8
    Write-Host "已创建 $targetConfig（注意：provider/model/auth 需自配）"
} else {
    $backup = "$targetConfig.bak.$(Get-Date -Format yyyyMMddHHmmss)"
    Copy-Item $targetConfig $backup
    Add-Content -Path $targetConfig -Value "`n# ----- 迁移合并 $(Get-Date -Format 'yyyy-MM-dd') -----" -Encoding UTF8
    Add-Content -Path $targetConfig -Value $content -Encoding UTF8
    Write-Host "已合并到 $targetConfig（备份: $backup）"
    Write-Host "注意：只合并非 provider 片段；provider/model/auth 保留公司电脑已有的。重复段手动去重。"
}
Write-Host "完成。记得复制 instructions.md 和 skills/ 到 $CodexHome\"
