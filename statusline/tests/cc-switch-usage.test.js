'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { DatabaseSync } = require('node:sqlite');

const STATUSLINE_DIR = path.join(__dirname, '..');
const BRIDGE = path.join(STATUSLINE_DIR, 'cc-switch-usage.js');
const STATUSLINE = path.join(STATUSLINE_DIR, 'statusline.js');

const PROVIDERS = {
  opencode: {
    id: 'oc-1',
    name: 'OpenCode Go',
    baseUrl: 'https://opencode.ai/zen/go',
    apiFormat: 'anthropic',
    meta: { usage_script: { codingPlanProvider: 'opencode_go' } }
  },
  volcengine: {
    id: 'volc-1',
    name: '火山 Coding Plan',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/coding',
    apiFormat: 'anthropic',
    meta: { usage_script: { codingPlanProvider: 'volcengine' } }
  },
  codex: {
    id: 'codex-1',
    name: 'Codex-公司账号',
    baseUrl: 'https://chatgpt.com/backend-api/codex',
    apiFormat: 'openai_responses',
    meta: {}
  }
};

const QUOTA_OF_PREVIOUS_PROVIDER = {
  endpoint: 'https://opencode.ai/zen/go/v1/usage',
  auth: 'bearer',
  rolling: { status: 'ok', usedPct: 1, resetsAt: null },
  weekly: { status: 'ok', usedPct: 48, resetsAt: null },
  monthly: { status: 'ok', usedPct: 24, resetsAt: null }
};

/**
 * cc-switch state plus a statusline cache seeded with the previous provider's
 * quota, i.e. the state a provider switch leaves behind.
 */
function makeSandbox(currentProvider, seededCache) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ccswitch-usage-'));
  const claudeDir = path.join(root, 'claude');
  const cacheDir = path.join(claudeDir, 'statusline', '.cache');
  fs.mkdirSync(cacheDir, { recursive: true });

  fs.writeFileSync(
    path.join(root, 'settings.json'),
    JSON.stringify({ currentProviderClaude: currentProvider.id }),
    'utf8'
  );

  const db = new DatabaseSync(path.join(root, 'cc-switch.db'));
  db.exec('CREATE TABLE providers (id TEXT, app_type TEXT, name TEXT, settings_config TEXT, meta TEXT)');
  const insert = db.prepare('INSERT INTO providers VALUES (?, ?, ?, ?, ?)');
  for (const provider of Object.values(PROVIDERS)) {
    insert.run(
      provider.id,
      'claude',
      provider.name,
      JSON.stringify({ env: { ANTHROPIC_BASE_URL: provider.baseUrl, ANTHROPIC_API_KEY: 'test-key', ANTHROPIC_MODEL: 'test-model' } }),
      JSON.stringify(provider.meta)
    );
  }
  db.close();

  // Catalog snapshot pinned here so the test never reaches models.dev.
  fs.writeFileSync(
    path.join(cacheDir, 'models.dev.json'),
    JSON.stringify({ fetchedAt: Math.floor(Date.now() / 1000), catalog: {} }),
    'utf8'
  );
  fs.writeFileSync(path.join(cacheDir, 'ccswitch-usage.json'), JSON.stringify(seededCache), 'utf8');

  return {
    root,
    env: {
      ...process.env,
      CC_SWITCH_DIR: root,
      CLAUDE_CONFIG_DIR: claudeDir
    },
    readCache() {
      return JSON.parse(fs.readFileSync(path.join(cacheDir, 'ccswitch-usage.json'), 'utf8'));
    },
    cleanup() {
      fs.rmSync(root, { recursive: true, force: true });
    }
  };
}

function seededFromOpencode() {
  return {
    attemptedAt: Math.floor(Date.now() / 1000),
    checkedAt: Math.floor(Date.now() / 1000),
    providerId: PROVIDERS.opencode.id,
    providerName: PROVIDERS.opencode.name,
    baseUrl: PROVIDERS.opencode.baseUrl,
    planProvider: 'opencode_go',
    model: 'deepseek-v4.1-flash',
    modelWindowSource: null,
    modelWindows: {},
    quota: QUOTA_OF_PREVIOUS_PROVIDER
  };
}

test('refresh keeps the served identity and drops the previous provider quota', () => {
  const sandbox = makeSandbox(PROVIDERS.volcengine, seededFromOpencode());
  try {
    const result = spawnSync(process.execPath, [BRIDGE], { env: sandbox.env, encoding: 'utf8' });
    assert.strictEqual(result.status, 0, result.stderr);

    const cache = sandbox.readCache();
    assert.strictEqual(cache.providerId, PROVIDERS.volcengine.id);
    assert.strictEqual(cache.providerName, '火山 Coding Plan');
    assert.strictEqual(cache.quota, null);
    assert.match(cache.quotaError, /no quota endpoint mapped for plan provider volcengine/);
  } finally {
    sandbox.cleanup();
  }
});

test('refresh drops the previous provider quota when the provider has no usage script', () => {
  const sandbox = makeSandbox(PROVIDERS.codex, seededFromOpencode());
  try {
    const result = spawnSync(process.execPath, [BRIDGE], { env: sandbox.env, encoding: 'utf8' });
    assert.strictEqual(result.status, 0, result.stderr);

    const cache = sandbox.readCache();
    assert.strictEqual(cache.providerId, PROVIDERS.codex.id);
    assert.strictEqual(cache.quota, null);
    assert.strictEqual(cache.quotaError, null);
  } finally {
    sandbox.cleanup();
  }
});

function renderStatusline(env) {
  const payload = {
    model: { display_name: 'Opus 5' },
    workspace: { current_dir: STATUSLINE_DIR },
    session_id: 'ccswitch-usage-test',
    context_window: { remaining_percentage: 90, total_input_tokens: 1000 }
  };
  const result = spawnSync(process.execPath, [STATUSLINE], {
    env,
    input: JSON.stringify(payload),
    encoding: 'utf8'
  });
  assert.strictEqual(result.status, 0, result.stderr);
  return result.stdout;
}

test('statusline renders the quota of the served provider', () => {
  const sandbox = makeSandbox(PROVIDERS.opencode, seededFromOpencode());
  try {
    assert.match(renderStatusline(sandbox.env), /Usage/);
  } finally {
    sandbox.cleanup();
  }
});

test('statusline hides the quota once the cache belongs to another provider', () => {
  const sandbox = makeSandbox(PROVIDERS.volcengine, seededFromOpencode());
  try {
    assert.doesNotMatch(renderStatusline(sandbox.env), /Usage/);
  } finally {
    sandbox.cleanup();
  }
});
