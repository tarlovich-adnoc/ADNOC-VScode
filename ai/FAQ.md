# FAQ — the questions everyone asks in week one

When something doesn't work, your first move is almost always the same: open Copilot Chat and type **`/copilot-doctor`**. It runs about thirty seconds of checks — sign-in, the Azure DevOps connection, whether Copilot can actually see your agents and prompts — and tells you exactly what's off. Nine times out of ten it either fixes the thing or names it. Start there, then come back here.

**Q: Do we really need Copier? Couldn't you just hand us the files once and be done?**

You only meet Copier twice, honestly. Copier is a small tool that stamps the standard into your repo — you answer a short questionnaire once (about two minutes, when the repo is born), and after that you run `/copier-update` maybe once a month to pull in improvements. The rest of the time it's invisible: your repo is just plain files and you work exactly as you always have. If we handed you the files once instead, you'd get the same starting point but lose the pipe — no fixes flowing back, no picking up what another team already figured out, no promise your own customizations survive. That's how you end up with twenty slightly different versions of the same setup, which is the mess we're avoiding. So think of Copier as the courier, not something you operate: improvements show up as a pull request — a proposed change your team reads and approves before anything lands — and your own `team-local/` and `skills/team-local/` files are never touched. If you've used NuGet or npm, it's that, but for your Copilot setup.

**Q: If we adopt the template, is it going to stomp on our existing repo?**

No. Your `src/`, your tests, your `README` — never touched. The only place anything can collide is inside `.github/`, and only when a file has the exact same name as one the template ships. The template does not ship `.github/copilot-instructions.md`, so existing repository-wide Copilot guidance stays unchanged; ADNOC's standard arrives separately at `.github/instructions/generic/adnoc-standard.instructions.md`. Even for other paths, you adopt on a branch, so every change is visible in the pull-request diff before you merge it. Anything of yours in a Ring-3 path — `team-local/`, `skills/team-local/`, `project-learnings` — is skipped automatically. Run `/migrate-to-standard` on that adoption branch and it sorts every pre-existing file into "duplicate / yours / conflict" and writes you a plain migration plan. Nothing is ever deleted out from under you — your old version of any file is always one `git show main:<path>` away.

**Q: Can the central team push a change straight into my repo without asking?**

No, and that's on purpose. Every update arrives as a pull request your team reviews and merges — the last click is always yours. (If a repo is being wound down and you'd rather not see the nagging, `auto_skip_updates: true` in your answers file turns updates off for it.) "Central team" here means the CoE, the Center of Excellence — the small group that looks after the standard for everyone.

**Q: How do I move to a new template version — and back out if it goes wrong?**

Moving up: type `/copier-update`. It safely parks tracked and untracked unfinished work, updates on an isolated branch, commits the template changes, and restores your work. If restoration conflicts, it keeps the recovery stash and tells you exactly where it is. Review the diff, then merge the pull request. Backing out: Copier only ever moves forward, so there's no "undo" button — you just `git revert` the update commit in your own repo, the same as any other change. It's entirely local; no other team feels it.

**Q: `copier copy` is complaining that "Local template must be a directory" — what did I do?**

You gave it a plain URL and Copier tried to read it as a folder on disk. Put `git+` in front and it clicks into place: `git+https://dev.azure.com/<org>/<project>/_git/ai-sdlc-template`. That one prefix is almost always the whole fix.

**Q: Why is `--overwrite` off-limits?**

Because it lets Copier quietly replace same-named files with no diff to look at — exactly the silent stomp we just promised wouldn't happen. There's one sanctioned exception: a throwaway adoption branch, where `git diff` shows you everything anyway. Never on `main`, and never as a "just force it" fix for a messy update.

**Q: Copilot can't see our agents or prompts — especially in Rider. Now what?**

