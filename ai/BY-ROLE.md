# Your role in this repo — what you can get done, and how

This repo was set up from the ADNOC AI-workflow standard. Below is the toolkit for **your** role and
the real jobs you'll do with it. You only see the sections your team switched on when this repo was
created — if your role isn't here, ask your champion to enable its pack (a `copier update`).

New here? Do the one-time setup in **[SETUP-COPILOT.md](SETUP-COPILOT.md)**, then run the day-one
missions in **[ONBOARDING-QUEST.md](ONBOARDING-QUEST.md)**. **[HOW_TO_USE.md](HOW_TO_USE.md)** is the
daily one-pager once you're rolling.

**A few words you'll meet, before we start:**

- **Copilot Chat, Agent mode** — the Copilot chat panel, switched to "Agent" with the mode selector at
  the top of the chat box. Everything on this page happens there.
- **An agent** — a specialist you hand a whole task to. You pick it from the **agents dropdown** at the
  bottom of the chat box, then type what you want done. In VS Code and Rider you choose it from that
  dropdown — you do *not* type `@name` (that only works in Visual Studio).
- **A `/prompt`** — a ready-made routine you run by typing its name, like `/fix-bug`. Think of it as a
  saved recipe for a job you do often.
- **A skill** — background know-how that switches itself on when your request matches its topic. You
  usually don't call it by name — it just shows up when relevant — but it's also available as a `/name`
  slash command if you'd rather run it yourself.
- **MCP server** — a small local connector that lets Copilot read your Azure DevOps work items. Chat,
  the `/`-prompts and the skills all work **without** it; you only need it for live board access.
  (MCP vs the lean CLI path, and which tool uses which, is explained in `CONNECTIONS.md`.)
- **Pack** — the bundle of agents, prompts and skills for one role (BA, QA, PM, DevOps, Designer),
  switched on when this repo was created.
- **Ring 3 / team-local** — files your team owns. A `copier update` (the command that pulls in new
  versions of the standard) never overwrites them.

---

## Everyone: the Developer base

Every repo ships this — no pack required. It's the everyday loop: pick up a ticket, understand the
code, fix a bug, refactor, get a second opinion, and deliver work that traces back to an Azure Boards
item.

The one to reach for first on any real task is the **orchestrator** agent — pick it from the agents
dropdown, hand it a work-item number, and it runs the whole job end to end: pulls the ticket, writes a
short plan, **stops for your approval**, builds, gets the change reviewed, then delivers. It keeps its
plan in a file, so if your session crashes you don't lose the thread. Reach for it whenever a job
touches more than about three files; skip it for a one-line tweak or a quick question — just do those
directly.

When you only want a second pair of eyes on a change, pick the **code-reviewer** agent. It's read-only
— it reads your diff and tells you what's wrong, checking correctness first, then security, then
maintainability. Nothing gets edited; you get an honest verdict.

The rest are `/`-prompts you type when you want one specific job done well:

- Starting a ticket? Type **`/ado-intake`** with the work-item number and it pulls the item off the
  board into a tidy intake file, so you're planning from what the ticket actually says, not what you
  half-remember.
- Got a bug? **`/fix-bug`** keeps you honest: it writes a failing test that reproduces the problem
  first, finds the real cause, makes the smallest fix, runs the wider suite, and only then delivers.
  No guess-patches.
- Ready to ship? **`/git-deliver`** does it the team way — a feature branch, a commit linked to
  `#<id>`, a push, and a pull request. It never pushes to `main`.
- Reshaping code without changing what it does? **`/refactor`** proposes the change and its risks
  first, waits for your OK, then applies it and re-runs the tests.
- Staring at unfamiliar code? **`/explain`** walks you through it in layers — purpose, step by step,
  the types and side-effects, the gotchas — and never touches a thing.
- Just corrected the agent on something? Run **`/selfimprove`** right after, and it records the
  correction in the right place so the same mistake doesn't come back next session.
- Day one, or any time Copilot "can't see" something? **`/copilot-doctor`** runs a 30-second health
  check of the whole setup.

