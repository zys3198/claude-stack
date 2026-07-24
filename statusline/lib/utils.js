'use strict';

/**
 * Minimal utils for the standalone statusline bundle (~/.claude/statusline).
 *
 * Extracted from ECC scripts/lib/utils.js — only the three functions the
 * bridge writers (metrics-bridge / context-monitor / cost-tracker) actually
 * use. Keeping this tiny avoids dragging the full 641-line utils module.
 *
 * getClaudeDir() resolves the agent data home the same way ECC does
 * (ECC_AGENT_DATA_HOME env, else ~/.claude) so bridge + costs land where the
 * statusline expects them.
 */

const fs = require('fs');
const path = require('path');
const { resolveAgentDataHome } = require('./agent-data-home');

/**
 * Claude/agent config dir. Mirrors ECC utils.getClaudeDir() -> getAgentDataHome().
 * @returns {string}
 */
function getClaudeDir() {
  return resolveAgentDataHome();
}

/**
 * mkdir -p, tolerating a concurrent creator.
 * @param {string} dirPath
 */
function ensureDir(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  } catch (err) {
    // EEXIST is fine (race with another process creating it)
    if (err.code !== 'EEXIST') {
      throw new Error(`Failed to create directory '${dirPath}': ${err.message}`);
    }
  }
}

/**
 * Append content to a file, creating the parent dir first.
 * @param {string} filePath
 * @param {string} content
 */
function appendFile(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.appendFileSync(filePath, content, 'utf8');
}

module.exports = {
  getClaudeDir,
  ensureDir,
  appendFile,
};
