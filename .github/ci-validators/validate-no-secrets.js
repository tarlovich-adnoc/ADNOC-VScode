#!/usr/bin/env node
/*
 * validate-no-secrets.js — ADNOC CI gate against committed credentials
 *
 * Catches the classic leak shapes in AI-workflow files:
 *  - private key blocks (-----BEGIN ... PRIVATE KEY-----)
 *  - AWS access key ids (AKIA...)
 *  - GitHub tokens (ghp_/gho_/ghu_/ghs_/ghr_, github_pat_)
 *  - Slack tokens (xoxb-/xoxp-/...)
 *  - Azure Storage AccountKey= / SharedAccessSignature= material
 *  - generic quoted secrets:  password/secret/token/apikey = "real-looking-value"
 *
 * Deliberately conservative: placeholders (<token>, ${VAR}, $(var), env:NAME, example,
 * changeme, your-..., paste-..., ***, xxx) are ignored, and a `// validator-allow` comment on
 * the same line is an escape hatch — same conventions as validate-no-personal-paths.
 *
 * Scope: .github/, ai/governance/, ai/, .azuredevops/, azure-pipelines/, plus root config/docs
 * (.vscode/mcp.json, README.md). Source dirs are NOT scanned —
 * real secret scanning for src/ belongs to the platform scanner; this gate protects the
 * AI-workflow surface every team ships.
 *
 * Usage:  node ci-validators/validate-no-secrets.js
 * Exit codes: 0 = clean, 1 = potential secret found
 */

const fs = require('node:fs');
const path = require('node:path');

const PATTERNS = [
  { re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/g, name: 'private key block' },
  { re: /\bAKIA[0-9A-Z]{16}\b/g, name: 'AWS access key id' },
  { re: /\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b/g, name: 'GitHub token' },
  { re: /\bgithub_pat_[A-Za-z0-9_]{30,}\b/g, name: 'GitHub fine-grained PAT' },
  { re: /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/g, name: 'Slack token' },
  { re: /AccountKey=[A-Za-z0-9+/=]{40,}/g, name: 'Azure Storage account key' },
  { re: /SharedAccessSignature=sv=[^\s"']{20,}/g, name: 'Azure SAS token' },
  // lookbehind (not a consuming group) keeps m.index on the credential name → correct line numbers
  { re: /(?<=^|[\s"'-])((?:[A-Za-z0-9]+_)*(?:password|passwd|pwd|secret|token|api[_-]?key|pat))\b\s*[:=]\s*["']([^"'\s]{8,})["']/gim, name: 'hardcoded credential assignment' },
  // unquoted assignments (yml / sh / ps1 style): password: hunter2hunter2 / AZURE_DEVOPS_EXT_PAT: <52 chars>; optional trailing # comment
  { re: /(?<=^|[\s"'-])((?:[A-Za-z0-9]+_)*(?:password|passwd|pwd|secret|token|api[_-]?key|pat))\b\s*[:=][ \t]*([A-Za-z0-9+/_.-]{12,})[ \t]*(?:#.*)?$/gim, name: 'hardcoded credential assignment (unquoted)' },
];

// Values that are clearly placeholders, not credentials.
const PLACEHOLDER_RE = /<[^>]+>|\$\{|\$\(|%\w+%|\benv:|\bexample\b|\bchangeme\b|\byour[-_]|\bpaste[_-]|\*\*\*|\bxxx+\b|\bplaceholder\b|\bdummy\b|\bredacted\b/i;

const SCAN_DIRS = ['.github', 'governance', 'ai', '.azuredevops', 'azure-pipelines'];
const SCAN_FILES = ['.mcp.json', '.vscode/mcp.json', 'README.md', 'CHAMPIONS.md'];
const EXT_OK = /\.(md|ps1|sh|json|jsonc|yml|yaml|txt)$/i;

const root = process.cwd();
const findings = [];

function scanFile(filePath) {
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
  } catch {
    return; // binary or unreadable
  }
  const lines = content.split('\n');

  for (const { re, name } of PATTERNS) {
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(content)) !== null) {
      const lineNo = content.slice(0, m.index).split('\n').length;
      const lineText = lines[lineNo - 1] || '';

      // escape hatch (line-level) + placeholder filter (against the captured VALUE when the
      // pattern captures one — a "# example" trailing comment must not exempt a real secret)
      const valueToTest = m[2] !== undefined ? m[2] : m[0];
      if (/\/\/\s*validator-allow\b/i.test(lineText) || PLACEHOLDER_RE.test(valueToTest)) {
        if (m[0].length === 0) break;
        continue;
      }

      findings.push({
        file: path.relative(root, filePath),
        line: lineNo,
        pattern: name,
        // never echo the captured value itself — print a redacted stub
        match: m[0].slice(0, 12) + '…[redacted]',
      });
      if (m[0].length === 0) break;
    }
  }
}

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.git')) continue;
    if (entry.name === 'node_modules') continue;
    // The gate scripts define the detection patterns — scanning them is a self-match trap.
    if (entry.name === 'ci-validators') continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p);
    else if (EXT_OK.test(entry.name)) scanFile(p);
  }
}

for (const d of SCAN_DIRS) walk(path.join(root, d));
for (const f of SCAN_FILES) {
  const full = path.join(root, f);
  if (fs.existsSync(full)) scanFile(full);
}

if (findings.length > 0) {
  console.error(`\n[validate-no-secrets] FAIL — ${findings.length} potential secret(s):`);
  findings.forEach(f => {
    console.error(`  ${f.file}:${f.line}  [${f.pattern}]  "${f.match}"`);
  });
  console.error(`\nRotate anything real IMMEDIATELY (committed = leaked), then remove it from the file.`);
  console.error(`Use environment variables / a variable group / Azure Key Vault instead of literals.`);
  console.error(`False positive? Add a "// validator-allow" comment on that line.`);
  process.exit(1);
}

console.log(`\n[validate-no-secrets] OK — no committed credentials detected.`);
process.exit(0);
