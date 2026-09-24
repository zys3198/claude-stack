'use strict';

/**
 * cc-switch usage bridge.
 *
 * Resolves, for the provider cc-switch currently serves Claude Code with:
 *   - the provider identity (name, base URL, plan provider key)
 *   - the provider's coding-plan quota, queried the same way cc-switch does
 *     (see src/services/coding_plan.rs inside cc-switch.exe)
 *
 * Result is a small JSON cache that statusline.js reads on every render.
 * Refresh is triggered by a detached spawn so the statusline never blocks on
 * the network.
 */

const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { DatabaseSync } = require('node:sqlite');

const CLAUDE_DIR = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const CCSWITCH_DIR = process.env.CC_SWITCH_DIR || path.join(os.homedir(), '.cc-switch');
const CACHE_DIR = path.join(CLAUDE_DIR, 'statusline', '.cache');
const CACHE_FILE = path.join(CACHE_DIR, 'ccswitch-usage.json');

const REFRESH_TTL_MS = 60_000;
const HTTP_TIMEOUT_MS = 8000;

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

const CODEX_AUTH_FILE = path.join(CCSWITCH_DIR, 'codex_oauth_auth.json');
const CODEX_TOKEN_CACHE_FILE = path.join(CACHE_DIR, 'codex-oauth-token.json');
const CODEX_OAUTH_TOKEN_URL = 'https://auth.openai.com/oauth/token';
const CODEX_USAGE_ENDPOINT = 'https://chatgpt.com/backend-api/wham/usage';
const CODEX_CLIENT_ID = 'app_EMoamEEZ73f0CkXaXp7hrann';
const CODEX_USER_AGENT = 'cc-switch-codex-oauth';
const CODEX_TOKEN_REFRESH_BUFFER_MS = 60_000;

// ── Volcengine (Ark coding plan) ────────────────────────────
// The usage API is a control-plane OpenAPI behind the unified gateway
// open.volcengineapi.com, authenticated with Volcengine Signature V4 over the
// account AK/SK (the inference Bearer key is rejected by the gateway with
// 400 InvalidAuthorization). Transcribed from cc-switch's coding_plan.rs.

const VOLCENGINE_HOST = 'open.volcengineapi.com';
const VOLCENGINE_API_VERSION = '2024-01-01';
const VOLCENGINE_SERVICE = 'ark';
const VOLCENGINE_CONTENT_TYPE = 'application/json; charset=utf-8';
const VOLCENGINE_SIGNED_HEADERS = 'host;x-date;x-content-sha256;content-type';

function volcHmac(key, data) {
  return crypto.createHmac('sha256', key).update(data).digest();
}

