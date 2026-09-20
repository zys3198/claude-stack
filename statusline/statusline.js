#!/usr/bin/env node
/**
 * ECC Statusline — statusLine command
 *
 * Displays: model[plan] | task | $cost Nt Nf Nm | dir | branch | +N *N ?N !N ↑N ↓N |
 * Ctx <used>k/<budget>k <pct> | Hit N% | plan quota
 *
 * Registered in settings.json under "statusLine", not in hooks.json.
 * Reads bridge file from ecc-metrics-bridge.js and stdin from Claude Code runtime.
 *
 * The context budget is whichever is tighter: the auto-compact window resolved
 * with Claude Code's own precedence (env > settings), or the served model's own
 * window taken from the models.dev catalog via cc-switch-usage.js. That matches
 * the window Claude Code enforces and reports in /context. cc-switch's
 * coding-plan quota is appended from the same cache, and only while that cache
 * still describes the provider cc-switch serves.
 */

'use strict';

const fs = require('fs');
const { execFileSync, spawn } = require('child_process');
const net = require('net');
const os = require('os');
const path = require('path');
const { sanitizeSessionId, readBridge, writeBridgeAtomic } = require('./lib/session-bridge');
const ccSwitchUsage = require('./cc-switch-usage');

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
 * Render tokens as a whole-k count, e.g. 77406 -> "77k", 1000000 -> "1000k".
 * @param {number} n
 * @returns {string}
 */
function formatTokens(n) {
  return `${Math.round(n / 1000)}k`;
}

/**
 * Parse a token count from a number or a settings string like "372000",
 * "372k" or "1m".
 * @param {number|string} value
 * @returns {number|null}
 */
function parseTokenCount(value) {
  if (typeof value === 'number') return Number.isFinite(value) && value > 0 ? value : null;
  const match = String(value ?? '').trim().match(/^(\d+(?:\.\d+)?)\s*([km])?$/i);
  if (!match) return null;
  const scale = { k: 1000, m: 1000000 }[match[2]?.toLowerCase()] || 1;
  const n = Number(match[1]) * scale;
  return Number.isFinite(n) && n > 0 ? n : null;
}

function isTruthyEnv(value) {
  return value !== undefined && value !== '' && value !== '0' && value.toLowerCase() !== 'false';
}

const AUTO_COMPACT_MIN = 100000;
const AUTO_COMPACT_MAX = 1000000;

/**
 * Read the auto-compact window from settings.json. Only consulted when the
 * environment variable is absent, matching Claude Code's precedence.
 * @returns {number|string|undefined}
 */
function readSettingAutoCompactWindow() {
  try {
    const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
    const settings = JSON.parse(fs.readFileSync(path.join(claudeDir, 'settings.json'), 'utf8'));
    return settings.autoCompactWindow;
  } catch {
    return undefined;
  }
}

/**
 * Resolve the auto-compact window the way Claude Code does
 * (resolveAutoCompactWindow precedence: env > settings > ...), clamped to the
 * model window. The env value is additionally bounded to [100k, 1M] and raised
 * to the 100k floor; the settings value is used as written.
 * @param {number} modelWindow - Served model's window, 0 when unresolved (no clamp)
 * @returns {number|null} Window in tokens, or null when unconfigured/disabled
 */
function resolveAutoCompactWindow(modelWindow) {
  if (isTruthyEnv(process.env.DISABLE_COMPACT) || isTruthyEnv(process.env.DISABLE_AUTO_COMPACT)) return null;

  const bound = modelWindow > 0 ? modelWindow : Infinity;

  const fromEnv = parseTokenCount(process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW);
  if (fromEnv !== null) {
    const configured = Math.max(AUTO_COMPACT_MIN, Math.min(AUTO_COMPACT_MAX, fromEnv));
    return Math.min(bound, configured);
  }

  const fromSettings = parseTokenCount(readSettingAutoCompactWindow());
  if (fromSettings !== null) return Math.min(bound, fromSettings);

  return null;
}

/**
 * Build the context segment: used tokens over the binding budget, in k, then
 * the share already consumed, colored by level. The budget is whichever is
 * tighter — the auto-compact window or the model's own window — matching the
 * window Claude Code actually enforces.
 * @param {number} usedTokens - Current context occupancy
 * @param {number} limitTokens - Binding context budget
 * @returns {string} Colored segment, or empty when data is missing
 */
