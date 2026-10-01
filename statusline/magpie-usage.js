/**
 * Coding-plan quota, read from magpie's own quota cache.
 *
 * magpie already polls every provider on a timer and writes
 * ~/.config/magpie/quotas.json, so there is nothing left to refresh: the
 * statusline reads that file synchronously. The detached-refresh child that
 * the old cc-switch-backed reader needed went away with cc-switch.
 *
 * ponytail: no cache, no TTL, no network. When a quota stops being fresh that
 * is magpie's poller to fix, not a second implementation of it here.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');

const QUOTAS_FILE = process.env.MAGPIE_QUOTAS_FILE
  || path.join(os.homedir(), '.config', 'magpie', 'quotas.json');

// magpie names its windows; the statusline labels them by suffix.
const WINDOW_BY_NAME = new Map([
  ['5 hours', 'rolling'],
  ['7 days', 'weekly'],
  ['month', 'monthly']
]);

/**
 * Newest-quotaed entry for `provider`, or null when magpie has none.
 * Several keys can share a provider (one per account/key), so freshness
 * decides which one the statusline is talking about.
 * @param {object} quotas - parsed quotas.json
 * @param {string} provider - provider id, e.g. "opencode-go"
 * @returns {{key: string, at: string, quota: object}|null}
 */
function pickEntry(quotas, provider) {
  let best = null;
  for (const [key, entry] of Object.entries(quotas || {})) {
    const quota = entry && entry.quota;
    if (!quota || quota.provider !== provider) continue;
    if (!best || Date.parse(entry.at) > Date.parse(best.at)) best = { key, at: entry.at, quota };
  }
  return best;
}

/**
 * Quota for the provider currently serving this session.
 * @param {string} provider
 * @returns {{at: string, provider: string, quota: object}|null} null when
 *   magpie is absent, has not polled, or has no window for this provider
 */
function read(provider) {
  if (!provider) return null;
  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(QUOTAS_FILE, 'utf8'));
  } catch {
    return null;
  }
  const entry = pickEntry(parsed, provider);
  if (!entry) return null;

  const quota = {};
  for (const w of entry.quota.windows || []) {
    const key = WINDOW_BY_NAME.get(String(w.name || '').toLowerCase());
    if (key && typeof w.used === 'number') {
      quota[key] = { usedPct: w.used, resetsAt: w.resetsAt || null };
    }
  }
  return Object.keys(quota).length ? { at: entry.at, provider, quota } : null;
}

module.exports = { read, pickEntry, QUOTAS_FILE };

// Self-check: newest entry wins, foreign providers miss, missing file is null.
if (require.main === module) {
  const assert = require('assert');
  const two = {
    old: { at: '2026-10-01T10:00:00+08:00', quota: { provider: 'x', windows: [] } },
    fresh: { at: '2026-10-01T11:00:00+08:00', quota: { provider: 'x', windows: [] } }
  };
  assert.strictEqual(pickEntry(two, 'x').key, 'fresh');
  assert.strictEqual(pickEntry(two, 'y'), null);
  assert.strictEqual(read(''), null);
  const live = read('opencode-go');
  console.log(JSON.stringify(live, null, 2) || 'null');
}
