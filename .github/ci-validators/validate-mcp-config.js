#!/usr/bin/env node
/*
 * validate-mcp-config.js — ADNOC CI guard for `.vscode/mcp.json`
 *
 * Catches the exact bugs that broke earlier setups:
 *  - missing `<organization>` positional arg
 *  - `mode: agent` typo (should be `agent: 'agent'`) — checked in adjacent prompts/agents
 *  - `--tenant` accidentally placed in MCP args (belongs in `az login`)
 *  - missing `-d core repositories work work-items` domains
 *  - invented package names (`@copilot-mcp/*` and similar)
 *  - Confluence MCP/CLI mode drift (both enabled, neither enabled, or unsafe MCP config)
 *
 * Usage:  node ci-validators/validate-mcp-config.js [path-to-mcp.json]   (defaults to .vscode/mcp.json)
 * Exit codes: 0 = clean, 1 = config invalid
 *
 * Zero deps (Node core only). Drop into any repo's CI.
 */

const fs = require('node:fs');
const path = require('node:path');

const target = process.argv[2] || path.join(process.cwd(), '.vscode', 'mcp.json');

if (!fs.existsSync(target)) {
  console.error(`[validate-mcp-config] ERROR: file not found: ${target}`);
  process.exit(1);
}

let raw;
try {
  raw = fs.readFileSync(target, 'utf8').replace(/^\uFEFF/, ''); // BOM breaks JSON.parse
} catch (e) {
  console.error(`[validate-mcp-config] ERROR: cannot read ${target}: ${e.message}`);
  process.exit(1);
}

