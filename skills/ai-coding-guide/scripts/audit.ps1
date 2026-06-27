# ai-coding-guide env audit: disk-scan replaces unreliable session reminders.
# Scan ~/.claude/skills, ~/.claude/plugins/cache.
# Output each ecosystem real skill/command counts and load status.
# Run when ai-coding-guide triggers.
[CmdletBinding()]
param()
$ErrorActionPreference = 'SilentlyContinue'
$claude = Join-Path $env:USERPROFILE '.claude'

function Count-Skills($path) {
    if (Test-Path $path) {
        return (Get-ChildItem $path -Directory |
            Where-Object { $_.Name -ne '.system' }).Count
    }
    return 0
}

# Claude Code plugin layouts in cache/:
#   A) <plugin>/<plugin>/<version>/{skills,commands,agents}            (ecc, ponytail, caveman, ...)
#   B) <plugin>/<leaf>/<version>/{skills,commands,agents}              (karpathy-skills/andrej-karpathy-skills/<ver>)
#   C) <umbrella>/<plugin>/<version>/{skills,commands,agents}          (claude-plugins-official/superpowers/<ver>)
#   D) <plugin>/<leaf>/<subleaf>/<version>/...                         (rare)
# Strategy: for each top-level cache dir, walk all version dirs (names look like
# semver) found at depth 2 or 3, and report their skills/commands/agents counts.

function Find-VersionDirs($pluginPath) {
    # depth 2: plugin/<leaf>/<ver>
    $v1 = Get-ChildItem $pluginPath -Directory | ForEach-Object {
        Get-ChildItem $_.FullName -Directory -ErrorAction SilentlyContinue
    }
    # depth 3: plugin/<leaf>/<subleaf>/<ver> (umbrella case: claude-plugins-official/<plugin>/<ver> already at depth 2; depth 3 catches nested)
    return $v1
}

function Get-PluginMeta($cacheDir) {
    $results = [System.Collections.Generic.List[pscustomobject]]::new()
    $umbrellas = Get-ChildItem $cacheDir -Directory
    foreach ($umbrella in $umbrellas) {
        # Each child of umbrella is either a version-parent (layout A/B) or a sibling-plugin (layout C umbrella)
        $children = Get-ChildItem $umbrella.FullName -Directory -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            # If child contains version dirs directly -> this is the plugin (layout A/B/C)
            # Version dirs are named with semver (1.0.0) OR commit hash (82f22ec4f0a7) OR "unknown"
            $vers = Get-ChildItem $child.FullName -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match '^\d+\.\d+' -or $_.Name -match '^[0-9a-f]{8,}$' -or $_.Name -eq 'unknown' }
            if (-not $vers) {
                # child may itself be a sibling-plugin container (rare); skip
                continue
            }
            foreach ($ver in $vers) {
                $skillsDir = Join-Path $ver.FullName 'skills'
                $cmdsDir    = Join-Path $ver.FullName 'commands'
                $agentsDir  = Join-Path $ver.FullName 'agents'
                $sCount = if (Test-Path $skillsDir) { (Get-ChildItem $skillsDir -Directory).Count } else { 0 }
                $cCount = if (Test-Path $cmdsDir)   { (Get-ChildItem $cmdsDir -File).Count } else { 0 }
                $aCount = if (Test-Path $agentsDir) { (Get-ChildItem $agentsDir -File).Count } else { 0 }
                $results.Add([pscustomobject]@{
                    Umbrella = $umbrella.Name
                    Plugin   = $child.Name
                    Version  = $ver.Name
                    Skills   = $sCount
                    Commands = $cCount
                    Agents   = $aCount
                })
            }
        }
    }
    return $results
}

"=== user skills dir ==="
"~/.claude/skills: $(Count-Skills (Join-Path $claude 'skills'))"

# --- plugin cache ---
""
"=== plugin cache (umbrella / plugin / version + counts) ==="
$cache = Join-Path $claude 'plugins\cache'
Get-PluginMeta $cache | Format-Table -AutoSize

# --- totals ---
""
"=== totals ==="
$meta = Get-PluginMeta $cache
"plugins discovered: $($meta.Count)"
"total skills:      $(($meta | Measure-Object -Property Skills -Sum).Sum)"
"total commands:    $(($meta | Measure-Object -Property Commands -Sum).Sum)"
"total agents:      $(($meta | Measure-Object -Property Agents -Sum).Sum)"
