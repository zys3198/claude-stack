'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');

function getClaudeDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}
function ensureDir(d) { fs.mkdirSync(d, { recursive: true }); }
function appendFile(fp, c) { fs.appendFileSync(fp, c); }

module.exports = { getClaudeDir, ensureDir, appendFile };
