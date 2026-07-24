# How to use the AI workflow in onehub-team

This repo comes pre-wired for GitHub Copilot by the ADNOC standard — the agents, prompts, and
rules your team needs are already sitting in the `.github/` folder. You don't set any of that up.
Read this page once and you'll know how to get real work done here.

> **Not a developer?** You don't need to be. Whatever you do — business analysis, QA, project
> management, DevOps, design — there's a section written for your role in
> **[BY-ROLE.md](BY-ROLE.md)**. Open it, find your role, and you'll see the exact tools and the
> everyday jobs they're for.

## Two ways to ask, and one thing that just happens

Everything happens in the **Copilot Chat** panel, switched to **Agent mode** — there's a mode
selector at the top of the chat box. Once you're there, you have two ways to hand off a task, plus
one thing that takes care of itself:

- **Agents** are specialists you pick from the **dropdown at the bottom of the chat box**, then
  type your task in plain English. In VS Code and Rider that dropdown is how you choose one — you
  don't type its name with an `@`. So when you see **`[agent] orchestrator`** below, it means: open
  the dropdown, pick `orchestrator`, then type what you want. (Visual Studio is the odd one out —
  there you *can* type `@orchestrator` directly.)
- **Prompts** are the ones that start with `/`. You just type them straight into the chat, like
  `/fix-bug`. Think of a prompt as a saved recipe for a routine job.
- **Skills** mostly run themselves. They switch on when the topic comes up — open a React file and the
  React skill quietly loads its rules — so you usually just work and the right knowledge shows up. If you
  ever want to fire one on purpose, it's also there as a `/name` slash command, right next to the prompts.

## The one rule to remember

For anything bigger than a one-liner, start by opening Copilot Chat in Agent mode and writing what
you want in plain English. For the routine parts of the job, reach for the `/` prompts in the
cheat-sheet at the end of this page.


## The handful of moves that cover most days

**Something feels off?** Before anything else, type **`/copilot-doctor`**. It runs a ~30-second
local health check — are the rules loading, are the validators in place — and inventories the active
MCP servers. It then gives you copy-ready prompts to test those connections in a new Agent-mode
message. Run it on day one, and any time Copilot "can't see" a ticket or a file.

**Starting from a ticket?** Type **`/ado-intake #1234`**. It pulls that Azure Boards work item —
title, description, acceptance criteria, links — into a tidy `intake.md` under `ai/plans/`, so you're
never building on a half-remembered ticket.

**Chasing a bug?** Type **`/fix-bug`** and describe it, e.g. *login button does nothing*. It won't
guess-patch: first it writes the smallest test that fails for exactly the reason you reported, shows
you the red, finds the real cause, makes the smallest fix, and re-runs until it's green. If it can't
reproduce your bug, it stops and asks for more — which is the honest answer, not a fake fix.

**About to open a PR?** Pick **`code-reviewer`** from the dropdown and say *review my diff*. You get
a fast, honest read — correctness first, then security, then maintainability — before a human ever
looks. It only advises; it doesn't touch your code.

**Ready to ship it?** Type **`/git-deliver`**. It delivers the team way: makes a feature branch,
stages just what changed, writes a commit linked to your work item, pushes, and opens a **draft**
pull request. It will never push to `main`.

If your team has one of the role packs — QA, BA, PM, DevOps, or Designer — you'll have a few more
prompts and agents built for that work. They're in the cheat-sheet below and explained in
**[BY-ROLE.md](BY-ROLE.md)**.

## Teaching the repo when it gets something wrong

Here's the part that matters most: the model itself never remembers your corrections between chats —
but **this repo can.** When you correct the agent and it's the kind of thing that'll come up again,
say **"add this as a project learning"** or run **`/selfimprove`**. It writes a plain `Always X for Y`
rule into `project-learnings.instructions.md`, and from then on every chat picks that rule up
automatically. Fixing the same mistake twice without recording it is the one habit to avoid.

## Your first day (once per person)

> **You'll need a Copilot seat first.** That's a GitHub Copilot Business or Enterprise seat assigned
> to you. If Copilot Chat won't sign in or says you have no entitlement, ask your CoE or admin for a
> seat before going any further.

