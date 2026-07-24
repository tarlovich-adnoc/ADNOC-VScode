# How Copilot reaches your tools — MCP vs CLI, in plain words

Copilot already does a lot with just the files in this repo. But some jobs need it to reach *out* — to
your Azure DevOps board, your Confluence pages, your Figma designs. There are two ways it does that.
You never have to memorise this, but when someone asks "is that MCP or CLI, and which should I use?",
here's the honest, plain answer.

## The two ways, and the one difference that matters

**An MCP server** is a small always-on connector. The canonical repository setup lives in
`.vscode/mcp.json`; `copilot-doctor` creates a secret-safe root `.mcp.json` mirror for Rider users.
Once connected, its tools sit in Copilot's toolbox in *every* chat — it can reach the service any
time, no extra steps. The catch:
"always on" means its list of tools takes up a slice of the model's attention on every request, whether
you use it that day or not. (Copilot can only keep so much in mind at once — picture open browser tabs:
each is handy, but they all quietly use memory even when you're not looking at them.)

**A CLI skill** is the opposite. It's a *skill* — background know-how that knows how to drive a
command-line tool — and it stays completely out of the way until your question actually needs it. Then
it loads, runs the command, and steps back. It costs nothing when you're not using it. The trade-off:
under the hood it's a shell command, so it shines for occasional, on-demand reads rather than fast
back-and-forth.

So the one thing to hold onto: **MCP is always there and richest, but always takes up room; CLI is lean
and shows up only when needed, best for now-and-then.** Neither is "better" — they suit different
rhythms of work.

## Which of your tools uses which — and why

| Tool | How you reach it here | Why it's set up that way |
|---|---|---|
| **Azure DevOps** | **MCP** by default (`azure-devops`), plus a lean **CLI** skill (`ado-work-items`) | You touch the board constantly, so an always-on connector earns its keep. The CLI skill covers quick one-off reads — and lets a team turn the MCP off to reclaim context if they measure it's worth it. |
| **Confluence** | **MCP** by default; **CLI replacement** only with `use_confluence_cli: true` | A repository gets exactly one route, so Copilot cannot choose unpredictably between MCP and shell commands. Choose CLI only when the team deliberately prefers its on-demand context profile. |
| **Figma** | **MCP** (`figma`, designer/Figma teams only) | Comparing a design to the built page needs the live Dev Mode connection — there's no CLI equivalent. |

## "So how do I choose?"

Most of the time, **you don't** — and that's the point. You ask in plain words ("show me work item 1234",
"pull the LLD from Confluence", "compare this Figma frame to the login page") and Copilot uses whatever's
wired up. Each skill describes itself well enough that the right one fires on its own.

The real choice happens **once, at the repo level**, not per request:

- **Default:** keep Confluence MCP. It is the tested route and requires no prompt hint.
- **Measured CLI preference:** answer Yes to `use_confluence_cli`. That removes the Confluence MCP and
  installs the `confluence` skill instead; it never enables both. The `ado-work-items` skill separately
  documents a measured lean mode for Azure DevOps.

To see what *this* repo has switched on, open **`.vscode/mcp.json`** — every server listed there is an
active MCP connection. Rider's `.mcp.json` should contain the same servers with VS Code-only secret
inputs removed. Yours includes the **Confluence MCP** and omits the CLI skill (write-capable by default, within the permissions of the configured Confluence token). It also includes the **Figma** MCP.

## By role — what you'll actually touch

- **Developer / QA** — the **Azure DevOps** connection, for tickets and PRs. MCP by default; the CLI skill
  handles quick reads.
- **BA / PM** — mostly **Confluence**, for requirements, LLDs and KB pages. The Copier answer decides
  the one connection at repository level; either way you ask in plain words and never add a per-prompt
  "use MCP" or "use CLI" hint.
- **DevOps** — **Azure DevOps**, for standing up repos, pipelines and branch policies. That work runs
  through a PAT-authenticated **CLI** (`az` / REST scripts you run) plus the board MCP for reads — the MCP
  can't provision, so a human always applies the change.
- **Designer** — **Figma** (MCP), to check the built page against the design. Nothing to choose here
  (Figma is MCP-only) and nothing to do with the board; your setup steps are in the Designer section of
  `BY-ROLE.md`.

Setup for Azure DevOps and Confluence is in **`SETUP-COPILOT.md`**; the Figma connection is in the
Designer section of **`BY-ROLE.md`**. What each tool actually *does* for your role is in **`BY-ROLE.md`** too.