function volcSha256Hex(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Region for the control-plane OpenAPI, derived from the data-plane base URL
 * host (e.g. ark.cn-beijing.volces.com -> cn-beijing).
 * @param {string} baseUrl
 * @returns {string}
 */
function volcengineRegion(baseUrl) {
  const host = (baseUrl.split('://')[1] || baseUrl).split('/')[0] || '';
  const region = host.split('.').find(p => p.startsWith('cn-') || p.startsWith('ap-'));
  return region || 'cn-beijing';
}

/**
 * Volcengine Signature V4. Differs from AWS SigV4 in: fixed SignedHeaders
 * order (not alphabetical), `HMAC-SHA256` without the AWS4 prefix, credential
 * scope ending in `request`, and kDate = HMAC(SK, date) with no AWS4 prefix.
 * @param {string} ak
 * @param {string} sk
 * @param {string} region
 * @param {string} canonicalQuery
 * @param {Date} now
 * @returns {{authorization: string, xDate: string, bodySha: string}}
 */
function volcengineSign(ak, sk, region, canonicalQuery, now) {
  const pad = n => String(n).padStart(2, '0');
  const xDate =
    `${now.getUTCFullYear()}${pad(now.getUTCMonth() + 1)}${pad(now.getUTCDate())}` +
    `T${pad(now.getUTCHours())}${pad(now.getUTCMinutes())}${pad(now.getUTCSeconds())}Z`;
  const shortDate = xDate.slice(0, 8);
  const bodySha = volcSha256Hex('');

  const canonicalHeaders =
    `host:${VOLCENGINE_HOST}\nx-date:${xDate}\nx-content-sha256:${bodySha}\ncontent-type:${VOLCENGINE_CONTENT_TYPE}\n`;
  const canonicalRequest =
    `POST\n/\n${canonicalQuery}\n${canonicalHeaders}\n${VOLCENGINE_SIGNED_HEADERS}\n${bodySha}`;

  const credentialScope = `${shortDate}/${region}/${VOLCENGINE_SERVICE}/request`;
  const stringToSign =
    `HMAC-SHA256\n${xDate}\n${credentialScope}\n${volcSha256Hex(canonicalRequest)}`;

  const kDate = volcHmac(sk, shortDate);
  const kRegion = volcHmac(kDate, region);
  const kService = volcHmac(kRegion, VOLCENGINE_SERVICE);
  const kSigning = volcHmac(kService, 'request');
  const signature = volcHmac(kSigning, stringToSign).toString('hex');

  return {
    authorization: `HMAC-SHA256 Credential=${ak}/${credentialScope}, SignedHeaders=${VOLCENGINE_SIGNED_HEADERS}, Signature=${signature}`,
    xDate,
    bodySha
  };
}

/**
 * One control-plane OpenAPI call. Business errors arrive as HTTP 200 with a
 * ResponseMetadata.Error envelope, or as 4xx with the same envelope.
 * @param {string} region
 * @param {string} ak
 * @param {string} sk
 * @param {string} action
 * @returns {Promise<object>}
 */
async function volcengineCall(region, ak, sk, action) {
  const canonicalQuery = `Action=${action}&Region=${region}&Version=${VOLCENGINE_API_VERSION}`;
  const { authorization, xDate, bodySha } = volcengineSign(ak, sk, region, canonicalQuery, new Date());
  const res = await fetch(`https://${VOLCENGINE_HOST}/?${canonicalQuery}`, {
    method: 'POST',
    headers: {
      'X-Date': xDate,
      'X-Content-Sha256': bodySha,
      'Content-Type': VOLCENGINE_CONTENT_TYPE,
      Authorization: authorization
    },
    body: '',
    signal: AbortSignal.timeout(HTTP_TIMEOUT_MS)
  });
  const body = await res.json();
  const err = body?.ResponseMetadata?.Error || body?.Error;
  if (err?.Code || err?.Message) {
    throw new Error(`${action} returned ${err.Code || res.status}: ${err.Message || ''}`.trim());
  }
  if (!res.ok) throw new Error(`${action} returned HTTP ${res.status}`);
  return body;
}

/**
 * Normalize a Volcengine usage Result into the shared window shape. Agent
 * Plan (GetAFPUsage) answers absolute Quota/Used per window; Coding Plan
 * (GetCodingPlanUsage) answers QuotaUsage[] with used percent per level.
 * @param {object} body
 * @returns {{rolling: object|null, weekly: object|null, monthly: object|null}}
 */
function parseVolcengineWindows(body) {
  const result = body?.Result || body || {};
  const windows = { rolling: null, weekly: null, monthly: null };
  let found = false;
  for (const [key, name] of [
    ['AFPFiveHour', 'rolling'],
    ['AFPWeekly', 'weekly'],
    ['AFPMonthly', 'monthly']
  ]) {
    const win = result[key];
    const quota = Number(win?.Quota);
    if (!Number.isFinite(quota) || quota <= 0) continue;
    windows[name] = {
      status: null,
      usedPct: (Number(win.Used) / quota) * 100,
      resetsAt: win.ResetTime ?? null
    };
    found = true;
  }
  if (found) return windows;

  const levels = { session: 'rolling', '5h': 'rolling', rolling: 'rolling', weekly: 'weekly', '7d': 'weekly', monthly: 'monthly' };
  const arr = result.QuotaUsage || result.Usages || result.Details || [];
  for (const item of arr) {
    const name = levels[String(item.Level ?? item.Type ?? '').toLowerCase()];
    if (!name) continue;
    windows[name] = {
      status: item.Status ?? null,
      usedPct: numberOrNull(item.Percent ?? item.UsedPercent ?? item.UsagePercent),
      resetsAt: item.ResetTimestamp ?? item.ResetTime ?? null
    };
  }
  return windows;
}

/**
 * Query the Volcengine coding-plan quota: GetAFPUsage (Agent Plan) first,
 * falling back to GetCodingPlanUsage when no AFP window is subscribed.
 * @param {{baseUrl: string, accessKeyId: string, secretAccessKey: string}} provider
 * @returns {Promise<object>}
 */
async function fetchVolcengineQuota(provider) {
  const ak = (provider.accessKeyId || '').trim();
  const sk = (provider.secretAccessKey || '').trim();
  if (!ak || !sk) {
    throw new Error('volcengine usage query needs the account AccessKey ID + Secret (not the inference API key)');
  }
  const region = volcengineRegion(provider.baseUrl);
  const errors = [];
  for (const action of ['GetAFPUsage', 'GetCodingPlanUsage']) {
    let body;
    try {
      body = await volcengineCall(region, ak, sk, action);
    } catch (err) {
      errors.push(err.message);
      continue;
    }
    const windows = parseVolcengineWindows(body);
    if (windows.rolling || windows.weekly || windows.monthly) {
      return { endpoint: `https://${VOLCENGINE_HOST}/ (Action=${action})`, auth: 'ak-sk', ...windows };
    }
    errors.push(`${action} returned no quota windows`);
  }
  throw new Error(errors.join('; '));
}

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
 * @returns {{id: string, name: string, baseUrl: string, apiKey: string, planProvider: string|null}}
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
  const baseUrl = env.ANTHROPIC_BASE_URL || '';
  const authBinding = meta.authBinding || {};
  const isCodexOAuth =
    meta.providerType === 'codex_oauth' ||
    authBinding.authProvider === 'codex_oauth' ||
    /^https:\/\/chatgpt\.com\/backend-api\/codex\/?$/i.test(baseUrl);
  return {
    id: row.id,
    name: row.name,
    baseUrl,
    apiKey: env.ANTHROPIC_API_KEY || '',
    planProvider: meta.usage_script?.codingPlanProvider || (isCodexOAuth ? 'codex_oauth' : null),
    authAccountId: authBinding.accountId || '',
    accessKeyId: meta.usage_script?.accessKeyId || '',
    secretAccessKey: meta.usage_script?.secretAccessKey || ''
  };
}