Some help arrives on its own. Ask Copilot to update the template, or type **`/copier-update`**, and
the updater preserves unfinished work while it refreshes the standard. As you write tests, the
**tdd-workflow** and **verify** skills drive the
test-first loop and run your stack's build/test gate; your stack's own **`<stack>`-patterns** skill (for
example `react-patterns` or `dotnet-patterns`) supplies its idiomatic patterns; and **ado-work-items**
reads board items when you ask. Confluence uses the configured **Confluence MCP** tools. You ask in plain words; Copilot uses
the repository's one selected connection.


---

## Business Analyst

You turn meetings, stakeholder docs and board items into requirements, backlog items, acceptance
criteria, diagrams and KB pages. One thing to know up front: meeting transcripts travel to the Copilot
service, so strip names and anything sensitive before you paste.

Say a two-hour refinement call just wrapped. Instead of typing up notes and hand-building the backlog,
strip the names, type **`/transcript-to-backlog`**, and paste the transcript. In one pass the
**ba-analyst** agent pulls out the requirements and drafts backlog items — quoting the line each one
came from, and labelling anything unstated as an ASSUMPTION or HYPOTHESIS — then the **req-validator**
agent scores each draft from 0 to 100 (clarity, testability, completeness, traceability) and sends the
weak ones back to be sharpened, up to three rounds. You get the items that passed plus a short list of
what's still open. You skim, accept what's right, and you're done.

When a stakeholder hands you a request document, run **`/review-request`**. It pressure-tests the
request the way a senior BA would and hands back an executive summary, a Scope / Out-of-scope /
To-be-decided table, the gaps and conflicts it found, draft acceptance criteria, and a prioritized list
of questions to send back (P0/P1/P2).

Two more prompts for the everyday: **`/feature-discovery`** runs an interactive scoping session — it
asks, you answer, and it structures the requirements as it goes; **`/meeting-notes`** turns a transcript
into clean minutes with owners and deadlines, and won't invent anything that wasn't said.

When it's time to put a feature **onto the board**, pick the **ba-ado-ticket-structure** agent. Give it
the parent Epic plus the feature and the stories, and it creates the whole Azure DevOps hierarchy —
Feature → User Story → Task — with the BA naming, Area/Iteration and field conventions applied for you.
It shows you the planned tree and **waits for your approval before it writes anything.** (There's also a
`/ba-ticket-structure` shortcut that collects the inputs and hands off to the same agent.)

Need a picture? Pick the **diagrammer** agent, describe what you want, and it asks a couple of
clarifying questions before handing you ready-to-paste Mermaid (or Lucidchart XML) for a flow, sequence
or ER diagram.

A lot of the BA work fires on its own as skills — just ask in plain words:

- "Convert this FSD section into testable requirements and Gherkin" → **user-stories-gherkin**.
- "Turn this problem statement into prioritized functional requirements" → **functional-requirements**
  (MoSCoW, MVP-first).
- "Create a KB article in Confluence for Feature <ID>" → **kb-documentation** drafts it, shows you a
  preview, and publishes only when you confirm.
- Mapping how features depend on each other, or finding every user story linked to a feature →
  **feature-dependency-mapper** and **feature-story-search**.
- Summarizing a grooming or stakeholder call → the **meeting-summary-** skills (grooming, plus short
  and full stakeholder versions).
- Sharpening a prompt you're about to reuse → **prompt-engineer**.

**Setup note:** your tools that write to Confluence use the repository's **Confluence MCP** connection in SETUP-COPILOT;
the ADO board connection is optional unless you pull work items.


---

## QA / Test Engineer

Your job here is **manual QA** — turning a feature's requirements into a checklist, running it, and
recording the result. (Test *automation* — Vividus / Playwright — is a separate track owned by the AQA
champion in its own repo; it is not part of this pack.) It works even on a repo with no application
code (`stack: none`) — manual QA is first-class here.

Your CORE tool is the **checklist-confluence** agent. Give it a feature — its requirements (a Confluence
page and/or an Azure Boards feature) and its design — and it drafts a QA **checklist** in the OneHub
form: a header with the Design / Requirements / Feature links, then a numbered table of verifications,
each with its expected result and a pass/fail column per platform. It flags gaps in the requirements as
it goes, shows you the draft, and — only when you approve — creates or updates the **Confluence** page
for it. You review every line; it never signs off for you.

