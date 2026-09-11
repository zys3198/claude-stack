#!/usr/bin/env node
/**
 * ECC Statusline — statusLine command
 *
 * Displays: model[plan] | task | $cost Nt Nf Nm | dir | branch Ctx N% | Hit N% | 5h/7d limit
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
const net = require('net');
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
  return ` \x1b[1;31m${used}%\x1b[0m \x1b[33m/compact\x1b[0m`;
}

/**
 * Color a percentage where high = bad (ctx usage, rate limits).
 * Mirrors buildContextBar thresholds.
 * @param {number} n
 * @returns {string} Colored "N%" or empty
 */
function colorPct(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return '';
  const v = Math.min(100, Math.max(0, Math.round(Number(n))));
  if (v < 50) return `\x1b[32m${v}%\x1b[0m`;
  if (v < 65) return `\x1b[33m${v}%\x1b[0m`;
  if (v < 80) return `\x1b[38;5;208m${v}%\x1b[0m`;
  return `\x1b[1;31m${v}%\x1b[0m`;
}

/**
 * Format rate-limit reset timestamp (unix seconds) as "→HH:MM" or "→Wed HH:MM".
 * @param {number|string} ts
 * @param {boolean} withDay
 * @returns {string} Dim arrow + time, or empty
 */
function fmtReset(ts, withDay) {
  if (ts === undefined || ts === null || ts === '') return '';
  const d = new Date(Number(ts) * 1000);
  if (Number.isNaN(d.getTime())) return '';
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const t = withDay
    ? `${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()]} ${hh}:${mm}`
    : `${hh}:${mm}`;
  return `\x1b[2m→${t}\x1b[0m`;
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


const MODE_STATUS = [
  {
    file: '.caveman-active',
    label: 'CAVEMAN',
    color: 172,
    valid: new Set(['', 'off', 'lite', 'full', 'ultra', 'wenyan-lite', 'wenyan', 'wenyan-full', 'wenyan-ultra', 'commit', 'review', 'compress'])
  },
  {
    file: '.ponytail-active',
    label: 'PONYTAIL',
    color: 108,
    valid: new Set(['', 'off', 'lite', 'full', 'ultra'])
  }
];

function readSmallStatusFile(filePath) {
  try {
    const stat = fs.lstatSync(filePath);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 64) return null;
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

function readModeStatus() {
  const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
  const segments = [];

  for (const config of MODE_STATUS) {
    const unknown = `\x1b[38;5;${config.color}m[${config.label}:UNKNOWN]\x1b[0m`;
    try {
      const raw = readSmallStatusFile(path.join(claudeDir, config.file));
      if (raw === null) {
        segments.push(unknown);
        continue;
      }
      const firstLine = raw.split(/\r?\n/, 1)[0].trim().toLowerCase();
      const mode = firstLine.replace(/[^a-z0-9-]/g, '');
      if (mode !== firstLine || !config.valid.has(mode)) {
        segments.push(unknown);
        continue;
      }

      const suffix = !mode ? '' : `:${mode.toUpperCase()}`;
      let rendered = `\x1b[38;5;${config.color}m[${config.label}${suffix}]\x1b[0m`;

      if (config.label === 'CAVEMAN' && process.env.CAVEMAN_STATUSLINE_SAVINGS !== '0') {
        const savings = readSmallStatusFile(path.join(claudeDir, '.caveman-statusline-suffix'))
          ?.replace(/[\x00-\x1F\x7F]/g, '')
          .trimEnd();
        if (savings) rendered += ` \x1b[38;5;${config.color}m${savings}\x1b[0m`;
      }

      segments.push(rendered);
    } catch {
      segments.push(unknown);
    }
  }

  return segments.join(' ');
}

/**
 * Headroom marker: ANTHROPIC_BASE_URL points at the local headroom proxy
 * (CC -> 8787 -> 15721). Probe the port live — env alone doesn't prove
 * the proxy process is running. Remote base URLs are not probed.
 * @returns {{host: string, port: number} | null}
 */
function localProxyTarget() {
  let u;
  try {
    u = new URL(process.env.ANTHROPIC_BASE_URL || '');
  } catch {
    return null;
  }
  if (!['127.0.0.1', 'localhost', '::1'].includes(u.hostname.toLowerCase())) return null;
  const port = Number(u.port) || (u.protocol === 'https:' ? 443 : 80);
  return { host: u.hostname, port };
}

function probeTcp(host, port, timeoutMs = 250) {
  return new Promise(resolve => {
    const socket = net.connect(port, host);
    let settled = false;
    const finish = up => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve(up);
    };
    socket.setTimeout(timeoutMs, () => finish(false));
    socket.on('connect', () => finish(true));
    socket.on('error', () => finish(false));
  });
}

function runStatusline() {
  let input = '';
  const stdinTimeout = setTimeout(() => process.exit(0), 3000);
  // Start the proxy probe in parallel with stdin read.
  const proxyTarget = localProxyTarget();
  const proxyProbe = proxyTarget ? probeTcp(proxyTarget.host, proxyTarget.port) : Promise.resolve(null);
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => {
    if (input.length < MAX_STDIN) {
      input += chunk.substring(0, MAX_STDIN - input.length);
    }
  });
  process.stdin.on('end', async () => {
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
      const usedPercentage = remaining === null || remaining === undefined
        ? cw.used_percentage
        : 100 - Number(remaining);

      const sessionId = sanitizeSessionId(session);
      const bridge = sessionId ? readBridge(sessionId) : null;

      // Write harness cost to per-session cache for cost-tracker (Stop hook).
      // cost-tracker prefers this authoritative value over its RATE_TABLE
      // estimate, which cannot price proxy-routed models (deepseek etc).
      const harnessCost = data.cost?.total_cost_usd;
      if (sessionId && harnessCost > 0) {
        try {
          fs.writeFileSync(
            path.join(os.tmpdir(), `harness-cost-${sessionId}.json`),
            JSON.stringify({ ts: Math.floor(Date.now() / 1000), cost_usd: harnessCost })
          );
        } catch {
          /* best effort */
        }
      }

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

      // Metrics from bridge; cost from live harness report, bridge as fallback
      // (gateway doesn't relay usage, so metrics-bridge cost can be 0)
      let metricsStr = '';
      const costUsd = data.cost?.total_cost_usd > 0 ? data.cost.total_cost_usd : (bridge?.total_cost_usd || 0);
      if (bridge || costUsd > 0) {
        const parts = [];
        if (costUsd > 0) {
          parts.push(`$${costUsd.toFixed(2)}`);
        }
        if (bridge) {
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
        }
        if (parts.length > 0) {
          metricsStr = `\x1b[38;5;117m${parts.join(' ')}\x1b[0m`;
        }
      }

      // Context usage (text-only, colored by level) + cache hit, | separated
      const ctx = buildContextBar(totalInputTokens, autoCompactWindow, usedPercentage);
      let hitStr = '';
      const currentUsage = cw.current_usage;
      const cacheRead = Number(currentUsage?.cache_read_input_tokens) || 0;
      const freshInput = Number(currentUsage?.input_tokens) || 0;
      const liveDenom = freshInput + cacheRead;
      if (liveDenom > 0) {
        const hitPct = Math.round((cacheRead / liveDenom) * 100);
        hitStr = `\x1b[38;5;117mHit ${hitPct}%\x1b[0m`;
      } else if (bridge) {
        const bridgeCacheRead = bridge.cache_read_tokens || 0;
        const totalIn = bridge.total_input_tokens || 0;
        if (bridgeCacheRead > 0) {
          const denom = totalIn + bridgeCacheRead;
          const hitPct = denom > 0 ? Math.round((bridgeCacheRead / denom) * 100) : 0;
          hitStr = `\x1b[38;5;117mHit ${hitPct}%\x1b[0m`;
        }
      }
      // Rate-limit usage (5h / 7d) with reset times
      const rl = data.rate_limits || {};
      const rateParts = [];
      if (rl.five_hour && rl.five_hour.used_percentage !== undefined && rl.five_hour.used_percentage !== null) {
        rateParts.push(`5h ${colorPct(rl.five_hour.used_percentage)}${fmtReset(rl.five_hour.resets_at, false)}`);
      }
      if (rl.seven_day && rl.seven_day.used_percentage !== undefined && rl.seven_day.used_percentage !== null) {
        rateParts.push(`7d ${colorPct(rl.seven_day.used_percentage)}${fmtReset(rl.seven_day.resets_at, true)}`);
      }
      const rateStr = rateParts.join(' ');

      const modeStr = readModeStatus();

      let proxyStr = '\x1b[38;5;110m[HEADROOM:UNKNOWN]\x1b[0m';
      if (proxyTarget) {
        const up = await proxyProbe;
        proxyStr = up
          ? '\x1b[38;5;110m[HEADROOM:RUNNING]\x1b[0m'
          : '\x1b[31m[HEADROOM:DOWN]\x1b[0m';
      }

      const usageStr = [ctx ? `Ctx${ctx}` : '', hitStr].filter(Boolean).join(' \x1b[2m│\x1b[0m ');

      // Build output
      const dirname = path.basename(dir);
      const effort = data.effort?.level;
      const segments = [`\x1b[2m${model}${effort ? ` [${effort}]` : ''}\x1b[0m`];

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

      process.stdout.write(
        segments.join(' \x1b[2m│\x1b[0m ') +
        (usageStr ? ` \x1b[2m│\x1b[0m ${usageStr}` : '') +
        (rateStr ? ` \x1b[2m│\x1b[0m ${rateStr}` : '') +
        (modeStr ? ` ${modeStr}` : '') +
        (proxyStr ? ` ${proxyStr}` : '')
      );
    } catch {
      // Silent fail
    }
  });
}

module.exports = { formatDuration, buildContextBar, readCurrentTask, MAX_STDIN };

if (require.main === module) runStatusline();