function readJsonText(text) {
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function quotaRequestOptions(apiKey, useApiKeyHeader) {
  return {
    headers: useApiKeyHeader ? { 'x-api-key': apiKey } : { Authorization: `Bearer ${apiKey}` },
    signal: AbortSignal.timeout(HTTP_TIMEOUT_MS)
  };
}

function resolveCodexAccount(provider) {
  let auth;
  try {
    auth = readJson(CODEX_AUTH_FILE);
  } catch (err) {
    throw new Error(`cannot read ${CODEX_AUTH_FILE}: ${err.message}`);
  }
  const accountId = provider.authAccountId || auth.default_account_id;
  if (!accountId) throw new Error(`${CODEX_AUTH_FILE} has no bound or default account`);
  const account = auth.accounts?.[accountId];
  if (!account) throw new Error(`${CODEX_AUTH_FILE} has no account ${accountId}`);
  if (!account.refresh_token) throw new Error(`Codex OAuth account ${accountId} has no refresh token`);
  if (!account.chatgpt_account_id) throw new Error(`Codex OAuth account ${accountId} has no ChatGPT account ID`);
  return { auth, accountId, account };
}

function readCachedCodexAccessToken(accountId) {
  try {
    const cached = readJson(CODEX_TOKEN_CACHE_FILE);
    if (
      cached.accountId === accountId &&
      typeof cached.accessToken === 'string' &&
      cached.accessToken &&
      Number(cached.expiresAtMs) > Date.now() + CODEX_TOKEN_REFRESH_BUFFER_MS
    ) {
      return cached.accessToken;
    }
  } catch {
    // Missing or corrupt token cache is refreshed below.
  }
  return null;
}

async function refreshCodexAccessToken(refreshToken) {
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: refreshToken,
    client_id: CODEX_CLIENT_ID,
    scope: 'openid profile email'
  });
  const res = await fetch(CODEX_OAUTH_TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': CODEX_USER_AGENT
    },
    body,
    signal: AbortSignal.timeout(HTTP_TIMEOUT_MS)
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`${CODEX_OAUTH_TOKEN_URL} returned HTTP ${res.status}: ${text.slice(0, 300)}`);
  const tokens = JSON.parse(text);
  if (!tokens.access_token) throw new Error('Codex OAuth refresh returned no access token');
  return tokens;
}

