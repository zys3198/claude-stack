# Read stdin as raw UTF-8 bytes: under hook runner (Git Bash → powershell.exe 5.1),
# [Console]::In defaults to the system ANSI codepage (GBK) and corrupts Chinese payload.
$stdin = [Console]::OpenStandardInput()
$ms = New-Object System.IO.MemoryStream
$stdin.CopyTo($ms)
$raw = [System.Text.Encoding]::UTF8.GetString($ms.ToArray())
$ms.Dispose(); $stdin.Dispose()
try {
    $event = $raw | ConvertFrom-Json
} catch {
    exit 0
}

function Text([int[]]$codes) {
    $chars = $codes | ForEach-Object { [char]$_ }
    return -join $chars
}

$body = switch ([string]$event.hook_event_name) {
    'Notification' {
        switch ([string]$event.notification_type) {
            'permission_prompt' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x6B63,0x5728,0x7B49,0x5F85,0x4F60,0x7684,0x786E,0x8BA4) }
            'idle_prompt' { exit 0 }
            'elicitation_dialog' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x9700,0x8981,0x4F60,0x63D0,0x4F9B,0x66F4,0x591A,0x4FE1,0x606F) }
            'agent_needs_input' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x73B0,0x5728,0x9700,0x8981,0x4F60,0x7684,0x56DE,0x590D) }
            default { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x9700,0x8981,0x4F60,0x5904,0x7406) }
        }
    }
    'StopFailure' {
        switch ([string]$event.error) {
            'server_error' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x9047,0x5230,0x4E86,0x7F51,0x7EDC,0x6216,0x670D,0x52A1,0x95EE,0x9898) }
            'authentication_failed' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x8EAB,0x4EFD,0x9A8C,0x8BC1,0x5931,0x8D25) }
            'billing_error' { exit 0 }
            'rate_limit' { exit 0 }
            'cloud_credential_error' { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x7684,0x4E91,0x670D,0x52A1,0x51ED,0x636E,0x51FA,0x73B0,0x95EE,0x9898) }
            default { Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x9047,0x5230,0x672A,0x77E5,0x95EE,0x9898,0xFF0C,0x672A,0x80FD,0x5B8C,0x6210,0x56DE,0x590D) }
        }
    }
    'Stop' {
        Text @(0x43,0x6C,0x61,0x75,0x64,0x65,0x20,0x5DF2,0x56DE,0x590D,0xFF0C,0x7B49,0x5F85,0x4F60,0x7EE7,0x7EED)
    }
    default {
        exit 0
    }
}

$isVsCode =
    -not [string]::IsNullOrWhiteSpace($env:VSCODE_PID) -or
    $env:TERM_PROGRAM -eq 'vscode' -or
    -not [string]::IsNullOrWhiteSpace($env:VSCODE_INJECTION)
if ($isVsCode) {
    $title = 'VS Code'
    $appId = 'Microsoft.VisualStudioCode'
} else {
    $title = 'Windows Terminal'
    $appId = 'Microsoft.WindowsTerminal_8wekyb3d8bbwe!App'
}

function Escape-Xml([string]$value) {
    return [System.Security.SecurityElement]::Escape($value)
}

try {
    $xmlText = "<toast activationType='protocol' launch='claude-notify://dismiss'><visual><binding template='ToastGeneric'><text>$(Escape-Xml $title)</text><text>$(Escape-Xml $body)</text></binding></visual></toast>"
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($xmlText)
    $toast = New-Object Windows.UI.Notifications.ToastNotification -ArgumentList $xml
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId)
    $notifier.Show($toast)
} catch {
    exit 0
}
