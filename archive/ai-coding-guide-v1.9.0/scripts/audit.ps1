[CmdletBinding()]
param(
    [string]$Root = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrEmpty($Root)) {
    if ($PSScriptRoot) {
        $Root = (Split-Path $PSScriptRoot -Parent)
    } else {
        $scriptPath = $MyInvocation.MyCommand.Path
        if ($scriptPath) { $Root = (Split-Path $scriptPath -Parent | Split-Path -Parent) }
    }
}
if ([string]::IsNullOrEmpty($Root)) { $Root = (Get-Location).Path }

$docFiles = @(
    (Join-Path $Root 'SKILL.md'),
    (Join-Path $Root 'references\ecosystems.md'),
    (Join-Path $Root 'references\MAINTENANCE.md')
)
$jsonFile = Join-Path $Root 'test-prompts.json'

$findings = [System.Collections.Generic.List[pscustomobject]]::new()

function Add-Finding {
    param(
        [string]$Severity,
        [string]$File,
        [int]$Line,
        [string]$Message
    )
    $findings.Add([pscustomobject]@{
        Severity = $Severity
        File     = $File
        Line     = $Line
        Message  = $Message
    })
}

function Scan-Pattern {
    param(
        [string]$Path,
        [string]$Severity,
        [string]$Pattern,
        [string]$Message
    )
    $hits = Select-String -Path $Path -Pattern $Pattern -AllMatches
    foreach ($hit in $hits) {
        Add-Finding -Severity $Severity -File (Resolve-Path $Path | Split-Path -Leaf) -Line $hit.LineNumber -Message $Message
    }
}

foreach ($file in $docFiles) {
    Scan-Pattern -Path $file -Severity 'P0' -Pattern '~/.codex/|~/.cursor/|~/.windsurf/|~/.config/opencode/' -Message 'Cross-IDE path residue in Claude Code guide.'
    Scan-Pattern -Path $file -Severity 'P1' -Pattern '唯一正确|一定更好|必须如此' -Message 'Overclaim wording; downgrade to evidence-labeled recommendation.'
}

function Test-AnyFileNamed {
    param(
        [string]$RootPath,
        [string[]]$Names
    )
    if (-not (Test-Path $RootPath)) { return $false }
    foreach ($name in $Names) {
        if (Get-ChildItem -Path $RootPath -Recurse -File -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1) { return $true }
    }
    return $false
}

function Test-SkillDirExists {
    param(
        [string]$RootPath,
        [string]$SkillName
    )
    if (-not (Test-Path $RootPath)) { return $false }
    foreach ($file in (Get-ChildItem -Path $RootPath -Recurse -File -Filter 'SKILL.md' -ErrorAction SilentlyContinue)) {
        if ($file.Directory.Name -ieq $SkillName) { return $true }
    }
    return $false
}

function Test-SkillExists {
    param([string]$Name)

    $homeDir = [Environment]::GetFolderPath('UserProfile')
    $pluginCache = Join-Path $homeDir ".claude\plugins\cache"
    $parts = $Name -split ':'
    if ($parts.Count -eq 2) {
        $plugin = $parts[0]
        $skill = $parts[1]
        $directPaths = @(
            (Join-Path $homeDir ".claude\skills\$Name\SKILL.md"),
            (Join-Path $homeDir ".cc-switch\skills\$Name\SKILL.md")
        )
        foreach ($path in $directPaths) {
            if (Test-Path $path) { return $true }
        }
        if (Test-SkillDirExists -RootPath $pluginCache -SkillName $skill) { return $true }
        return (Test-AnyFileNamed -RootPath $pluginCache -Names @("$skill.md", "$skill.json", "$plugin-$skill.md", "$plugin-$skill.json"))
    } else {
        $directPaths = @(
            (Join-Path $homeDir ".claude\skills\$Name\SKILL.md"),
            (Join-Path $homeDir ".cc-switch\skills\$Name\SKILL.md")
        )
        foreach ($path in $directPaths) {
            if (Test-Path $path) { return $true }
        }
        if (Test-SkillDirExists -RootPath $pluginCache -SkillName $Name) { return $true }
        return (Test-AnyFileNamed -RootPath $pluginCache -Names @("$Name.md", "$Name.json"))
    }
}

function Test-SlashCommandExists {
    param([string]$Name)

    $homeDir = [Environment]::GetFolderPath('UserProfile')
    $patterns = @(
        (Join-Path $homeDir ".claude\commands\$Name.md"),
        (Join-Path $homeDir ".claude\plugins\cache\**\commands\$Name.md")
    )
    foreach ($pattern in $patterns) {
        if (Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1) { return $true }
    }
    return $false
}