First, `/copilot-doctor` — it checks this exact thing. If you're in Rider, make sure you're on a 2026 Copilot plugin build; older ones simply don't show custom agents and prompts at all. In VS Code the repo already ships a `.vscode/settings.json` that pins instruction-file loading on, so it should just work. And a quick reminder on how these show up once they're visible: an agent you pick from the dropdown at the bottom of the chat box (you don't type its name), a prompt you invoke by typing its `/name` into chat, and a skill fires on its own the moment your request matches its topic (and if you want, you can also run it deliberately by typing its `/name`).

**Q: Confluence access is failing.**

This repository uses the default Confluence MCP. Open `.vscode/mcp.json`, confirm the `confluence` server is running, and re-enter `confluence_pat` through VS Code's secret prompt if authentication expired. Also confirm `uvx --version` works. The complete walkthrough is in the Confluence section of `SETUP-COPILOT.md`; run `/copilot-doctor` first.

**Q: Copilot won't sign in — it says I have no access.**

That's almost always a licensing thing, not a setup thing. You need a GitHub Copilot Business or Enterprise seat assigned to your account. If sign-in shows no entitlement, ask your CoE or admin to assign you one — it's an org-level step that has to happen before any of the rest of this works.

**Q: Remind me — what are Ring 1, 2, and 3?**

It's just how we label who owns what. Ring 1 is mandatory and always comes from the template — you get it, you don't edit it. Ring 2 is the stuff the template asks you about, where your answers decide the outcome; those answers live in `.copier-answers.yml`, which is basically your repo's passport. Ring 3 is yours forever, and updates never reach into it — that's `team-local/`, `skills/team-local/`, and `project-learnings`.

**Q: I want to add my own prompt or skill — how do I do that without breaking updates?**

Put it in Ring 3, which exists for exactly this: drop a prompt into `.github/prompts/team-local/` or a skill into `.github/skills/team-local/`. Those folders are yours and updates skip right over them. The one thing not to do is hand-edit a template-managed file — that's a guaranteed merge conflict the next time you update.

**Q: Our team-local skill turned out great. How do we get it into the standard so everyone has it?**

Nice — that's exactly the path we want. Roughly four steps. One: prove it — run it in Ring 3 (`team-local/` or `skills/team-local/`) for at least a sprint of real work. Two: clone the template repo, make a branch, move the file under `template/…` (strip out anything specific to your team), and open a pull request against the template. Three: the CoE reviews it with a few honest questions — is this universal or should it be opt-in behind a `copier.yml` question, does it duplicate something already shipped, is it worth an eval? Four: once it merges and gets a new tag, every team picks it up with an ordinary `copier update` — and you delete your local copy in that same update PR. Shortcut: when two or more teams record the same learning, it shows up on the CoE's learnings-radar as a promotion candidate all on its own, so sometimes you don't even have to ask.

**Q: The agent keeps making the same mistake. How do I make it stop?**

Correct it once, then either say "add this as a project learning" or run `/selfimprove`. Either way the rule gets written into `project-learnings.instructions.md` and quietly applies in every session after that — the model doesn't remember on its own, so this is how the repo remembers for it. And if the rule would be true for any ADNOC repo, not just yours, flag it: two teams recording the same rule fast-tracks it into the standard.

**Q: Where do the Spec Kit commands come from? I don't see them.**

Those (`/speckit.specify`, `/speckit.plan`, and the rest) come from GitHub Spec Kit, which is a separate install — the template doesn't ship the commands themselves, it ships the `ai/specs/` workspace they write into. `ai/specs/README.md` lays out what comes with the template versus what you install yourself.

**Q: What does the CI gate actually check on my pull request?**

Six quick automated checks, all plain Node with no dependencies: your frontmatter is shaped right, your skills honor their contract, there are no hard-coded personal paths, the MCP config is sane, the text is unicode-safe, and no secrets got committed. Passing them is the floor, not the ceiling — a green gate doesn't skip human review, and your Branch Policies still require a real approver.

**Q: Who's paying for all this AI, and how does it get tracked?**

Every agent run adds one line to `ai/governance/agent-runs.jsonl`, and `python ai/governance/dashboard.py` rolls those lines up per agent and per team so you can actually see the usage. Separately, as you finish Boards items, set the AI Usage field on them — `AI-primary` or `AI-assisted` — going forward; that's how the adoption numbers get counted.

**Q: There are a lot of models in the picker. Which one should I actually use?**

Short version: leave it on the default and get on with your work — that handles most of the day and costs the least. When you're running an agent on real feature work, bump it up to a stronger model. Save the heaviest (Opus-class) ones for a genuinely hard problem the normal model already failed at — then switch back, because the picker keeps using your last pick, and every chat turn spends from a budget the whole org shares. So: default for everyday, stronger for real work, heaviest only on purpose. Your remaining allowance is in Copilot's usage settings.

**Q: The Figma MCP server won't connect — the tools aren't showing up in Copilot.**

MCP is just the connector that lets Copilot reach an outside tool — here, Figma. Two things to check. Figma Desktop has to be running, and its server has to be switched on: **Figma → Preferences → Enable Dev Mode MCP Server**. It listens on `http://127.0.0.1:3845/mcp`; if that port is unreachable, quitting and reopening Figma Desktop usually clears it. The full walkthrough is on the KB: https://kb.epam.com/spaces/ADNO/pages/2790844955/Figma+Desktop+MCP.

**Q: Is there something more complete than this FAQ?**

Yes — `HANDBOOK.md`, at the root of the template repository (`ai-sdlc-template`). It's the full reference: every agent, prompt, and skill; how Copier works end to end; a thirty-recipe customization cookbook; and onboarding checklists for both individual developers and whole teams.

**Q: What other AI tools are available at ADNOC beyond the ones in this repo?**

See the **[AI Tools Catalog](https://adno-dib.git.pages.epam.com/adno-dib/)** (requires EPAM VPN)
for the full index of approved tools, agents, prompts, and skills across ADNOC. If you can't reach
it, the **[static snapshot](https://git.epam.com/adno-dib/adno-dib/-/raw/main/pages/index.html?inline=false)**
has the last committed copy.

**Q: What if my question isn't in here?**

Ask your team champion, who can carry it to the champion council channel. If the answer turns out to be useful for everyone, it becomes either a rule (via `/selfimprove`) or a new FAQ entry through a pull request to the template.
