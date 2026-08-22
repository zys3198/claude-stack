#!/usr/bin/env node
/**
 * ECC Statusline — statusLine command
 *
 * Displays: model | task | $cost Nt Nf Nm | dir | branch Ctx N% | Hit N%
 *
 * Registered in settings.json under "statusLine", not in hooks.json.
 * Reads bridge file from ecc-metrics-bridge.js and stdin from Claude Code runtime.
 *
 * Context bar: uses runtime-reported context usage percentage when available;
 * older runtimes fall back to CLAUDE_CODE_AUTO_COMPACT_WINDOW and token counts.
 * This value reflects runtime context usage, not the model's full context window.
 */

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { sanitizeSessionId, readBridge, writeBridgeAtomic } = require('./lib/session-bridge');

const MAX_STDIN = 1024 * 1024;

/**
 * Format duration from ISO timestamp to now.
 * @param {string} isoTimestamp
 * @returns {string} e.g. "5s", "12m", "1h23m"
 */
function formatDuration(isoTimestamp) {
  if (!isoTimestamp) return '?';
  const elapsed = Math.floor((Date.now() - new Date(isoTimestamp).getTime()) / 1000);
  if (elapsed < 0) return '?';
  if (elapsed < 60) return `${elapsed}s`;
  const mins = Math.floor(elapsed / 60);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  return remMins > 0 ? `${hours}h${remMins}m` : `${hours}h`;
}

/**
 * Build context progress bar with ANSI colors.
 * Runtime percentage matches Claude Code context usage; legacy fallback uses
 * CLAUDE_CODE_AUTO_COMPACT_WINDOW and token counts.
 * @param {number} totalInputTokens - Legacy input token count
 * @param {number} autoCompactWindow - Legacy compaction window in tokens
 * @param {number} usedPercentage - Runtime-reported context usage percentage
 * @returns {string} Colored bar string
 */
function buildContextBar(totalInputTokens, autoCompactWindow, usedPercentage) {
  const used = usedPercentage !== null && usedPercentage !== undefined
    ? Math.min(100, Math.max(0, Math.round(usedPercentage)))
    : totalInputTokens === null || totalInputTokens === undefined || !autoCompactWindow
      ? null
      : Math.min(100, Math.round((totalInputTokens / autoCompactWindow) * 100));

  if (used === null) return '';

  if (used < 50) return ` \x1b[32m${used}%\x1b[0m`;
  if (used < 65) return ` \x1b[33m${used}%\x1b[0m`;
  if (used < 80) return ` \x1b[38;5;208m${used}%\x1b[0m`;
  return ` \x1b[1;31m${used}%\x1b[0m`;
}

/**
 * Read current in-progress task from todos directory.
 * @param {string} sessionId
 * @returns {string} Task activeForm text or empty string
 */
function readCurrentTask(sessionId) {
  try {
    const safeSessionId = sanitizeSessionId(sessionId);
    if (!safeSessionId) return '';

    const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
    const todosDir = path.join(claudeDir, 'todos');
    if (!fs.existsSync(todosDir)) return '';

    const files = fs
      .readdirSync(todosDir)
      .filter(f => f.startsWith(safeSessionId) && f.includes('-agent-') && f.endsWith('.json'))
      .map(f => ({ name: f, mtime: fs.statSync(path.join(todosDir, f)).mtime }))
      .sort((a, b) => b.mtime - a.mtime);

    if (files.length === 0) return '';

    const todos = JSON.parse(fs.readFileSync(path.join(todosDir, files[0].name), 'utf8'));
    const inProgress = todos.find(t => t.status === 'in_progress');
    return inProgress?.activeForm || '';
  } catch {
    return '';
  }
}

/**
 * Detect git branch by walking up from dir looking for .git.
 * Reads .git/HEAD directly (no git subprocess). Handles worktrees
 * where .git is a file pointing to the real gitdir.
 * @param {string} dir
 * @returns {string} Branch name, short commit hash (detached), or empty
 */
function getGitBranch(dir) {
  try {
    let current = dir;
    for (let i = 0; i < 20; i++) {
      const gitPath = path.join(current, '.git');
      if (fs.existsSync(gitPath)) {
        let headPath;
        if (fs.statSync(gitPath).isDirectory()) {
          headPath = path.join(gitPath, 'HEAD');
        } else {
          // .git is a file -> worktree/submodule: "gitdir: <path>"
          const content = fs.readFileSync(gitPath, 'utf8').trim();
          const match = content.match(/^gitdir:\s*(.+)$/);
          if (!match) return '';
          let gitdir = match[1];
          if (!path.isAbsolute(gitdir)) gitdir = path.join(current, gitdir);
          headPath = path.join(gitdir, 'HEAD');
        }
        if (!fs.existsSync(headPath)) return '';
        const head = fs.readFileSync(headPath, 'utf8').trim();
        const refMatch = head.match(/^ref:\s*refs\/heads\/(.+)$/);
        if (refMatch) return refMatch[1];
        // Detached HEAD: short hash
        return head.substring(0, 7);
      }
      const parent = path.dirname(current);
      if (parent === current) break;
      current = parent;
    }
    return '';
  } catch {
    return '';
  }
}

