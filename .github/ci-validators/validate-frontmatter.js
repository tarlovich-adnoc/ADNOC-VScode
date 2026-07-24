#!/usr/bin/env node
/*
 * validate-frontmatter.js — ADNOC CI gate for YAML frontmatter shape
 *
 * Inspired by ECC's CI validators (MIT).
 *
 * Catches:
 *  - prompt files using `mode: agent` (the silent-breakage bug — should be `agent: 'agent'`)
 *  - missing required fields per file type:
 *      .instructions.md → description, applyTo
 *      .prompt.md       → description, agent
 *      .agent.md        → description, tools
 *      SKILL.md         → name, description (covered by validate-skills.js but rechecked here)
 *  - malformed YAML (frontmatter block without closing `---`)
 *  - `applyTo` using brace expansion ({ts,tsx}) which isn't guaranteed in VS Code
 *
 * Usage:  node ci-validators/validate-frontmatter.js [path-to-.github]
 *
 * Exit codes: 0 = clean, 1 = at least one file invalid
 */

const fs = require('node:fs');
const path = require('node:path');

const root = process.argv[2] || path.join(process.cwd(), '.github');

if (!fs.existsSync(root)) {
  console.error(`[validate-frontmatter] ERROR: root not found: ${root}`);
  process.exit(1);
}

const errors = [];
const warnings = [];

const REQUIRED = {
  '.instructions.md': ['description', 'applyTo'],
  '.prompt.md':       ['description', 'agent'],
  '.agent.md':        ['description'],   // tools optional but recommended
  'SKILL.md':         ['name', 'description'],
};

function categorize(filename) {
  // Strip a trailing `.jinja` so source-side template files (e.g. `code-reviewer.agent.md.jinja`)
  // are validated too — not just rendered output in a team repo.
  const name = filename.endsWith('.jinja') ? filename.slice(0, -'.jinja'.length) : filename;
  if (name === 'SKILL.md') return 'SKILL.md';
  if (name.endsWith('.instructions.md')) return '.instructions.md';
  if (name.endsWith('.prompt.md'))       return '.prompt.md';
  if (name.endsWith('.agent.md'))        return '.agent.md';
  return null;
}

function parseFrontmatter(content) {
  if (!content.startsWith('---\n')) return { fm: null, error: 'no frontmatter block at file start' };
  const endIdx = content.indexOf('\n---', 4);
  if (endIdx === -1) return { fm: null, error: 'frontmatter block not closed with ---' };
  const block = content.slice(4, endIdx);
  const fm = {};
  let lastKey = null;
  for (const line of block.split('\n')) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const m = line.match(/^(\w[\w-]*):\s*(.*)$/);
    if (m) {
      lastKey = m[1];
      fm[lastKey] = m[2] === '' ? null : m[2].replace(/^['"]|['"]$/g, '');
    } else if (lastKey && line.startsWith('  ')) {
      fm[lastKey] = (fm[lastKey] || '') + ' ' + line.trim();
    }
  }
  return { fm, error: null };
}

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.git') || entry.name === 'node_modules') continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(p);
      continue;
    }
    const cat = categorize(entry.name);
    if (!cat) continue;
    check(p, cat);
  }
}

function check(filePath, cat) {
  const rel = path.relative(process.cwd(), filePath);
  // Normalize CRLF -> LF: Copier writes verbatim files with CRLF on Windows, and the
  // frontmatter check is newline-sensitive. Without this, valid files fail with a confusing
  // "no frontmatter block at file start" on Windows-scaffolded repos.
  // Also strip a UTF-8 BOM: Windows PowerShell 5.1's `Set-Content -Encoding utf8` writes one,
  // and a BOM before "---" reads as "no frontmatter at file start".
  const content = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
  const { fm, error } = parseFrontmatter(content);
  if (error) {
    errors.push(`${rel}: ${error}`);
    return;
  }
  // Required fields
  for (const field of REQUIRED[cat]) {
    if (!fm[field]) {
      errors.push(`${rel}: missing required frontmatter "${field}" (${cat})`);
    }
  }
  // Prompt-specific: catch the silent-breakage bug
  if (cat === '.prompt.md') {
    if (fm.mode) {
      errors.push(
        `${rel}: uses "mode: ${fm.mode}" — legacy pre-2026 "chat modes" field, no longer in the ` +
        `VS Code prompt-file schema. The current field is "agent" (e.g. agent: 'agent'). On ` +
        `current builds "mode:" is ignored and the prompt silently runs without agent powers.`
      );
    }
    if (fm.agent && !['agent', 'ask', 'plan'].includes(fm.agent)) {
      warnings.push(
        `${rel}: agent="${fm.agent}" is non-standard. ` +
        `Common values: 'agent' (default), 'ask', 'plan', or a custom agent name from .github/agents/.`
      );
    }
  }
  // Instruction-specific: glob shape
  if (cat === '.instructions.md' && fm.applyTo) {
    if (/\{[^}]*,[^}]*\}/.test(fm.applyTo)) {
      warnings.push(
        `${rel}: applyTo uses brace expansion "${fm.applyTo}". ` +
        `VS Code does not guarantee brace expansion in applyTo. Use comma-separated form: ` +
        `"**/*.ts,**/*.tsx" instead of "**/*.{ts,tsx}".`
      );
    }
  }
  // Tools field: catch the deprecated unnamespaced names
  if ((cat === '.prompt.md' || cat === '.agent.md') && fm.tools) {
    if (/\brunCommands\b/.test(fm.tools)) {
      errors.push(
        `${rel}: tools array references "runCommands" — that is NOT a real VS Code tool name. ` +
        `Use "execute/runInTerminal" instead.`
      );
    }
    if (/(?<!\/)\beditFiles\b/.test(fm.tools)) {
      warnings.push(
        `${rel}: tools array references "editFiles" (unnamespaced) — deprecated form. ` +
        `Use "edit/editFiles" instead.`
      );
    }
  }
}

walk(root);

if (warnings.length > 0) {
  console.warn(`\n[validate-frontmatter] WARNINGS (${warnings.length}):`);
  warnings.forEach(w => console.warn(`  - ${w}`));
}

if (errors.length > 0) {
  console.error(`\n[validate-frontmatter] FAIL — ${errors.length} error(s):`);
  errors.forEach(e => console.error(`  - ${e}`));
  process.exit(1);
}

console.log(`\n[validate-frontmatter] OK — all frontmatter blocks valid.`);
process.exit(0);