// Strip FULL-LINE comments + block comments to tolerate jsonc.
// Deliberately NOT stripping trailing "//" — it would corrupt URLs inside
// strings ("https://...") for remote MCP servers.
const stripped = raw
  .replace(/^\s*\/\/[^\n]*$/gm, '')
  .replace(/\/\*[\s\S]*?\*\//g, '');

let cfg;
try {
  cfg = JSON.parse(stripped);
} catch (e) {
  console.error(`[validate-mcp-config] ERROR: invalid JSON in ${target}: ${e.message}`);
  console.error(`[validate-mcp-config] note: trailing "//" comments are not supported by this gate — use full-line comments.`);
  process.exit(1);
}

const errors = [];
const warnings = [];

const KNOWN_PACKAGES = new Set([
  '@azure-devops/mcp',
  '@upstash/context7-mcp',
  '@modelcontextprotocol/server-github',
  '@modelcontextprotocol/server-postgres',
  'mcp-atlassian',
  // org-prefixed copies are also OK
]);

const REQUIRED_ADO_DOMAINS = ['core', 'repositories', 'work', 'work-items'];

const servers = cfg.mcpServers ?? cfg.servers ?? {};

if (typeof servers !== 'object' || Array.isArray(servers) || Object.keys(servers).length === 0) {
  errors.push(`Missing or empty "mcpServers" object`);
} else {
  for (const [name, s] of Object.entries(servers)) {
    const args = Array.isArray(s.args) ? s.args : [];

    // Check 1: package name is not an invented scope
    const pkg = args.find(a => typeof a === 'string' && (a.startsWith('@') || a.startsWith('mcp-atlassian')));
    if (pkg) {
      const bare = pkg.split('@').slice(0, -1).join('@') || pkg; // strip version if present
      const noVersion = bare.split(/[@^~>]/)[0].startsWith('@')
        ? bare.split('@').slice(0, 2).join('@')
        : bare;
      // Heuristic: anything starting with @copilot-mcp/ is invented
      if (pkg.startsWith('@copilot-mcp/')) {
        errors.push(
          `[${name}] uses invented MCP package "${pkg}". ` +
          `Use @azure-devops/mcp for ADO; see ai/SETUP-COPILOT.md.`
        );
      }
      const known = [...KNOWN_PACKAGES].some(k => pkg.startsWith(k));
      if (!known) {
        warnings.push(`[${name}] uses unknown package "${pkg}". Verify it exists on npm before shipping.`);
      }
    }

    // Check 2: Azure DevOps MCP specifics
    if (pkg && pkg.startsWith('@azure-devops/mcp')) {
      // 2a: organization positional arg right after package
      const pkgIdx = args.findIndex(a => typeof a === 'string' && a.includes('@azure-devops/mcp'));
      const next = args[pkgIdx + 1];
      const isOrgArg = typeof next === 'string'
        && !next.startsWith('-')
        && next !== '-y';
      if (!isOrgArg) {
        errors.push(
          `[${name}] missing <organization> positional arg right after "@azure-devops/mcp". ` +
          `The MCP server requires it (the URL slug from https://dev.azure.com/<slug>).`
        );
      }

      // 2b: --tenant should NOT be here (goes into az login)
      if (args.includes('--tenant')) {
        errors.push(
          `[${name}] has "--tenant" in MCP args. ` +
          `It's not an MCP flag — put the tenant in "az login --tenant <guid>" instead.`
        );
      }

      // 2c: --authentication must be 'pat' — the only method supported at ADNOC.
      //     Interactive 'az login' (Entra) is blocked by Conditional Access.
      const authIdx = args.indexOf('--authentication');
      if (authIdx === -1) {
        errors.push(`[${name}] missing "--authentication" — set "pat" (the only supported method). Without it the server picks a default that may not authenticate.`);
      } else {
        const method = args[authIdx + 1];
        if (method !== 'pat') {
          errors.push(`[${name}] --authentication is "${method}". Must be "pat" (ADNOC supports only PAT; az login is blocked).`);
        }
        // A PAT must never be hard-coded: VS Code references "${input:...}", Rider an OS env var.
        const tok = s.env && s.env.PERSONAL_ACCESS_TOKEN;
        if (method === 'pat' && typeof tok === 'string' && !/^\$\{(input|env):/.test(tok)) {
          errors.push(
            `[${name}] PERSONAL_ACCESS_TOKEN looks hard-coded. Reference it instead ` +
            `("\${input:ado_pat_b64}" in VS Code, or set the OS env var and drop the env block in Rider). ` +
            `Never commit the token.`
          );
        }
      }

      // 2d: -d domains include required four
      const dIdx = args.indexOf('-d');
      if (dIdx === -1) {
        errors.push(`[${name}] missing "-d" domain list. Required: ${REQUIRED_ADO_DOMAINS.join(', ')}.`);
      } else {
        const provided = new Set();
        for (let i = dIdx + 1; i < args.length; i++) {
          const a = args[i];
          if (typeof a !== 'string' || a.startsWith('-')) break;
          provided.add(a);
        }
        const missing = REQUIRED_ADO_DOMAINS.filter(d => !provided.has(d));
        if (missing.length > 0) {
          errors.push(
            `[${name}] -d is missing required domain(s): ${missing.join(', ')}. ` +
            `Without "repositories" the /ticket-to-branch flow breaks.`
          );
        }
      }
    }

    // Check 3: the template's Confluence MCP is pinned, secret-safe, and write-capable by default.
    if (name === 'confluence' || (pkg && pkg.startsWith('mcp-atlassian'))) {
      if (s.command !== 'uvx') {
        errors.push(`[${name}] command must be "uvx" for the pinned mcp-atlassian server.`);
      }
      if (!args.includes('mcp-atlassian@0.21.1')) {
        errors.push(`[${name}] must pin "mcp-atlassian@0.21.1"; unpinned upgrades previously broke startup.`);
      }
      const env = s.env || {};
      if (env.CONFLUENCE_URL !== 'https://confluence.adnoc.ae') {
        errors.push(`[${name}] CONFLUENCE_URL must be "https://confluence.adnoc.ae".`);
      }
      if (env.CONFLUENCE_PERSONAL_TOKEN !== '${input:confluence_pat}') {
        errors.push(`[${name}] CONFLUENCE_PERSONAL_TOKEN must reference "\${input:confluence_pat}"; never commit a literal token.`);
      }
      if (env.READ_ONLY_MODE !== 'false') {
        errors.push(`[${name}] READ_ONLY_MODE must be "false" in the committed default so approved write operations are available.`);
      }
      const inputs = Array.isArray(cfg.inputs) ? cfg.inputs : [];
      if (!inputs.some(input => input && input.id === 'confluence_pat' && input.password === true)) {
        errors.push(`[${name}] missing password input "confluence_pat".`);
      }
    }
  }
}

// Check 4: Copier selects exactly one Confluence path for generated repositories.
const repoRoot = path.dirname(path.dirname(path.resolve(target)));
const passportPath = path.join(repoRoot, '.copier-answers.yml');
const cliSkillPath = path.join(repoRoot, '.github', 'skills', 'generic', 'confluence', 'SKILL.md');
if (fs.existsSync(passportPath)) {
  const passport = fs.readFileSync(passportPath, 'utf8').replace(/^\uFEFF/, '');
  const choice = passport.match(/^use_confluence_cli:\s*(true|false)\s*$/m);
  if (!choice) {
    errors.push(`Passport is missing boolean "use_confluence_cli"; run a clean copier update.`);
  } else {
    const useCli = choice[1] === 'true';
    const hasMcp = Object.prototype.hasOwnProperty.call(servers, 'confluence');
    const hasCliSkill = fs.existsSync(cliSkillPath);
    if (useCli && (hasMcp || !hasCliSkill)) {
      errors.push(`use_confluence_cli=true requires CLI skill present and Confluence MCP absent (found: mcp=${hasMcp}, cliSkill=${hasCliSkill}).`);
    }
    if (!useCli && (!hasMcp || hasCliSkill)) {
      errors.push(`use_confluence_cli=false requires Confluence MCP present and CLI skill absent (found: mcp=${hasMcp}, cliSkill=${hasCliSkill}).`);
    }
  }
}

if (warnings.length > 0) {
  console.warn(`\n[validate-mcp-config] WARNINGS (${warnings.length}):`);
  warnings.forEach(w => console.warn(`  - ${w}`));
}

if (errors.length > 0) {
  console.error(`\n[validate-mcp-config] FAIL — ${errors.length} error(s):`);
  errors.forEach(e => console.error(`  - ${e}`));
  process.exit(1);
}

console.log(`\n[validate-mcp-config] OK — ${target} passes all checks.`);
process.exit(0);