When you want that same checklist recorded in **Azure DevOps**, pick the **checklist-ado**
agent: it turns each checklist row into a Test Case in a Test Plan / Suite you name, links them to the
Feature, and again waits for your approval before it writes anything.

> **The checklist format is provisional** — modelled on the current OneHub checklist convention, to be
> confirmed with the QA champion (Yuliya). If your team's checklist differs, just tell the agent the
> real shape and it adapts.

**Setup note:** the Confluence step uses the repository's Confluence MCP tools (see
`SETUP-COPILOT.md`); the Azure DevOps step needs the **test-plans** MCP domain (this pack turns it on)
and a PAT with **Work Items → Read & Write** — the read-only default in `SETUP-COPILOT.md` can't create
test cases.


---

## DevOps / Platform Engineer

This pack is for getting repos onto the standard and keeping the merge bar honest — creating repos,
registering pipelines, wiring secrets, setting branch policies. One thing to know first: the MCP
connector can't provision anything. These tools write you PAT-authenticated `az`/REST scripts and a
portal runbook that **you** run — they never touch Azure DevOps themselves.

Standing up a brand-new repo? Type **`/bootstrap-repo`** and you get a script plus a runbook that
creates the repo in Azure DevOps, applies this template, makes the first commit, and sets the standard
branch policies — you review it, then run it. Onboarding a messy existing repo instead? Pick the
**platform-engineer** agent; it takes a repo from "not on the standard" to "on standard, gated,
policied" as one ordered runbook with a verify step at the end.

Adding a CI gate that actually blocks bad merges is two moves: ask for the pipeline YAML (the
**pipeline-author** skill writes or edits it), commit it, then run **`/provision-pipeline`** to register
that file as a live, PR-gating pipeline and wire its variable groups and service connections. To set the
merge bar itself, **`/branch-policies`** generates the standard five-policy bundle on `main`. Behind
these, the **ado-provisioning** skill supplies the canonical `az`/REST recipes whenever you ask about
provisioning.

**Setup notes:**

- **To RUN the generated scripts you need a second, broader token** — a raw (not base64)
  `AZURE_DEVOPS_EXT_PAT` with **Project & Team → Manage**, **Build → Read & Execute**, **Code → Read &
  Write**, used via **`az devops login`** (never interactive `az login` — that's blocked here). The
  read-only MCP PAT from SETUP-COPILOT is *not* enough.
- The scripts write to a `provisioning/` folder — create it in the repo you're operating from if it's
  absent.


---

<a id="designer"></a>
## Designer

Your one job here is a good one: checking that what engineers actually built matches the Figma design,
down to the pixels.

Pick the **figma-ui-comparator** agent, paste the Figma frame URL, and tell it which page or route to
check. It compares the two and hands you a match-vs-differ table listing every mismatch — size, color,
spacing, typography — each with a clickable link to the exact source file to fix, and a recommendation
naming the precise token or CSS change. No live Figma at the moment? Give it an exported Dev-Mode spec
or an annotated screenshot and it carries on from that.

**Setup note (do this first):** the comparator needs a live Figma connection. Open Figma Desktop and
sign in to the account that can read the target design. Use **Figma → Preferences** on macOS or
**Main menu → Preferences** on Windows/Linux, then enable
**Dev Mode MCP Server** and confirm it uses `http://127.0.0.1:3845/mcp`. In VS Code, start `figma`
from `.vscode/mcp.json`. In Rider, run `/copilot-doctor` to create the root `.mcp.json`, then open
**Copilot icon → Edit Settings → Model Context Protocol → Configure**, import `.mcp.json`, and start
`figma`. The comparator also needs **the team's front-end code checked out in this repo** and the
page's route/name. You can **skip the Azure DevOps PAT** — your one tool doesn't use the board.

---

*Don't see your role above? Its pack wasn't enabled when this repo was created — ask your champion to turn on
`use_<role>_pack` (a `copier update`). Full daily reference: `HOW_TO_USE.md`.*