function persistRefreshedCodexTokens(accountId, usedRefreshToken, tokens) {
  const latest = readJson(CODEX_AUTH_FILE);
  const account = latest.accounts?.[accountId];
  if (!account) throw new Error(`Codex OAuth account ${accountId} disappeared during refresh`);
  if (account.refresh_token !== usedRefreshToken) {
    throw new Error(`Codex OAuth account ${accountId} changed during refresh; retry on next status update`);
  }
  if (tokens.refresh_token) account.refresh_token = tokens.refresh_token;
  if (tokens.id_token) account.id_token = tokens.id_token;
  account.token_updated_at_ms = Date.now();
  writeJsonAtomic(CODEX_AUTH_FILE, latest);
}

async function codexCredentials(provider, forceRefresh = false) {
  const { accountId, account } = resolveCodexAccount(provider);
  if (!forceRefresh) {
    const accessToken = readCachedCodexAccessToken(accountId);
    if (accessToken) {
      return { accountId, chatgptAccountId: account.chatgpt_account_id, accessToken };
    }
  }

  const usedRefreshToken = account.refresh_token;
  const tokens = await refreshCodexAccessToken(usedRefreshToken);
  persistRefreshedCodexTokens(accountId, usedRefreshToken, tokens);
  const expiresIn = Number(tokens.expires_in);
  const expiresAtMs = Date.now() + (Number.isFinite(expiresIn) && expiresIn > 0 ? expiresIn : 3600) * 1000;
  writeJsonAtomic(CODEX_TOKEN_CACHE_FILE, {
    accountId,
    accessToken: tokens.access_token,
    expiresAtMs
  });
  return {
    accountId,
    chatgptAccountId: account.chatgpt_account_id,
    accessToken: tokens.access_token
  };
}

async function requestCodexQuota(credentials) {
  return fetch(CODEX_USAGE_ENDPOINT, {
    headers: {
      Authorization: `Bearer ${credentials.accessToken}`,
      'ChatGPT-Account-Id': credentials.chatgptAccountId,
      'User-Agent': 'codex-cli',
      Accept: 'application/json'
    },
    signal: AbortSignal.timeout(HTTP_TIMEOUT_MS)
  });
}

async function fetchCodexQuota(provider) {
  let credentials = await codexCredentials(provider);
  let res = await requestCodexQuota(credentials);
  if (res.status === 401) {
    credentials = await codexCredentials(provider, true);
    res = await requestCodexQuota(credentials);
  }
  const body = await res.text();
  if (!res.ok) throw new Error(`${CODEX_USAGE_ENDPOINT} returned HTTP ${res.status}: ${body.slice(0, 300)}`);
  return { endpoint: CODEX_USAGE_ENDPOINT, auth: 'oauth', ...parseCodexQuota(JSON.parse(body)) };
}