function resolveModelName(modelInfo) {
  const displayName = modelInfo?.display_name || 'Claude';
  const modelName = displayName.toLowerCase();

  // cc-switch 路由：显示当前模型槽实际指向的下游模型名（_MODEL_NAME），而非 Claude 槽名
  if (modelName.includes('sonnet')) return process.env.ANTHROPIC_DEFAULT_SONNET_MODEL_NAME || displayName;
  if (modelName.includes('opus')) return process.env.ANTHROPIC_DEFAULT_OPUS_MODEL_NAME || displayName;
  if (modelName.includes('haiku')) return process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME || displayName;
  if (modelName.includes('fable') || modelName.includes('mythos')) return process.env.ANTHROPIC_DEFAULT_FABLE_MODEL_NAME || displayName;

  return displayName;
}

function runStatusline() {
  let input = '';
  const stdinTimeout = setTimeout(() => process.exit(0), 3000);
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => {
    if (input.length < MAX_STDIN) {
      input += chunk.substring(0, MAX_STDIN - input.length);
    }
  });
  process.stdin.on('end', () => {
    clearTimeout(stdinTimeout);
    try {
      const data = JSON.parse(input);
      const model = resolveModelName(data.model);
      const dir = data.workspace?.current_dir || process.cwd();
      const session = data.session_id || '';
      const cw = data.context_window || {};
      const remaining = cw.remaining_percentage;
      const totalInputTokens = cw.total_input_tokens;
      // Compaction point = AUTO_COMPACT_WINDOW env; fall back to reported window size
      const autoCompactWindow = Number(process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW) || cw.context_window_size || 0;
      const usedPercentage = cw.used_percentage ?? (remaining === null || remaining === undefined ? null : 100 - remaining);

      const sessionId = sanitizeSessionId(session);
      const bridge = sessionId ? readBridge(sessionId) : null;

      // Write context % back to bridge for context-monitor
      if (sessionId && bridge && remaining !== null && remaining !== undefined) {
        bridge.context_remaining_pct = remaining;
        try {
          writeBridgeAtomic(sessionId, bridge);
        } catch {
          /* best effort */
        }
      }

      // Current task
      const task = sessionId ? readCurrentTask(sessionId) : '';

      // Metrics from bridge
      let metricsStr = '';
      if (bridge) {
        const parts = [];
        if (bridge.total_cost_usd > 0) {
          parts.push(`$${bridge.total_cost_usd.toFixed(2)}`);
        }
        if (bridge.tool_count > 0) {
          parts.push(`${bridge.tool_count}t`);
        }
        if (bridge.files_modified_count > 0) {
          parts.push(`${bridge.files_modified_count}f`);
        }
        const dur = formatDuration(bridge.first_timestamp);
        if (dur !== '?') {
          parts.push(dur);
        }
        if (parts.length > 0) {
          metricsStr = `\x1b[38;5;117m${parts.join(' ')}\x1b[0m`;
        }
      }

      // Context usage (text-only, colored by level) + cache hit, | separated
      const ctx = buildContextBar(totalInputTokens, autoCompactWindow, usedPercentage);
      let hitStr = '';
      if (bridge) {
        const cacheRead = bridge.cache_read_tokens || 0;
        const cacheWrite = bridge.cache_write_tokens || 0;
        const totalIn = bridge.total_input_tokens || 0;
        if (cacheRead > 0) {
          // input_tokens 已含 cache 部分(Anthropic 语义)时分母=in;
          // 否则(proxy fresh-only 语义)分母=in+cr+cw,当前者成立时 in 已经盖住 cache,再加会双重计数
          const denom = totalIn >= cacheRead + cacheWrite ? totalIn : totalIn + cacheRead + cacheWrite;
          const hitPct = denom > 0 ? Math.round((cacheRead / denom) * 100) : 0;
          hitStr = `\x1b[38;5;117mHit ${hitPct}%\x1b[0m`;
        }
      }
      const usageStr = [ctx ? `Ctx${ctx}` : '', hitStr].filter(Boolean).join(' \x1b[2m\u2502\x1b[0m ');

      // Build output
      const dirname = path.basename(dir);
      const segments = [`\x1b[2m${model}\x1b[0m`];

      if (task) {
        segments.push(`\x1b[1;97m${task}\x1b[0m`);
      }
      if (metricsStr) {
        segments.push(metricsStr);
      }
      segments.push(`\x1b[2m${dirname}\x1b[0m`);

      const branch = getGitBranch(dir);
      if (branch) {
        segments.push(`\x1b[33m${branch}\x1b[0m`);
      }

      process.stdout.write(segments.join(' \x1b[2m\u2502\x1b[0m ') + (usageStr ? ` \x1b[2m\u2502\x1b[0m ${usageStr}` : ''));
    } catch {
      // Silent fail
    }
  });
}

module.exports = { formatDuration, buildContextBar, readCurrentTask, MAX_STDIN };

if (require.main === module) runStatusline();
