# Onboarding quest — onehub-team (45 minutes day one + one graduate mission in week 1)

Welcome to the onehub-team AI workflow. This is a quick, hands-on tour — five short missions
today, plus one graduate mission to finish in your first week. Do them in order; each takes a few
minutes and leaves you able to do something real. When missions 1–5 are ticked off, post
"quest done" in your team channel so your champion knows you're up and running. Mission 6 is due
sometime this week.

One thing up front: everything here happens in **Copilot Chat**, right inside this repo. There's no
new app to install — the whole workflow is just files in the project you cloned, so you already have it.

## Mission 1 — Power up (≈10 min)

Let's get your tools talking to each other. Nothing exotic — a pull, a mode switch, and one connection
to Azure DevOps.

- [ ] `git pull` — the whole AI workflow is just files in this repo, so a pull means every agent, prompt, and skill is already on your machine.
- [ ] **Open Copilot Chat and switch it to Agent mode** — the mode selector sits at the top of the chat box. Once you're in Agent mode, a **dropdown** appears at the bottom; that's where you'll pick agents in a minute. (While you're here, check Node: run `node -v`. If nothing prints, install Node LTS — the Azure DevOps connector needs it.)
- [ ] **Connect the services your role needs — follow `SETUP-COPILOT.md`** (Azure DevOps and/or Confluence; your `ai/BY-ROLE.md` section says which — a BA leans on Confluence, say, while a designer wants Figma instead).
      ADNOC signs in to the Azure DevOps connector with a Personal Access Token — a PAT, a long
      string you generate once (plain `az login` is blocked here, so don't reach for it). VS Code:
      hit ▶ Start in `.vscode/mcp.json` and paste the token. Rider: set the OS variable, then let
      `copilot-doctor` create the secret-safe root `.mcp.json` mirror.
- [ ] Rider only: check the Copilot plugin is a **2026 build** (Settings → Plugins).
- [ ] In Copilot Chat, type **`/copilot-doctor`** — a *skill* that runs deterministic local checks and repairs in about 30 seconds. Fix anything it flags, then use its copy-ready prompts to verify each active MCP connection with a real tool response.

## Mission 2 — Read the map (≈5 min)

Five minutes of reading now saves you an hour of guessing later. Skim these three, honestly.

- [ ] Read `HOW_TO_USE.md` — one page, the big picture.
- [ ] **Open `ai/BY-ROLE.md` and read your role's section** — your tools and your first real jobs (BA / QA / PM / DevOps / Designer / Developer). This is the one page that's actually about you.
- [ ] Open `.github/skills/` and name which skills **your stack** got (dotnet). A *skill* is know-how that switches itself on when your question touches its topic — you usually don't call it by name (it just fires), though it's also available as a `/name` slash command if you want to run it deliberately.
- [ ] Optionally, browse the **[AI Tools Catalog](https://adno-dib.git.pages.epam.com/adno-dib/)** for
      the full index of ADNOC-wide tools *(EPAM VPN required;
      [static snapshot](https://git.epam.com/adno-dib/adno-dib/-/raw/main/pages/index.html?inline=false) if offline)*.
- [ ] Open `.github/instructions/generic/adnoc-standard.instructions.md` — these are the
      template-managed ADNOC house rules. If this brownfield repo also has
      `.github/copilot-instructions.md`, that repository-wide file remains team-owned.
- [ ] Open `.github/instructions/generic/project-learnings.instructions.md` — this is the team's
      shared memory, where every lesson anyone teaches the repo lands. You'll add your own line in
      Mission 4.

## Mission 3 — First flight (≈15 min)

Time to actually fly. Pick a small, real work item and watch the workflow do a lap.

- [ ] Run `/ado-intake #<id>` on any small work item and read the intake file it writes —
      a clean, structured brief beats a half-remembered ticket every time.

- [ ] Now open the dropdown, pick `code-reviewer`, and type `review my current diff` on any change you
      have lying around. Notice its verdict is **advisory** — a second pair of eyes, not the
      gatekeeper: Branch Policies and a human approver still decide what merges.

> **Not a coding role?** The two steps above assume app code. Do **your** role's first flight instead — one is enough. Full details in `ai/BY-ROLE.md`:
- [ ] **BA:** type `/transcript-to-backlog`, paste a short meeting snippet (strip names and anything sensitive first — it goes to the Copilot service), and read the backlog items it ACCEPTed plus the still-open list.
- [ ] **QA:** open the dropdown, pick `checklist-confluence`, point it at one small feature's requirements, and read the QA checklist it drafts — you approve before it publishes to Confluence.
- [ ] **DevOps:** type `/bootstrap-repo` with a throwaway repo name and **read** the script and runbook it generates — do NOT run it yet.
- [ ] **Designer:** pick `figma-ui-comparator`, paste one Figma frame URL plus a page name, and read its report on what matches the design and what drifted.


## Mission 4 — Teach it (≈10 min)

This is the part that makes the workflow yours. When an agent does something that doesn't fit how this
team actually works, you correct it once — and it stays corrected, for everyone.

- [ ] Spot one thing the agent gets wrong for this team — a naming convention, a library it reaches
      for that you don't use, a step in the wrong order. Fix it right there in chat, then run
      **`/selfimprove`** to bank the lesson.
- [ ] Open `project-learnings.instructions.md` and confirm your `Always X for Y` rule is written down.
- [ ] Commit it on your current task branch — or ship it with `/git-deliver` alongside your Mission-3
      work item. Never straight to main. From now on every session — yours and your teammates' —
      already knows your rule. Fixing the same mistake twice without recording it is the one habit
      to avoid.

## Mission 5 — Leave a trace (≈5 min)

Last quick one — let's watch the workflow keep its own books.

- [ ] Check `ai/governance/agent-runs.jsonl` — your Mission 3 and 4 runs should have appended a line
      or two of telemetry. (No such file at all? Then nothing self-reported — telemetry is an
      instruction the agents are asked to follow, not a guarantee. Rerun a prompt, look again, and
      flag it to your champion.)
- [ ] Run `python ai/governance/dashboard.py` and find your own runs in the rollup. (No Python on the
      box? Just open `agent-runs.jsonl` and find your lines by hand — the dashboard is a convenience,
      not a requirement.)
- [ ] When your work item completes, set its AI Usage field to `AI-assisted` in Boards — or `AI-primary` if AI authored the bulk. Record it as you go; it's forward-only, so there's no backfilling later.

---

**Done?** Post "quest done". You now know how to check your setup (`/copilot-doctor`), how to get real
work done (`/fix-bug`, `/git-deliver`), how to teach the repo something
new (`/selfimprove`), and how your usage gets measured (telemetry → the dashboard). That's the whole
system — the rest is practice.

## Mission 6 — Build your own (graduate level, ≈25 min, within week 1)

So far you've been using the standard. This mission is where you start growing it. You'll build one of
each — a custom instruction, skill, and agent — in your team's own zone, a corner of the repo template
updates can never overwrite. It's the same move the whole standard was built from.

Three quick checks before you create anything: **(1) names** — never reuse a template file's name
(`git ls-files .github | Select-String <name>` to check — `grep` on macOS/Linux), and don't collide
with a teammate's quest artifacts; if one already exists, extend it instead. **(2) topics** — make
sure your idea isn't already covered by a shipped skill (a "react tips" skill sitting next to
`react-patterns` just creates two voices giving contradictory always-on advice). **(3) review** — your
Mission-6 PR goes to your team champion, who's allowed to prune practice artifacts that aren't
genuinely pulling their weight.

- [ ] **Instruction** — rules that apply automatically by file mask. Create
      `.github/instructions/team-local/team-conventions.instructions.md`:

      ```markdown
      ---
      description: 'onehub-team project conventions auto-applied to source files.'
      applyTo: "src/**"
      ---
      - Always <one REAL convention your team has that the standard doesn't cover>.
      ```

      Verify: open a matching file, ask Copilot Chat *"which instruction files apply here?"* —
      yours must be in the list (also visible in the response's References).

- [ ] **Skill** — know-how that triggers itself. Create
      `.github/skills/team-local/<topic>/SKILL.md`, on a topic you genuinely know cold
      (a deploy quirk, a fiddly integration):

      ```markdown
      ---
      name: <topic>
      description: <What it does>. Use when the user <does the concrete task — these
        trigger phrases decide whether it ever fires>.
      ---
      # <Topic>
      <the know-how, with one good/bad example>
      ```

      Verify like a pro (a mini Tier-2 check from `ai/governance/how-to-eval-a-skill.md`): ask a
      question that SHOULD trigger it (skill appears in References), one **adjacent** question — same
      domain, different task — that SHOULDN'T (this catches an over-broad description), and one
      off-topic one (it stays silent). A skill that fires on everything is worse than no skill.

- [ ] **Agent** — a role you hand work to. Create `.github/agents/team-local/release-notes-writer.agent.md`
      — or, if a teammate already built that one, any small role nobody's built yet:

      ```markdown
      ---
      name: release-notes-writer
      description: Drafts release notes from merged commits since the last tag. Use before a release.
      tools: ['search/codebase', 'execute/runInTerminal', 'edit/editFiles']
      ---
      # release-notes-writer
      Run `git log "$(git describe --tags --abbrev=0)..HEAD" --oneline --no-merges` to collect
      the changes (quotes matter in PowerShell; no tags yet → use the full history instead),
      group by feature/fix, draft notes in the team's tone. Never invent changes —
      quote commit subjects. Append one telemetry line per run to `ai/governance/agent-runs.jsonl`.
      ```

      Verify: open the agents dropdown in Copilot Chat — your agent is in the picker; run it once.

- [ ] **Gate it and ship it:** run `/copilot-doctor` (it dry-runs all six validators) → green →
      deliver with `/git-deliver`, and set your **champion as the PR reviewer**. Your teammates
      get all three the moment your PR lands.

**Why this matters:** everything in this repo's standard started life as someone's Ring-3 file — a
local experiment in a team's own zone. If yours earns its keep over a sprint, the bottom-up path
(the FAQ answers "how does my work get into the standard?") can carry it all the way to every team.
The cookbook in the template repo's `HANDBOOK.md` (recipes 1–6) walks through each variant.