/**
 * Query the provider's coding-plan quota. OpenCode Zen answers 401 for a
 * malformed Authorization header, so that one status retries with x-api-key;
 * any other failure is reported as-is.
 * @param {object} provider
 * @returns {Promise<object>}
 */
async function fetchQuota(provider) {
  if (provider.planProvider === 'volcengine') return fetchVolcengineQuota(provider);
  if (provider.planProvider === 'codex_oauth') return fetchCodexQuota(provider);

  const endpoint = QUOTA_ENDPOINTS[provider.planProvider];
  if (!endpoint) throw new Error(`no quota endpoint mapped for plan provider ${provider.planProvider}`);
  const apiKey = provider.apiKey;
  if (!apiKey) throw new Error('provider has no API key');

  let res = await fetch(endpoint, quotaRequestOptions(apiKey, false));
  let auth = 'bearer';
  if (res.status === 401) {
    res = await fetch(endpoint, quotaRequestOptions(apiKey, true));
    auth = 'x-api-key';
  }
  const body = await res.text();
  if (!res.ok) throw new Error(`${endpoint} returned HTTP ${res.status}: ${body.slice(0, 300)}`);

  return { endpoint, auth, ...parseQuota(provider.planProvider, JSON.parse(body)) };
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

function parseCodexQuota(payload) {
  const rateLimit = payload?.rate_limit;
  if (!rateLimit) {
    throw new Error(`unexpected Codex usage response shape: ${JSON.stringify(payload).slice(0, 300)}`);
  }

  const windows = { rolling: null, weekly: null, monthly: null };
  for (const [position, raw] of [
    ['primary', rateLimit.primary_window],
    ['secondary', rateLimit.secondary_window]
  ]) {
    if (!raw) continue;
    const seconds = Number(raw.limit_window_seconds);
    const name = seconds === 18_000 ? 'rolling' : seconds === 604_800 ? 'weekly' : position === 'primary' ? 'rolling' : 'weekly';
    const usedPct = numberOrNull(raw.used_percent);
    if (usedPct === null) continue;
    windows[name] = {
      status: null,
      usedPct,
      resetsAt: raw.reset_at ?? null
    };
  }
  if (!windows.rolling && !windows.weekly) {
    throw new Error(`Codex usage response has no rate-limit windows: ${JSON.stringify(payload).slice(0, 300)}`);
  }
  return windows;
}

function numberOrNull(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

/**
 * Rebuild the cache. Records `attemptedAt` first so a crash mid-flight still
 * counts as an attempt and the statusline does not respawn every render.
 * The entry is rebuilt from scratch: a quota fetched for the previous provider
 * must never outlive the provider switch that invalidated it.
 */
async function refresh() {
  const now = Math.floor(Date.now() / 1000);
  writeJsonAtomic(CACHE_FILE, { attemptedAt: now });

  const provider = readProvider(currentProviderId());

  const entry = {
    checkedAt: now,
    attemptedAt: now,
    providerId: provider.id,
    providerName: provider.name,
    baseUrl: provider.baseUrl,
    planProvider: provider.planProvider,
    quota: null,
    quotaError: null
  };

  if (provider.planProvider) {
    // A quota the bridge cannot fetch leaves the entry without one; the
    // statusline then renders no usage rather than the previous provider's.
    try {
      entry.quota = await fetchQuota(provider);
    } catch (err) {
      entry.quotaError = err.message;
    }
  }
  writeJsonAtomic(CACHE_FILE, entry);
  return entry;
}

/**
 * Whether a cache entry describes the provider cc-switch currently serves.
 * A cache whose provider cannot be read is treated as not current, so a stale
 * quota is never rendered as if it belonged to the served subscription.
 * @param {object|null} cache
 * @returns {boolean}
 */
function isCurrent(cache) {
  if (!cache?.providerId) return false;
  try {
    return cache.providerId === currentProviderId();
  } catch {
    return false;
  }
}

module.exports = { readCache, isStale, isCurrent, refresh, parseCodexQuota, CACHE_FILE, REFRESH_TTL_MS };

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
