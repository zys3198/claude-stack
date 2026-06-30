# ai-coding-guide env audit: disk-scan replaces unreliable session reminders.
# Scan ~/.codex/skills, ~/.agents/skills, ~/.codex/plugins/cache.
# Output each ecosystem real skill/command counts and load status.
# Run when ai-coding-guide triggers.
[CmdletBinding()]
param()
$ErrorActionPreference = 'SilentlyContinue'
$codex = Join-Path $env:USERPROFILE '.codex'
$agents = Join-Path $env:USERPROFILE '.agents'

function Count-Skills($path) {
    if (Test-Path $path) {
        return (Get-ChildItem $path -Directory |
            Where-Object { $_.Name -ne '.system' }).Count
    }
    return 0
}

function Get-PluginMeta($cacheDir) {
    $results = [System.Collections.Generic.List[pscustomobject]]::new()
    $plugins = Get-ChildItem $cacheDir -Directory
    foreach ($plug in $plugins) {
        $pjs = Get-ChildItem $plug.FullName -Recurse -Filter 'plugin.json'
        foreach ($pj in $pjs) {
            $raw = Get-Content $pj.FullName -Raw
            $hasSkills = $raw -match '"skills"'
            $hasCommands = $raw -match '"commands"'
            # plugin.json lives at <plugin>/<name>/<ver>/.codex-plugin/ (or .claude-plugin/).
            # skills/ is a sibling of the plugin.json's grandparent version dir, or of the
            # plugin.json dir itself. Walk up to find it instead of assuming one level.
            $skillsLoaded = 0
            if ($hasSkills) {
                $dir = Split-Path $pj.FullName -Parent
                foreach ($candidate in @(
                    (Join-Path $dir 'skills'),
                    (Join-Path (Split-Path $dir -Parent) 'skills'),
                    (Join-Path (Split-Path (Split-Path $dir -Parent) -Parent) 'skills')
                )) {
                    if (Test-Path $candidate) {
                        $skillsLoaded = (Get-ChildItem $candidate -Directory).Count
                        break
                    }
                }
            }
            $results.Add([pscustomobject]@{
                Plugin    = $plug.Name
                DeclCmd   = $hasCommands
                DeclSkill = $hasSkills
                SkillsDir = $skillsLoaded
            })
        }
    }
    return $results
}

"=== user skills dirs ==="
"~/.codex/skills:  $(Count-Skills (Join-Path $codex 'skills'))"
"~/.agents/skills: $(Count-Skills (Join-Path $agents 'skills'))"

# --- plugin cache ---
""
"=== plugin cache (commands declaration check) ==="
$cache = Join-Path $codex 'plugins\cache'
Get-PluginMeta $cache | Format-Table -AutoSize

# --- known-good plugin cross-check ---
""
"=== known-good plugin skill counts (cross-check) ==="
$checks = [ordered]@{
    'superpowers'       = 'openai-curated-remote\superpowers'
    'codex-security'    = 'openai-curated-remote\codex-security'
    'build-web-apps'    = 'openai-curated-remote\build-web-apps'
    'openai-developers' = 'openai-curated-remote\openai-developers'
    'github'            = 'openai-curated-remote\github'
}
foreach ($k in $checks.Keys) {
    $p = Join-Path $cache $checks[$k]
    if (Test-Path $p) {
        $ver = Get-ChildItem $p -Directory | Select-Object -First 1
        $sk = Join-Path $ver.FullName 'skills'
        $n = if (Test-Path $sk) { (Get-ChildItem $sk -Directory).Count } else { 0 }
        "{0,-20} skills={1}" -f $k, $n
    } else {
        "{0,-20} NOT FOUND" -f $k
    }
}
