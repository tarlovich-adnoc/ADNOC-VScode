#!/usr/bin/env node
/*
 * check-unicode-safety.js — ADNOC CI gate against invisible-char prompt injection
 *
 * Adapted from ECC's `scripts/ci/check-unicode-safety.js` (MIT).
 *
 * Catches the "ASCII smuggling" attack vector: attackers hide LLM instructions
 * inside Unicode Tag block (U+E0000–U+E007F) characters in PR bodies, SKILL.md,
 * frontmatter, or any text Copilot ingests. The bytes look invisible to a human
 * reviewer but the LLM tokenizer consumes them. Also catches BiDi overrides,
 * zero-width chars, BOMs, and other invisible homoglyphs commonly used in
 * supply-chain attacks.
 *
 * Scope: `.github/`, `ai/governance/`, `ai/`, `.azuredevops/`, `azure-pipelines/`, top-level docs.
 * Excludes binary / non-text / vendor dirs.
 *
 * Modes:
 *   default        — report violations and exit 1
 *   --write        — auto-strip dangerous chars from `.md/.mdx/.txt` only
 *
 * Usage:  node ci-validators/check-unicode-safety.js [--write]
 * Exit codes: 0 = clean, 1 = at least one violation
 */

const fs = require('node:fs');
const path = require('node:path');

const writeMode = process.argv.includes('--write');

const SCAN_DIRS = [
  '.github',
  'governance',
  'ai',
  '.azuredevops',
  'azure-pipelines',
];
const SCAN_FILES = [
  '.mcp.json',
  '.vscode/mcp.json',
  'README.md',
];

const TEXT_EXTENSIONS = new Set([
  '.md', '.mdx', '.txt', '.js', '.cjs', '.mjs', '.ts', '.tsx', '.jsx',
  '.json', '.jsonc', '.toml', '.yml', '.yaml', '.sh', '.bash', '.ps1', '.py', '.cs',
]);
const WRITABLE_EXTENSIONS = new Set(['.md', '.mdx', '.txt']);
const IGNORED_DIRS = new Set(['.git', 'node_modules', '.next', 'coverage', 'venv', '.venv', 'dist', 'build']);

function isDangerousInvisibleCodePoint(cp) {
  return (
    (cp >= 0x200B && cp <= 0x200D) ||         // ZWSP/ZWNJ/ZWJ
    cp === 0x2060 ||                          // WORD JOINER
    cp === 0xFEFF ||                          // BOM
    (cp >= 0x202A && cp <= 0x202E) ||         // BiDi overrides
    (cp >= 0x2066 && cp <= 0x2069) ||         // BiDi isolates
    (cp >= 0xFE00 && cp <= 0xFE0F) ||         // Variation selectors
    (cp >= 0xE0100 && cp <= 0xE01EF) ||       // Variation selectors supplement
    (cp >= 0xE0000 && cp <= 0xE007F) ||       // (!) Tag block — ASCII smuggling vector
    cp === 0x180E ||                          // Mongolian Vowel Separator
    cp === 0x115F || cp === 0x1160 ||         // Hangul fillers
    (cp >= 0x2061 && cp <= 0x2064) ||         // Invisible math operators
    cp === 0x3164                             // Hangul Filler
  );
}

// ADNOC house rule: shipped artifacts are plain-text English with NO emoji / pictographs.
// These are VISIBLE, so the invisible-char check above misses them. Flag the emoji blocks.
// Legitimate typography (em/en dash, arrows U+2190-21FF, >=, middot, ellipsis, (c), box-drawing
// U+2500-257F) is OUTSIDE these ranges and stays allowed.
function isForbiddenEmoji(cp) {
  return (
    (cp >= 0x2600 && cp <= 0x27BF) ||         // Misc Symbols + Dingbats (warning, check, cross, hand)
    (cp >= 0x2B00 && cp <= 0x2BFF) ||         // stars / pictographic arrows
    (cp >= 0x1F000 && cp <= 0x1FAFF)          // emoji pictographs (lock, party, traffic lights)
  );
}

function lineAndColumn(text, index) {
  let line = 1, col = 1;
  for (let i = 0; i < index; i++) {
    if (text[i] === '\n') { line++; col = 1; } else { col++; }
  }
  return { line, col };
}

