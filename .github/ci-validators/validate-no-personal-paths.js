#!/usr/bin/env node
/*
 * validate-no-personal-paths.js — ADNOC CI gate against absolute-path leaks
 *
 * Inspired by ECC's `scripts/ci/validate-no-personal-paths.js` (MIT).
 *
 * Catches:
 *  - `C:\Users\<name>\` Windows user paths
 *  - `/Users/<name>/` macOS user paths
 *  - `/home/<name>/` Linux home paths
 *  - leaked enterprise paths (e.g. `\\corp.adnoc.local\share\`)
 *
 * Scans all markdown, ps1, sh, json, yml under `.github/`, `ai/governance/`, `ai/`, `.azuredevops/`,
 * `CHAMPIONS.md`, the root README/SECURITY files, and `.copier-answers.yml`.
 * (Source code dirs are NOT scanned — paths there can be legitimate.)
 *
 * Note on `.copier-answers.yml`: its `_src_path` must be the Azure Repos **git URL** in
 * production (clean). A repo scaffolded from a LOCAL path will correctly FAIL here — that's
 * the signal to distribute the template via its git URL, not a local folder.
 *
 * Usage:  node ci-validators/validate-no-personal-paths.js
 *
 * Exit codes: 0 = clean, 1 = paths found
 */

const fs = require('node:fs');
const path = require('node:path');

const PATTERNS = [
  // Windows (single pattern: any drive letter, both slash conventions)
  { re: /[A-Z]:[\\\/]Users[\\\/][A-Za-z0-9._\- ]+/g, name: 'Windows user path' },
  // Unix
  { re: /\/Users\/[a-z0-9._\-]+\//gi, name: 'macOS user path' },
  { re: /\/home\/[a-z0-9._\-]+\//gi, name: 'Linux home path' },
  // Network shares
  { re: /\\\\[A-Za-z0-9._\-]+(\.adnoc\.local|\.corp\.)/gi, name: 'enterprise network share' },
  // Common tmp paths with user names
  { re: /\/tmp\/[a-z0-9._\-]+\//gi, name: 'tmp path with user-like segment' },
];

const PLACEHOLDER_USERNAMES = new Set([
  'example', 'me', 'user', 'username', 'you',
  'yourname', 'yourusername', 'your-username',
  'name', // generic placeholders used in the guide's path examples
]);

const SCAN_DIRS = [
  '.github',
  'governance',
  'ai',
  '.azuredevops',
  'enterprise-setup',
];

const SCAN_FILES = [
  'CHAMPIONS.md',
  'README.md',
  'SECURITY.md',
  'COVER_NOTE_FOR_MANAGER.md',
  'ADNOC_COPILOT_WORKFLOW_GUIDE.md',
  // The Copier passport records `_src_path`. In production that's the Azure Repos git URL
  // (clean); if a repo was scaffolded from a LOCAL path, this catches the leaked user path.
  '.copier-answers.yml',
];

const EXT_OK = /\.(md|ps1|sh|json|jsonc|yml|yaml|cs|ts|tsx|js)$/i;

const root = process.cwd();
const findings = [];

function scanFile(filePath) {
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch {
    return; // binary or unreadable, skip
  }
  const lines = content.split('\n');

  for (const { re, name } of PATTERNS) {
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(content)) !== null) {
      // Compute line number once
      const lineNo = content.slice(0, m.index).split('\n').length;
      const lineText = lines[lineNo - 1] || '';

      // Honor `// validator-allow` escape hatch on the same line
      if (/\/\/\s*validator-allow\b/i.test(lineText)) {
        if (m[0].length === 0) break;
        continue;
      }

      // Skip placeholder usernames (example, me, user, yourname, etc.)
      const segments = m[0].split(/[\\\/]+/);
      const usernameSeg = segments[segments.length - 1].toLowerCase();
      if (PLACEHOLDER_USERNAMES.has(usernameSeg)) {
        if (m[0].length === 0) break;
        continue;
      }

      findings.push({
        file: path.relative(root, filePath),
        line: lineNo,
        pattern: name,
        match: m[0],
      });
      if (m[0].length === 0) break; // safety
    }
  }
}

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  const stat = fs.statSync(dir);
  if (stat.isFile()) {
    if (EXT_OK.test(dir)) scanFile(dir);
    return;
  }
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.git')) continue;
    if (entry.name === 'node_modules') continue;
    // The gate scripts themselves contain path PATTERNS and doc examples by design —
    // scanning them produces false positives (a validator matching its own definitions).
    if (entry.name === 'ci-validators') continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(p);
    } else if (EXT_OK.test(entry.name)) {
      scanFile(p);
    }
  }
}

for (const d of SCAN_DIRS) {
  walk(path.join(root, d));
}
for (const f of SCAN_FILES) {
  const full = path.join(root, f);
  if (fs.existsSync(full)) scanFile(full);
}

if (findings.length > 0) {
  console.error(`\n[validate-no-personal-paths] FAIL — ${findings.length} leak(s):`);
  findings.forEach(f => {
    console.error(`  ${f.file}:${f.line}  [${f.pattern}]  "${f.match}"`);
  });
  console.error(`\nReplace absolute paths with relative paths or environment variables.`);
  console.error(`If a path is intentionally absolute (rare), add a "// validator-allow" comment.`);
  process.exit(1);
}

console.log(`\n[validate-no-personal-paths] OK — no personal paths leaked.`);
process.exit(0);
