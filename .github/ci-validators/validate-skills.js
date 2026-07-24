#!/usr/bin/env node
/*
 * validate-skills.js — ADNOC CI gate for `.github/skills/<role>/<name>/SKILL.md`
 *
 * Inspired by ECC's `scripts/ci/validate-skills.js` (MIT).
 *
 * Skills are organized in role subdirectories:
 *   .github/skills/<role>/<name>/SKILL.md
 * where <role> is one of: ba, devops, generic, optional, qa, team-local.
 * SKILL.md.jinja (Jinja-templated skills, e.g. generic/verify) are also validated.
 *
 * Catches:
 *  - skill files in the wrong place (must be `.github/skills/<role>/<name>/SKILL.md`)
 *  - filename not literally `SKILL.md` or `SKILL.md.jinja` (case-sensitive)
 *  - missing `name` or `description` frontmatter
 *  - `name` doesn't match the parent directory (<name>)
 *  - description too short (< 30 chars) — Copilot needs trigger phrases for auto-discovery
 *  - missing "Use when" or "Use this skill" trigger language
 *
 * Usage:  node ci-validators/validate-skills.js [skills-root]
 * Default skills-root: `.github/skills`
 *
 * Exit codes: 0 = clean, 1 = at least one skill invalid
 */

const fs = require('node:fs');
const path = require('node:path');

const root = process.argv[2] || path.join(process.cwd(), '.github', 'skills');

if (!fs.existsSync(root)) {
  console.error(`[validate-skills] ERROR: skills root not found: ${root}`);
  console.error(`  Skills MUST live in .github/skills/ (Microsoft's documented discovery path).`);
  process.exit(1);
}

const errors = [];
const warnings = [];
let checked = 0;

function parseFrontmatter(content) {
  // Very small YAML-ish parser — handles the flat key:value structure we use
  if (!content.startsWith('---\n')) return null;
  const endIdx = content.indexOf('\n---', 4);
  if (endIdx === -1) return null;
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
      // continuation (folded scalar like description: > \n  ...)
      fm[lastKey] = (fm[lastKey] || '') + ' ' + line.trim();
    }
  }
  return fm;
}

// README / CHANGELOG / LICENSE etc. are documentation, NOT skills — ignore them.
const DOC_RE = /^(readme|changelog|contributing|license|notice)\.md$/i;

function validateSkill(name, file) {
  checked++;
  // Normalize CRLF -> LF first: Copier writes verbatim SKILL.md files with CRLF on Windows,
  // which would otherwise both hide the frontmatter and leave a trailing \r on `name`
  // (false "name doesn't match dir" error).
  const fm = parseFrontmatter(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n'));
  if (!fm) {
    errors.push(`[${name}] SKILL.md has no YAML frontmatter (missing the --- block).`);
    return;
  }
  if (!fm.name) {
    errors.push(`[${name}] SKILL.md frontmatter missing "name:".`);
  } else if (fm.name !== name) {
    errors.push(
      `[${name}] frontmatter name="${fm.name}" doesn't match parent dir "${name}". ` +
      `Microsoft requires them to match (silent discovery failure otherwise).`
    );
  }
  if (!fm.description) {
    errors.push(`[${name}] SKILL.md frontmatter missing "description:".`);
  } else if (fm.description.trim().length < 30) {
    warnings.push(
      `[${name}] description is only ${fm.description.trim().length} chars. ` +
      `Auto-discovery works best with 50+ chars and concrete trigger phrases ` +
      `("Use when the user asks to...").`
    );
  } else if (!/\b(use when|use this|when the user)/i.test(fm.description)) {
    warnings.push(
      `[${name}] description doesn't contain "Use when" / "Use this skill" / ` +
      `"when the user". Auto-discovery quality is significantly better with these phrases.`
    );
  }
}

function walkSkillDirs(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const skillDir = path.join(dir, entry.name);
    const items = fs.readdirSync(skillDir, { withFileTypes: true });
    const hasSkill     = items.some(e => e.isFile() && e.name === 'SKILL.md');
    // SKILL.md.jinja is a Jinja template that renders to SKILL.md in team repos.
    // Validate it here too so template-source runs catch name/description issues.
    const hasSkillJinja = !hasSkill && items.some(e => e.isFile() && e.name === 'SKILL.md.jinja');
    const subdirs = items.filter(e => e.isDirectory());
    // a candidate skill file = a .md that isn't a doc (README) and isn't already SKILL.md
    const candidateMd = items
      .filter(e => e.isFile() && /\.md$/i.test(e.name) && !DOC_RE.test(e.name) && e.name !== 'SKILL.md')
      .map(e => e.name);

    if (hasSkill) {
      validateSkill(entry.name, path.join(skillDir, 'SKILL.md'));
    } else if (hasSkillJinja) {
      validateSkill(entry.name, path.join(skillDir, 'SKILL.md.jinja'));
    } else if (candidateMd.length > 0) {
      // a non-SKILL, non-README .md sitting where a skill should be = a mis-named skill
      errors.push(
        `[${entry.name}] filename is "${candidateMd[0]}" — must be exactly "SKILL.md" ` +
        `(uppercase, singular). Copilot's auto-discovery is case-sensitive.`
      );
    }
    // Role container dirs (ba/, devops/, generic/, qa/, etc.) hold skills one level deeper.
    // Recurse so <role>/<name>/SKILL.md is validated, while <role>/README.md is ignored.
    if (subdirs.length > 0) walkSkillDirs(skillDir);
  }
}

walkSkillDirs(root);

if (warnings.length > 0) {
  console.warn(`\n[validate-skills] WARNINGS (${warnings.length}):`);
  warnings.forEach(w => console.warn(`  - ${w}`));
}

if (errors.length > 0) {
  console.error(`\n[validate-skills] FAIL — ${errors.length} error(s) across ${checked} skill(s):`);
  errors.forEach(e => console.error(`  - ${e}`));
  process.exit(1);
}

console.log(`\n[validate-skills] OK — ${checked} skill(s) pass all checks.`);
process.exit(0);