function findInvisibles(content) {
  const findings = [];
  for (let i = 0; i < content.length; i++) {
    const cp = content.codePointAt(i);
    // A BOM at offset 0 is a legitimate Windows encoding artifact (PowerShell 5.1's
    // `-Encoding utf8` writes one), not smuggling. Anywhere ELSE it stays flagged.
    if (i === 0 && cp === 0xFEFF) continue;
    if (isDangerousInvisibleCodePoint(cp)) {
      const loc = lineAndColumn(content, i);
      findings.push({ kind: 'invisible', codePoint: cp.toString(16).toUpperCase().padStart(4, '0'), ...loc });
    } else if (isForbiddenEmoji(cp)) {
      const loc = lineAndColumn(content, i);
      findings.push({ kind: 'emoji', char: String.fromCodePoint(cp), codePoint: cp.toString(16).toUpperCase().padStart(4, '0'), ...loc });
    }
    if (cp > 0xFFFF) i++; // skip low surrogate
  }
  return findings;
}

function stripDangerous(content) {
  let out = '';
  for (let i = 0; i < content.length; i++) {
    const cp = content.codePointAt(i);
    // keep a LEADING BOM — the checker tolerates it, so the fixer must too
    if (i === 0 && cp === 0xFEFF) { out += String.fromCodePoint(cp); continue; }
    if (!isDangerousInvisibleCodePoint(cp)) {
      out += String.fromCodePoint(cp);
    }
    if (cp > 0xFFFF) i++;
  }
  return out;
}

// Treat a *.jinja template source as the type it renders to, so a scan of the template
// SOURCE also covers copilot-instructions.md.jinja, *.instructions.md.jinja, verify scripts,
// etc. In a rendered team repo there are no .jinja files, so this is a no-op there.
function isTextFile(name) {
  const base = name.endsWith('.jinja') ? name.slice(0, -6) : name;
  return TEXT_EXTENSIONS.has(path.extname(base));
}

function walk(dir, files) {
  if (!fs.existsSync(dir)) return;
  const stat = fs.statSync(dir);
  if (stat.isFile()) { files.push(dir); return; }
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED_DIRS.has(entry.name)) continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p, files);
    else if (isTextFile(entry.name)) files.push(p);
  }
}

const root = process.cwd();
const files = [];
for (const d of SCAN_DIRS) walk(path.join(root, d), files);
for (const f of SCAN_FILES) {
  for (const cand of [f, f + '.jinja']) {     // also catch the .jinja source variant
    const full = path.join(root, cand);
    if (fs.existsSync(full) && isTextFile(cand)) { files.push(full); break; }
  }
}

let violations = 0;
let autoFixed = 0;

for (const file of files) {
  const ext = path.extname(file);
  let content;
  try { content = fs.readFileSync(file, 'utf8'); }
  catch { continue; }

  const findings = findInvisibles(content);
  if (findings.length === 0) continue;

  // --write only strips INVISIBLE chars from .md/.mdx/.txt. Emoji are NEVER auto-stripped
  // (the ASCII replacement is a human call) and always count as a violation — so a --write
  // run can never report success while emoji remain.
  const invisible = findings.filter((f) => f.kind !== 'emoji');
  const didStrip = writeMode && WRITABLE_EXTENSIONS.has(ext) && invisible.length > 0;
  if (didStrip) {
    fs.writeFileSync(file, stripDangerous(content), 'utf8');
    autoFixed += invisible.length;
    console.log(`[check-unicode-safety] fixed ${invisible.length} invisible char(s) in ${path.relative(root, file)}`);
  }

  for (const f of findings) {
    if (didStrip && f.kind !== 'emoji') continue; // this invisible was just stripped — not a violation
    const label = f.kind === 'emoji' ? `emoji ${f.char} U+${f.codePoint}` : `invisible-cp U+${f.codePoint}`;
    console.error(`${path.relative(root, file)}:${f.line}:${f.col}  ${label}`);
    violations++;
  }
}

if (writeMode && autoFixed > 0) {
  console.log(`\n[check-unicode-safety] auto-fixed ${autoFixed} invisible char(s) across ${files.length} files. Emoji are never auto-fixed — replace them with ASCII by hand.`);
}

if (violations > 0) {
  console.error(`\n[check-unicode-safety] FAIL — ${violations} forbidden char(s) found (invisible smuggling chars and/or emoji).`);
  console.error(`Invisible chars are an ASCII-smuggling / prompt-injection vector; emoji are banned in shipped artifacts (plain-text English only).`);
  console.error(`Run with --write to auto-strip invisible chars from .md/.mdx/.txt files; replace emoji with ASCII by hand.`);
  process.exit(1);
}

console.log(`\n[check-unicode-safety] OK — no forbidden chars (invisible or emoji) in ${files.length} files.`);
process.exit(0);
