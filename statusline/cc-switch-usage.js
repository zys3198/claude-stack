'use strict';

/**
 * cc-switch usage bridge.
 *
 * Resolves, for the provider cc-switch currently serves Claude Code with:
 *   - the provider identity (name, base URL, plan provider key)
 *   - the real context window of the served model, from the models.dev catalog
 *   - the provider's coding-plan quota, queried the same way cc-switch does
 *     (see src/services/coding_plan.rs inside cc-switch.exe)
 *
 * Result is a small JSON cache that statusline.js reads on every render.
 * Refresh is triggered by a detached spawn so the statusline never blocks on
 * the network.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { DatabaseSync } = require('node:sqlite');

const CLAUDE_DIR = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const CCSWITCH_DIR = process.env.CC_SWITCH_DIR || path.join(os.homedir(), '.cc-switch');
const CACHE_DIR = path.join(CLAUDE_DIR, 'statusline', '.cache');
const CACHE_FILE = path.join(CACHE_DIR, 'ccswitch-usage.json');
const CATALOG_FILE = path.join(CACHE_DIR, 'models.dev.json');

const REFRESH_TTL_MS = 60_000;
const CATALOG_TTL_MS = 7 * 24 * 3600_000;
const HTTP_TIMEOUT_MS = 8000;
const CATALOG_URL = 'https://models.dev/api.json';

/**
 * Coding-plan quota endpoints, transcribed from cc-switch's coding_plan.rs.
 * @type {Record<string, string>}
 */
const QUOTA_ENDPOINTS = {
  opencode_go: 'https://opencode.ai/zen/go/v1/usage',
  kimi: 'https://api.kimi.com/coding/v1/usages',
  zhipu_glm: 'https://open.bigmodel.cn/api/monitor/usage/quota/limit',
  minimax: 'https://api.minimax.io/v1/api/openplatform/coding_plan/remains'
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeJsonAtomic(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value), 'utf8');
  fs.renameSync(tmp, file);
}

/**
 * @returns {object|null} Cached usage payload, or null when absent/corrupt.
 */
function readCache() {
  try {
    return readJson(CACHE_FILE);
  } catch {
    return null;
  }
}

/**
 * Timestamp of the last refresh attempt (successful or not), used as backoff.
 * @param {object|null} cache
 * @returns {number}
 */
function cacheAgeMs(cache) {
  if (!cache) return Infinity;
  const at = cache.attemptedAt || cache.checkedAt || 0;
  return Date.now() - at * 1000;
}

function isStale(cache) {
  return cacheAgeMs(cache) >= REFRESH_TTL_MS;
}

/**
 * Read the active Claude provider id from cc-switch's settings file, falling
 * back to the is_current flag in the database.
 * @returns {string}
 */
function currentProviderId() {
  const fromSettings = readJson(path.join(CCSWITCH_DIR, 'settings.json')).currentProviderClaude;
  if (fromSettings) return fromSettings;

  const db = new DatabaseSync(path.join(CCSWITCH_DIR, 'cc-switch.db'), { readOnly: true });
  try {
    const row = db.prepare("SELECT id FROM providers WHERE app_type = 'claude' AND is_current = 1").get();
    if (!row) throw new Error('cc-switch has no current claude provider');
    return row.id;
  } finally {
    db.close();
  }
}

/**
 * @param {string} providerId
 * @returns {{id: string, name: string, baseUrl: string, apiKey: string, model: string, planProvider: string|null}}
 */
function readProvider(providerId) {
  const db = new DatabaseSync(path.join(CCSWITCH_DIR, 'cc-switch.db'), { readOnly: true });
  let row;
  try {
    row = db
      .prepare('SELECT id, name, settings_config, meta FROM providers WHERE app_type = ? AND id = ?')
      .get('claude', providerId);
  } finally {
    db.close();
  }
  if (!row) throw new Error(`cc-switch provider not found: ${providerId}`);

  const env = readJsonText(row.settings_config).env || {};
  const meta = readJsonText(row.meta);
  return {
    id: row.id,
    name: row.name,
    baseUrl: env.ANTHROPIC_BASE_URL || '',
    apiKey: env.ANTHROPIC_API_KEY || '',
    model: env.ANTHROPIC_MODEL || env.ANTHROPIC_DEFAULT_OPUS_MODEL_NAME || '',
    planProvider: meta.usage_script?.codingPlanProvider || null
  };
}

