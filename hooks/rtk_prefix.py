#!/usr/bin/env python3
"""PreToolUse hook: auto-prefix rtk for supported commands.

Reads Codex PreToolUse JSON on stdin. If the Bash command's first word is a
supported rtk subcommand, rewrites the command with an `rtk ` prefix and
returns permissionDecision=allow + updatedInput.command. Otherwise no-op.

Codex PreToolUse only intercepts *some* shell calls, so this is best-effort,
not a complete enforcement boundary. See https://developers.openai.com/codex/hooks
"""
import json
import os
import re
import sys

RTK_SUBCOMMANDS = {
    "ls", "tree", "read", "smart", "git", "gh", "glab", "aws", "psql", "pnpm",
    "err", "test", "json", "deps", "env", "find", "diff", "log", "dotnet",
    "docker", "kubectl", "summary", "grep", "wget", "wc", "jest", "vitest",
    "prisma", "tsc", "next", "lint", "prettier", "format", "playwright",
    "cargo", "npm", "npx", "curl", "ruff", "pytest", "mypy", "rake", "rubocop",
    "rspec", "pip", "go", "gt", "golangci-lint", "gradlew", "mvn",
}


def first_word(command):
    """Return the leading executable token of a shell command string.

    Handles: leading env-var assignments (FOO=bar cmd ...), leading variable
    expansions, wrappers like `& "path\to.exe"`, and quoted executables.
    Returns None when no clear executable is found.
    """
    s = command.strip()
    if not s:
        return None
    # Skip leading VAR=value assignments (sh-style and powershell-less-common).
    while re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", s):
        s = s.split(None, 1)[1] if len(s.split(None, 1)) > 1 else ""
        s = s.strip()
        if not s:
            return None
    # PowerShell call operator: & "C:\path\to\tool.exe" args
    m = re.match(r"^&\s*['\"]?(.*?)['\"]?\s", s)
    if m:
        exe = m.group(1)
        return os.path.splitext(os.path.basename(exe.replace("/", "\\")))[0].lower()
    # Quoted executable: "tool" args  or  'tool' args
    m = re.match(r"^['\"]([^'\"]+)['\"]", s)
    if m:
        return os.path.splitext(os.path.basename(m.group(1).replace("/", "\\")))[0].lower()
    # Bare executable token.
    tok = s.split(None, 1)[0]
    # Strip any leading shell metacharacters.
    tok = tok.lstrip("(<{&|")
    return os.path.splitext(os.path.basename(tok.replace("/", "\\")))[0].lower() or None


def emit(payload):
    sys.stdout.write(json.dumps(payload))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        # Never block on malformed input.
        emit({})
        return

    tool_name = data.get("tool_name", "")
    # PreToolUse matcher is on tool_name; Bash is the canonical shell tool name.
    if tool_name not in ("Bash", "shell_command", "exec", "local_shell", "run"):
        emit({})
        return

    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        emit({})
        return
    command = tool_input.get("command", "")
    if not isinstance(command, str) or not command.strip():
        emit({})
        return

    # Already rtk-prefixed (allow rtk.exe / full paths too).
    head = command.lstrip().split(None, 1)
    if head and os.path.splitext(os.path.basename(head[0].replace("/", "\\")))[0].lower() in ("rtk",):
        emit({})
        return

    word = first_word(command)
    if not word or word not in RTK_SUBCOMMANDS:
        emit({})
        return

    # Rewrite: prepend rtk. Keep the rest of the command verbatim.
    new_command = "rtk " + command.lstrip()
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {"command": new_command},
        }
    })


if __name__ == "__main__":
    main()