# 死 slash 命令巡检：只扫推荐正文（SKILL.md+ecosystems.md），不扫 MAINTENANCE 变更记录；抓 backtick 包裹的 /cmd 并只报告本机缺失项
$recFiles = @(
    (Join-Path $Root 'SKILL.md'),
    (Join-Path $Root 'references\ecosystems.md')
)
$slashCmds = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($file in $recFiles) {
    if (-not (Test-Path $file)) { continue }
    $content = Get-Content $file -Raw -Encoding UTF8
    foreach ($m in [regex]::Matches($content, '`/([a-z][a-z0-9-]+)`')) {
        [void]$slashCmds.Add($m.Groups[1].Value)
    }
}
# MAINTENANCE 规则段（变更记录前）也扫死命令
$maintPath = Join-Path $Root 'references\MAINTENANCE.md'
if (Test-Path $maintPath) {
    $rulesSection = ((Get-Content $maintPath -Raw -Encoding UTF8) -split '## 变更记录')[0]
    foreach ($m in [regex]::Matches($rulesSection, '`/([a-z][a-z0-9-]+)`')) {
        [void]$slashCmds.Add($m.Groups[1].Value)
    }
}
$knownBuiltinSlash = @{'loop'=$true}
foreach ($cmd in ($slashCmds | Sort-Object)) {
    if ($knownBuiltinSlash.ContainsKey($cmd)) { continue }
    if (-not (Test-SlashCommandExists -Name $cmd)) {
        Add-Finding -Severity 'P2' -File 'SKILL.md/ecosystems.md' -Line 0 -Message "Verify slash command exists on this machine: /$cmd"
    }
}

# 死 skill 名巡检：抓 backtick 包裹的 skill 名（含 namespace），过滤常见非 skill 词，标 P2 人工核存在性
$skillNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$nonSkill = @{
    'git'=$true;'gh'=$true;'rg'=$true;'origin'=$true;'main'=$true;'master'=$true;'head'=$true;'bash'=$true
    'coach'=$true;'pair'=$true;'driver'=$true
    'brainstorming'=$true;'writing-plans'=$true;'test-driven-development'=$true;'systematic-debugging'=$true;'verification-before-completion'=$true
    'commit-push-pr'=$true
    'agent-skills:grill-me'=$true
    'security-review'=$true;'verify'=$true
}
foreach ($file in $recFiles) {
    if (-not (Test-Path $file)) { continue }
    $content = Get-Content $file -Raw -Encoding UTF8
    foreach ($m in [regex]::Matches($content, '`([a-z][a-z][a-z0-9-]+(?::[a-z][a-z0-9-]+)?)`')) {
        $name = $m.Groups[1].Value
        if ($nonSkill.ContainsKey($name)) { continue }
        [void]$skillNames.Add($name)
    }
}
foreach ($name in ($skillNames | Sort-Object)) {
    if (-not (Test-SkillExists -Name $name)) {
        Add-Finding -Severity 'P2' -File 'SKILL.md/ecosystems.md' -Line 0 -Message "Verify skill exists on this machine: $name"
    }
}

$skill = Get-Content (Join-Path $Root 'SKILL.md') -Raw -Encoding UTF8
if ($skill -notmatch 'Claude Code 当前环境') {
    Add-Finding -Severity 'P0' -File 'SKILL.md' -Line 1 -Message 'Main guide is missing Claude Code scope statement.'
}
foreach ($required in @('本地已证实', '官方可证实', '经验判断', '证据不足', 'references/ecosystems.md', 'references/MAINTENANCE.md')) {
    if ($skill -notmatch [regex]::Escape($required)) {
        Add-Finding -Severity 'P1' -File 'SKILL.md' -Line 1 -Message "Missing required string: $required"
    }
}

$maintenance = Get-Content (Join-Path $Root 'references\MAINTENANCE.md') -Raw -Encoding UTF8
foreach ($required in @('何时必须更新', '证据源', '同步文件', '变更记录')) {
    if ($maintenance -notmatch [regex]::Escape($required)) {
        Add-Finding -Severity 'P1' -File 'references/MAINTENANCE.md' -Line 1 -Message "Missing maintenance heading: $required"
    }
}

try {
    $bytes = [System.IO.File]::ReadAllBytes($jsonFile)
    $jsonText = [System.Text.Encoding]::UTF8.GetString($bytes)
    $prompts = $jsonText | ConvertFrom-Json
} catch {
    Add-Finding -Severity 'P0' -File 'test-prompts.json' -Line 1 -Message 'Invalid JSON.'
    $prompts = @()
}

if ($prompts.Count -lt 8) {
    Add-Finding -Severity 'P1' -File 'test-prompts.json' -Line 1 -Message 'Regression corpus is too small; expected at least 8 prompts.'
}

$ids = @($prompts | ForEach-Object { $_.id })
if ($ids.Count -ne (@($ids | Select-Object -Unique)).Count) {
    Add-Finding -Severity 'P0' -File 'test-prompts.json' -Line 1 -Message 'Prompt IDs must be unique.'
}

$summary = [ordered]@{
    P0 = @($findings | Where-Object Severity -eq 'P0').Count
    P1 = @($findings | Where-Object Severity -eq 'P1').Count
    P2 = @($findings | Where-Object Severity -eq 'P2').Count
}

"=== ai-coding-guide accuracy audit ==="
foreach ($severity in 'P0', 'P1', 'P2') {
    "$($severity): $($summary[$severity])"
    $group = $findings | Where-Object Severity -eq $severity
    foreach ($item in $group) {
        "  - $($item.File):$($item.Line) $($item.Message)"
    }
}

if ($summary.P0 -gt 0 -or $summary.P1 -gt 0) {
    exit 1
}
exit 0