function buildContextBar(usedTokens, limitTokens) {
  if (!usedTokens || !limitTokens) return '';

  const used = Math.min(100, Math.max(0, Math.round((usedTokens / limitTokens) * 100)));
  return `Ctx ${formatTokens(usedTokens)}/${formatTokens(limitTokens)} ${colorPct(used)}`;
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

/**
 * Parse porcelain-v1 status and upstream divergence.
 * @param {string} output
 * @returns {{staged: number, modified: number, untracked: number, conflicts: number, ahead: number, behind: number}}
 */
function parseGitStatus(output) {
  const result = { staged: 0, modified: 0, untracked: 0, conflicts: 0, ahead: 0, behind: 0 };
  for (const line of output.split(/\r?\n/)) {
    if (line.startsWith('## ')) {
      const ahead = line.match(/\bahead (\d+)/);
      const behind = line.match(/\bbehind (\d+)/);
      result.ahead = ahead ? Number(ahead[1]) : 0;
      result.behind = behind ? Number(behind[1]) : 0;
      continue;
    }
    if (line.length < 2) continue;

    const index = line[0];
    const worktree = line[1];
    if (index === '?' && worktree === '?') {
      result.untracked++;
    } else if (
      index === 'U' ||
      worktree === 'U' ||
      (index === 'A' && worktree === 'A') ||
      (index === 'D' && worktree === 'D')
    ) {
      result.conflicts++;
    } else {
      if (index !== ' ') result.staged++;
      if (worktree !== ' ') result.modified++;
    }
  }
  return result;
}

/**
 * Read Git status without taking optional repository locks.
 * @param {string} dir
 * @returns {ReturnType<typeof parseGitStatus> | null}
 */
function getGitStatus(dir) {
  try {
    const output = execFileSync(
      'git',
      ['--no-optional-locks', 'status', '--porcelain=v1', '--branch'],
      { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 700 }
    );
    return parseGitStatus(output);
  } catch {
    return null;
  }
}

function formatGitStatus(status) {
  if (!status) return '';
  const parts = [];
  if (status.staged) parts.push(`\x1b[32m+${status.staged}\x1b[0m`);
  if (status.modified) parts.push(`\x1b[33m*${status.modified}\x1b[0m`);
  if (status.untracked) parts.push(`\x1b[36m?${status.untracked}\x1b[0m`);
  if (status.conflicts) parts.push(`\x1b[1;31m!${status.conflicts}\x1b[0m`);
  if (status.ahead) parts.push(`\x1b[35m↑${status.ahead}\x1b[0m`);
  if (status.behind) parts.push(`\x1b[35m↓${status.behind}\x1b[0m`);
  return parts.join(' ');
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

/**
 * Kick off a detached cache refresh so no render waits on the network.
 * Only the child writes the cache; its output goes to a log file.
 */
function refreshUsageInBackground() {
  const dir = path.dirname(ccSwitchUsage.CACHE_FILE);
  fs.mkdirSync(dir, { recursive: true });
  const log = fs.openSync(path.join(dir, 'ccswitch-usage.log'), 'w');
  const child = spawn(process.execPath, [path.join(__dirname, 'cc-switch-usage.js'), '--refresh'], {
    detached: true,
    stdio: ['ignore', log, log],
    windowsHide: true
  });
  child.unref();
}

const QUOTA_LABEL = 'Usage';
const QUOTA_WINDOWS = [
  ['rolling', 'h'],
  ['weekly', 'w'],
  ['monthly', 'm']
];

/**
 * Render the active cc-switch provider's coding-plan quota, e.g.
 * "Usage h3% w16% m8%". Every window is a used percentage.
 * @param {object|null} cache - cache for the currently served cc-switch
 *   provider, or null when ownership is unproven
 * @returns {string} Colored segment, or empty when unavailable
 */
function buildQuotaSegment(cache) {
  const quota = cache?.quota;
  if (!quota) return '';

  const windows = QUOTA_WINDOWS
    .map(([key, label]) => {
      const usedPct = quota[key]?.usedPct;
      return usedPct === null || usedPct === undefined ? '' : `${label}${colorPct(usedPct)}`;
    })
    .filter(Boolean);
  if (windows.length === 0) return '';

  return `\x1b[38;5;110m${QUOTA_LABEL}\x1b[0m ${windows.join(' ')}`;
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

      // cc-switch provider identity + plan quota, refreshed by a detached child
      const usageCache = ccSwitchUsage.readCache();
      const usageIsCurrent = ccSwitchUsage.isCurrent(usageCache);
      if (!usageIsCurrent || ccSwitchUsage.isStale(usageCache)) refreshUsageInBackground();
      const cachedWindow = ccSwitchUsage.modelWindow(usageCache, model);
      const modelWindow = cachedWindow?.window || 0;
      const compactWindow = resolveAutoCompactWindow(modelWindow);
      const contextLimit = compactWindow || modelWindow;

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
      const ctx = buildContextBar(totalInputTokens, contextLimit);
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

      const usageStr = [ctx, hitStr, buildQuotaSegment(usageIsCurrent ? usageCache : null)].filter(Boolean).join(' \x1b[2m│\x1b[0m ');

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

      const gitStatusStr = formatGitStatus(getGitStatus(dir));
      if (gitStatusStr) {
        segments.push(gitStatusStr);
      }

      process.stdout.write(
        segments.join(' \x1b[2m│\x1b[0m ') +
        (usageStr ? ` \x1b[2m│\x1b[0m ${usageStr}` : '') +
        (rateStr ? ` \x1b[2m│\x1b[0m ${rateStr}` : '') +
        (modeStr ? ` ${modeStr}` : '') +
        (proxyStr ? ` ${proxyStr}` : '')
      );
    } catch (err) {
      // Silent fail in normal operation; STATUSLINE_DEBUG surfaces the cause.
      if (process.env.STATUSLINE_DEBUG) process.stderr.write(`${err.stack || err}\n`);
    }
  });
}

module.exports = {
  formatDuration,
  formatTokens,
  parseTokenCount,
  resolveAutoCompactWindow,
  buildContextBar,
  buildQuotaSegment,
  readCurrentTask,
  parseGitStatus,
  formatGitStatus,
  MAX_STDIN
};

if (require.main === module) runStatusline();