function readJsonText(text) {
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

/**
 * Load the models.dev catalog, refreshing the local snapshot when it expires.
 * Snapshot shape: { [providerId]: { api, models: { [modelId]: contextTokens } } }
 * @returns {object}
 */
async function loadCatalog() {
  const cached = (() => {
    try {
      const snapshot = readJson(CATALOG_FILE);
      return Date.now() - snapshot.fetchedAt * 1000 < CATALOG_TTL_MS ? snapshot.catalog : null;
    } catch {
      return null;
    }
  })();
  if (cached) return cached;

  const res = await fetch(CATALOG_URL, { signal: AbortSignal.timeout(HTTP_TIMEOUT_MS) });
  if (!res.ok) throw new Error(`models.dev returned HTTP ${res.status}`);
  const raw = await res.json();

  const catalog = {};
  for (const [providerId, provider] of Object.entries(raw)) {
    const models = {};
    for (const [modelId, model] of Object.entries(provider.models || {})) {
      if (model.limit?.context) models[modelId] = model.limit.context;
    }
    catalog[providerId] = { api: provider.api || '', models };
  }
  writeJsonAtomic(CATALOG_FILE, { fetchedAt: Math.floor(Date.now() / 1000), catalog });
  return catalog;
}

/**
 * Match a cc-switch provider to its models.dev entry. The base URL is the
 * strongest signal; the plan-provider key is the fallback.
 * @param {{baseUrl: string, planProvider: string|null}} provider
 * @param {object} catalog
 * @returns {{id: string, models: object}|null}
 */
function matchCatalogProvider(provider, catalog) {
  const strip = url => url.replace(/\/+$/, '').toLowerCase();
  const base = strip(provider.baseUrl);
  if (base) {
    for (const [id, entry] of Object.entries(catalog)) {
      const api = strip(entry.api);
      if (api && (api === base || api.startsWith(`${base}/`) || base.startsWith(`${api}/`))) {
        return { id, models: entry.models };
      }
    }
  }
  const key = provider.planProvider?.replace(/_/g, '-');
  if (key && catalog[key]) return { id: key, models: catalog[key].models };
  return null;
}

function quotaRequestOptions(apiKey, useApiKeyHeader) {
  return {
    headers: useApiKeyHeader ? { 'x-api-key': apiKey } : { Authorization: `Bearer ${apiKey}` },
    signal: AbortSignal.timeout(HTTP_TIMEOUT_MS)
  };
}

/**
 * Query the provider's coding-plan quota. OpenCode Zen answers 401 for a
 * malformed Authorization header, so that one status retries with x-api-key;
 * any other failure is reported as-is.
 * @param {string} planProvider
 * @param {string} apiKey
 * @returns {Promise<object>}
 */
async function fetchQuota(planProvider, apiKey) {
  const endpoint = QUOTA_ENDPOINTS[planProvider];
  if (!endpoint) throw new Error(`no quota endpoint mapped for plan provider ${planProvider}`);
  if (!apiKey) throw new Error('provider has no API key');

  let res = await fetch(endpoint, quotaRequestOptions(apiKey, false));
  let auth = 'bearer';
  if (res.status === 401) {
    res = await fetch(endpoint, quotaRequestOptions(apiKey, true));
    auth = 'x-api-key';
  }
  const body = await res.text();
  if (!res.ok) throw new Error(`${endpoint} returned HTTP ${res.status}: ${body.slice(0, 300)}`);

  return { endpoint, auth, ...parseQuota(planProvider, JSON.parse(body)) };
}

/**
 * OpenCode Zen answers with used-percent windows:
 * { usage: { rolling|weekly|monthly: { status, percent, resetsAt } } }
 * @param {string} planProvider
 * @param {object} payload
 * @returns {object}
 */
function parseQuota(planProvider, payload) {
  if (planProvider !== 'opencode_go') {
    throw new Error(`no response parser mapped for plan provider ${planProvider}`);
  }
  if (!payload.usage) {
    throw new Error(`unexpected usage response shape: ${JSON.stringify(payload).slice(0, 300)}`);
  }
  const window = key => {
    const raw = payload.usage[key];
    if (!raw) return null;
    return {
      status: raw.status ?? null,
      usedPct: numberOrNull(raw.percent),
      resetsAt: raw.resetsAt ?? null
    };
  };
  return { rolling: window('rolling'), weekly: window('weekly'), monthly: window('monthly') };
}

function numberOrNull(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

/**
 * Rebuild the cache. Records `attemptedAt` first so a crash mid-flight still
 * counts as an attempt and the statusline does not respawn every render.
 */
async function refresh() {
  const previous = readCache();
  writeJsonAtomic(CACHE_FILE, { ...previous, attemptedAt: Math.floor(Date.now() / 1000) });

  const provider = readProvider(currentProviderId());
  const catalog = await loadCatalog();
  const matched = matchCatalogProvider(provider, catalog);

  const entry = {
    ...previous,
    checkedAt: Math.floor(Date.now() / 1000),
    attemptedAt: Math.floor(Date.now() / 1000),
    providerId: provider.id,
    providerName: provider.name,
    baseUrl: provider.baseUrl,
    planProvider: provider.planProvider,
    model: provider.model,
    modelWindowSource: matched ? `models.dev:${matched.id}` : null,
    modelWindows: matched ? matched.models : {}
  };

  if (provider.planProvider) {
    entry.quota = await fetchQuota(provider.planProvider, provider.apiKey);
  }
  writeJsonAtomic(CACHE_FILE, entry);
  return entry;
}

/**
 * Resolve the context window advertised for a served model.
 * @param {object|null} cache
 * @param {string} model
 * @returns {{window: number, source: string}|null}
 */
function modelWindow(cache, model) {
  const window = cache?.modelWindows?.[model];
  return window ? { window, source: cache.modelWindowSource } : null;
}

module.exports = { readCache, isStale, modelWindow, refresh, CACHE_FILE, REFRESH_TTL_MS };

if (require.main === module) {
  refresh()
    .then(entry => {
      if (process.argv.includes('--print')) process.stdout.write(`${JSON.stringify(entry, null, 2)}\n`);
    })
    .catch(err => {
      process.stderr.write(`${err.stack || err}\n`);
      process.exitCode = 1;
    });
}