1. Run `git pull`, open the **Copilot Chat** panel, and switch it to **Agent mode** with the
   selector at the top — that's where all of this lives, and your agents appear in the dropdown at
   the bottom. While you're there, check Node with `node -v`; if nothing prints, install Node LTS,
   because the Azure DevOps connector needs it.
2. Connect Copilot to **Azure DevOps and Confluence** by following **`SETUP-COPILOT.md`** (about
   5 minutes — it walks you through both). ADNOC signs in to Azure DevOps with a **Personal Access
   Token**, not `az login` (that's blocked here). In VS Code, click ▶ Start in `.vscode/mcp.json`
   and paste the token when it asks. In Rider, set the OS variable and run `/copilot-doctor`; it
   creates the secret-safe root `.mcp.json` mirror. The guide has both paths.
3. On **Rider**, make sure the GitHub Copilot plugin is a **2026 build** (Settings → Plugins) —
   agents and the Azure DevOps connection need it.
4. Run **`/copilot-doctor`** in the chat, resolve every local failure, then use its copy-ready prompts
   to verify each active MCP connection with a real tool response.

> Best way to spend your first hour: the five short missions in **`ONBOARDING-QUEST.md`**. Stuck on
> anything? **`FAQ.md`** has you covered.

## A few hard rules

These aren't style preferences — the CI gate and the rest of the team depend on them:

- **Never push to `main`.** Work on a feature branch and open a PR; the AI-workflow gate (6
  validators) has to pass.
- **Link every commit to its work item**, like `feat: add export retry #1234`.
- **Don't hand-edit the files the template manages** — `.github/agents/generic/code-reviewer.agent.md`,
  the validators, `.vscode/mcp.json`. Your own changes go in a `team-local/` folder, or as a PR to
  the template repo.
- **Set the AI Usage field** on Boards items that used AI (`AI-primary` or `AI-assisted`), as you
  finish them, not weeks later. Where that field isn't available, a tag with the same name is the
  fallback.
- **Never run `copier copy --overwrite` here.** Updates arrive through `copier update` on a branch.

## Quick reference

The moves above in one place — `/` you type, `[agent]` you pick from the dropdown then type your task:

```text
/copilot-doctor                         ← local health check + MCP verification guide, run this FIRST
/ado-intake #1234                       ← just pull the ticket into a structured intake file
/fix-bug login button does nothing      ← reproduce-first bug fix discipline
[agent] code-reviewer → review my diff  ← advisory review before you open the PR
/git-deliver                            ← branch · commit linked to #id · push · draft PR
/selfimprove                            ← the agent was wrong and you corrected it? record the rule
[agent] checklist-confluence → checklist for #123  ← QA: feature requirements → checklist → Confluence
[agent] checklist-ado          ← QA: that checklist → Azure DevOps test cases
[agent] figma-ui-comparator → compare Figma to /route  ← Designer: design-to-implementation gap report
/transcript-to-backlog                  ← BA: meeting transcript → draft backlog items
[agent] diagrammer → create a sequence diagram  ← BA: Mermaid/Lucidchart diagram assistant
[agent] ba-ado-ticket-structure → tickets under epic #123  ← BA: Epic → Feature/Story/Task in ADO
/incident-response                      ← sev1/sev2 triage companion
```

And where everything lives, if you go looking:

| What | Where |
|---|---|
| ADNOC house rules (`applyTo: "**"`) | `.github/instructions/generic/adnoc-standard.instructions.md` |
| Auto-applied per-file-type rules | `.github/instructions/**/*.instructions.md` |
| **The team's learned corrections** | `.github/instructions/generic/project-learnings.instructions.md` |
| Agents (pick from the dropdown in Chat) | `.github/agents/` |
| Prompts (type in Chat with `/`) | `.github/prompts/` |
| Skills (switch on by themselves) | `.github/skills/` |
| **How Copilot reaches ADO / Confluence / Figma** (MCP vs CLI, and why) | `ai/CONNECTIONS.md` |
| Feature specs (Spec-Driven Dev) | `ai/specs/` |
| Cost / usage telemetry | `ai/governance/agent-runs.jsonl` + `ai/governance/dashboard.py` |
| **Your team's own additions** | `.github/prompts/team-local/`, `.github/skills/team-local/`, `.github/agents/team-local/`, `.github/instructions/team-local/` |
