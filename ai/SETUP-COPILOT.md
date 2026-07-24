# Connect Copilot to Azure DevOps & Confluence — onehub-team

This is a one-time bit of plumbing. Once it's done, Copilot can reach into your real work — read your Azure DevOps tickets and code, and pull documentation out of Confluence — instead of only seeing the file you happen to have open. You do it once per machine and then forget it exists.

There are two connections here, and you only set up the one(s) your role actually uses. Your section in `BY-ROLE.md` tells you which. The short version:

1. **Azure DevOps** (right below) — your work items and repos. Developers and QA need it; BA, PM, and Designer can skip it unless you pull tickets.
2. **Confluence** (further down, past the `---`) — your documentation space. Mainly BAs and PMs working with requirements and KB pages.

*Designer? Neither of these is yours — your one tool connects to **Figma** instead. See the Designer section in `BY-ROLE.md`.*

> **Not a developer or QA?** Your setup is short. **BA / PM: skip straight to the Confluence half** (past
> the `---` divider below) — the long Azure DevOps section right underneath is only for people who work
> the board. Designer: your step is the Figma one in `BY-ROLE.md`.

Not sure whether you already did this? Type `/copilot-doctor` in Copilot Chat. It checks the local
setup, inventories active MCP servers, and gives you a copy-ready test prompt for each configured
connection. A successful actual tool response means no setup action is required for that server.

<a id="azure-devops"></a>
## Azure DevOps

Here's what this buys you: with the connection in place you can ask Copilot "what are my open tickets?", pull a work item straight into your chat with `/ado-intake`, and have it link a pull request back to its ticket — no copy-pasting between browser tabs. The thing doing the reaching-out is a small local connector called an **MCP server** — it just gives Copilot a way to talk to an outside system, in this case Azure DevOps. Set it up once per person, per machine.

> Worth knowing before you start: the rest of the AI workflow — chat, the `/` prompts, the skills,
> the instructions, code completion — all works **without** this. The steps below are only for the
> live Azure DevOps integration (`/ado-intake`, reading and writing work items, PR auto-linking). So
> if a step trips you up, you're not blocked — keep using Copilot and come back to finish this later.

## What you need first

- A **GitHub Copilot** seat assigned, signed in, with **Copilot Chat**. In VS Code, switch the chat
  to **Agent** mode; in Rider the Copilot plugin must be a **2026 build** (older builds don't show
  agents or MCP at all).
- **Node.js** on your machine — open a terminal and run `node -v`. Nothing prints? Install Node LTS
  first (the MCP server runs through `npx`, which comes with Node).

The way you'll sign in is a **Personal Access Token** — a PAT, basically a scoped password you
generate for Copilot. It's the only method that works at ADNOC: the interactive `az login` / Entra
sign-in is blocked by Conditional Access, so don't reach for that.

## Step 1 — create a PAT (2 minutes)

1. Open `https://dev.azure.com/DevOpsAD` → User Settings(button to the left of top-right avatar) → **Personal access tokens**.
2. **+ New Token**. Name it e.g. `copilot-mcp`. Expiry: your org's max.
3. **Scopes** (least privilege):
   - **Work Items → Read** — or **Read & Write** if Copilot will *create* items for you. **QA, and anyone
     who'll generate test cases or bugs into ADO: choose Read & Write now** — the create-in-ADO skills
     fail with a permissions error on a read-only token.
   - **Code → Read**
4. **Create**, then **copy the token now** — you can't see it again.

## Step 2 — base64-encode it

The connector wants that token handed over as one scrambled string rather than raw. That format is
**base64** — not encryption, just a reversible way of rewriting text so tools can pass it around
cleanly. Concretely, it expects `PERSONAL_ACCESS_TOKEN` to be the base64 of `email:pat` (the email
can be anything non-empty; only the token part is actually used).

**PowerShell (Windows):**
```powershell
$pat = 'PASTE_YOUR_PAT_HERE'
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("you@adnoc.ae:$pat"))
```

**Terminal (macOS / Linux):**
```bash
pat='PASTE_YOUR_PAT_HERE'
printf '%s' "you@adnoc.ae:$pat" | base64 | tr -d '\n'
```

Copy the resulting string. And the rule that matters most: **do not paste the token or this string
into any file in the repo, into chat, or into a commit.**

## Step 3 — wire your IDE

Pick your editor.

### VS Code (config already ships in this repo)

This repo already carries `.vscode/mcp.json` with the server set up — all you add is the secret:

1. Open `.vscode/mcp.json`. Above the `azure-devops` server you'll see a **`▶ Start`** link — click it.
   (No link? `Ctrl+Shift+P` → **MCP: List Servers** → `azure-devops` → **Start**.)
2. A field **`ado_pat_b64`** appears at the top — paste the **base64 string** from Step 2, Enter.
   VS Code keeps it in its encrypted secret store; it never touches the file.
3. The server should reach **Running** and discover its tools (you'll see a "N tools" count).

### Rider / other JetBrains IDEs

Rider cannot use VS Code's `${input:...}` secret prompt, so the token goes into an OS environment
variable. The `copilot-doctor` skill creates or repairs a root `.mcp.json` from the committed
`.vscode/mcp.json`, removing only VS Code-only inputs and secret placeholders. The server then
inherits the secret from the OS:

1. Set the env var once, then **fully restart Rider** so it inherits it:

   **PowerShell (Windows):**
   ```powershell
   setx PERSONAL_ACCESS_TOKEN "PASTE_BASE64_FROM_STEP_2"
   ```

   **Terminal (macOS) — add to `~/.zshrc` then restart Rider:**
   ```bash
   echo 'export PERSONAL_ACCESS_TOKEN="PASTE_BASE64_FROM_STEP_2"' >> ~/.zshrc
   source ~/.zshrc
   ```
   **Terminal (Linux) — add to `~/.profile`, then sign out and back in:**
   ```bash
   echo 'export PERSONAL_ACCESS_TOKEN="PASTE_BASE64_FROM_STEP_2"' >> ~/.profile
   ```
2. In Copilot Chat run **`/copilot-doctor`** and identify Rider if asked. It creates or corrects
   `.mcp.json` only when its normalized server configuration differs from `.vscode/mcp.json`.
3. **Copilot icon** → **Edit Settings** → **Model Context Protocol** → **Configure**. Open/import the
   repository's `.mcp.json` if Rider has not discovered it, then save and start the server. In
   **Agent mode**, the tools icon shows `azure-devops`.

## Step 4 — verify it actually works

Now prove it. In Copilot Chat (**Agent** mode), ask for something that can only come from Azure
DevOps. For example:

> Using the azure-devops tools, list my recent work items in project OneMenu.

If it returns real items, you're connected. Finish with **`/copilot-doctor`** for the full green check.

## Troubleshooting

When something's off, it's almost always one of these:

| Symptom | Cause | Fix |
|---|---|---|
| Server won't start, `npx` hangs/fails | npm registry not reachable | Confirm `npm -v` works and `registry.npmjs.org` is reachable; if blocked, raise with IT — Copilot still works without the MCP |
| `401 Unauthorized` from the server | PAT wrong scope / expired, or base64 of the wrong thing | Re-do Steps 1–2; ensure base64 is of `email:pat`, not the raw PAT |
| Chat returns `failed to decide RAI policy` / `CAPIError 400` | Model-side hiccup, **not** your setup | Retry the prompt; if it persists, switch the model in the picker |
| Tools don't appear in Chat | Not in **Agent** mode, or (Rider) old plugin | Switch to Agent mode; update the JetBrains Copilot plugin to a 2026 build |

## Security (do not skip)

- The PAT is a password. **Never** commit it, paste it into a file in the repo, or send it in chat.
  VS Code's secret store (Step 3) and the OS env var (Rider) keep it out of the repo.
- If a token is ever exposed, **revoke it** in Azure DevOps and create a new one.
- The committed `validate-no-secrets` gate will fail the PR if a token lands in a tracked file —
  that's the safety net, not the plan.

---

<a id="confluence-setup"></a>
# Connect Copilot to Confluence — onehub-team

This one's for pulling pages out of your Confluence documentation space — a requirement, an LLD, a
checklist — or publishing notes back. This repository has exactly one Confluence connection:
the default **Confluence MCP**
server (`mcp-atlassian`). The CLI skill is not installed, so Copilot uses MCP without needing a
prompt hint. One-time setup per machine. The choice is explained in `ai/CONNECTIONS.md`.


## Step 1 — install the MCP runner

The server runs through **`uvx`**, which ships with Python's **`uv`**. If `uvx --version` fails,
install `uv` using your approved workstation package path, then restart the IDE.

## Step 2 — get a Confluence personal access token (Data Center)

1. Open `https://confluence.adnoc.ae` → avatar (top-right) → **Settings** → **Personal Access Tokens**.
2. **Create token** → name it `copilot-mcp`, set an expiry → **Create** → copy it.
   Data Center tokens carry your existing Confluence permissions.

## Step 3 — start the server

### VS Code (config already ships in this repo)

1. In VS Code, open `.vscode/mcp.json` and click **▶ Start** above the `confluence` server (or
   `Ctrl+Shift+P` → **MCP: List Servers** → `confluence` → Start).
2. When prompted for **`confluence_pat`**, paste the token. VS Code stores it in its encrypted secret
   store; it is never written to the repository.
3. In Agent mode, ask *"search Confluence for the OneHub AI checklist"*. Real results mean the
   connection works.

### Rider / other JetBrains IDEs

Rider cannot use VS Code's `${input:...}` secret. Set the server variables in the OS, fully restart
Rider, then run `/copilot-doctor`. The skill copies the Confluence command and safe defaults into
the root `.mcp.json` mirror while leaving the personal token to the inherited OS environment.

**PowerShell (Windows):**
```powershell
setx CONFLUENCE_URL "https://confluence.adnoc.ae"
setx CONFLUENCE_PERSONAL_TOKEN "<your-confluence-PAT>"
setx READ_ONLY_MODE "false"
```

**Terminal (macOS) — add to `~/.zshrc`, then restart Rider:**
```bash
export CONFLUENCE_URL="https://confluence.adnoc.ae"
export CONFLUENCE_PERSONAL_TOKEN="<your-confluence-PAT>"
export READ_ONLY_MODE="false"
```

**Terminal (Linux) — add to `~/.profile`, then sign out and back in:**
```bash
export CONFLUENCE_URL="https://confluence.adnoc.ae"
export CONFLUENCE_PERSONAL_TOKEN="<your-confluence-PAT>"
export READ_ONLY_MODE="false"
```

If Rider does not discover the repository file automatically, use **Copilot icon** → **Edit
Settings** → **Model Context Protocol** → **Configure** and open/import `.mcp.json`. Save and start
the `confluence` server.

The committed server starts with **`READ_ONLY_MODE=false`**, so reads and approved create/update
operations are available within the configured token's Confluence permissions. Set it to `true` and
restart the server when a local read-only session is required. Never put the token itself in
`.vscode/mcp.json`.

Security: the token is a password — never commit it or paste it into chat; revoke and rotate if exposed.
