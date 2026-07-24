---
description: 'Record a correction into the right instruction layer so the mistake never repeats. Run after the user corrects the agent, or when the same mistake happened twice.'
agent: 'agent'
---

# /selfimprove — record a correction

The model never learns by itself; **this repo learns through this procedure.** A correction that
isn't recorded here will be repeated in the next session.

## When to run

- The user corrected your approach (wrong API, wrong layer, wrong order, wrong convention).
- You caught yourself repeating a mistake a previous session already made.
- A review/CI failure revealed a rule that exists in someone's head but not in the repo.

## Inputs (gather from context; ask only if genuinely ambiguous)

1. **What went wrong** — the concrete mistake.
2. **What the correct behavior is** — the fix the user applied or expects.
3. **Scope** — which file types, workflows, or agents it affects.

## The layer model — pick where the rule belongs

| Layer | File | Use for |
|---|---|---|
| Team memory (default) | `.github/instructions/generic/project-learnings.instructions.md` | Cross-cutting corrections; anything that doesn't clearly fit below |
| Stack rules | `.github/instructions/generic/<stack>.instructions.md` | Rules scoped to a file type (auto-applied by glob) |
| Team-wide rules | `.github/copilot-instructions.md` (team-owned, optional) or `.github/instructions/team-local/repository.instructions.md` with `applyTo: "**"` | Repository-wide local conventions; do not edit the template-managed ADNOC standard for a team-only correction |
| Agent behavior | `.github/agents/<role>/*.agent.md` | A specific agent misbehaving (wrong verdict policy, wrong routing) |
| Procedure | `.github/prompts/<role>/*.prompt.md` | A step missing / wrong order in a runbook prompt |
| Procedural knowledge | `.github/skills/<role>/<name>/SKILL.md` | Multi-step know-how that should auto-trigger by description |

## Procedure

1. **Root-cause first.** One sentence: why did the wrong behavior happen? (Missing rule? Ambiguous
   rule? Rule in the wrong layer so it never loaded?)
2. **Classify** the correction into ONE primary layer using the table above. Default to
   `project-learnings` when unsure.
3. **Dedup check** — search the target file (and `project-learnings`) for an existing rule covering
   this. If found: **tighten that rule in place**; do not add a near-duplicate.
4. **Write the rule** in the form `Always X for Y` / `Never X when Y` — concrete trigger, concrete
   action. Include the failure symptom in a trailing clause when it helps recognition
   (e.g. "— otherwise the gate fails with `<error>`").
5. **Sweep the other layers.** If the same wrong assumption is hardcoded elsewhere (a prompt step,
   an agent rule, a skill), update those in the SAME change. Updating only `project-learnings`
   when a prompt also encodes the mistake is an incomplete fix.
6. **Verify**: re-read the edited files; run the gates —
   `node .github/ci-validators/validate-frontmatter.js && node .github/ci-validators/validate-skills.js`.
7. **Telemetry**: append one line to `ai/governance/agent-runs.jsonl` with `"agent": "selfimprove"`.
8. **Report**: list every file changed and quote each new/tightened rule.

## Registry maintenance (when evidence supports it, propose — don't silently do)

- **Add an agent** when a recurring task pattern (3+ occurrences) has no owning agent.
- **Add a prompt** when a multi-step routine has been executed ad-hoc 3+ times.
- **Modify** when scope is unclear, overlaps, or a delegation target changed.
- **Remove** when a rule's trigger no longer exists or an agent hasn't been used in months —
  dead config misleads more than it helps.

## Promotion paths — rules graduate (propose, human decides)

Rules mature in two directions; check both every time you record one:

1. **Cluster → extract.** When `project-learnings` accumulates **≥ 5 rules on one topic**
   (count them while deduping), propose extracting that cluster into its own
   `.github/instructions/<topic>.instructions.md` (if glob-scopable) or a
   `.github/skills/team-local/<topic>/SKILL.md` (if procedural). Slim the learnings entries to one
   pointer line — a 100-rule flat log stops being read.
2. **Team → standard.** When a rule is clearly **not specific to this repo** (it would be true in
   any ADNOC repo on this stack), flag it in your report as a **template candidate**: the champion
   opens a PR against `ai-sdlc-template` so all teams get it via `copier update`. If the CoE
   sees **2+ teams independently record the same rule, that's the fast-track signal** — promote it
   to the standard instead of letting every team rediscover it.

Before any promotion proposal, run the eval ladder in `ai/governance/how-to-eval-a-skill.md`
(at minimum Tier 1–2; Tier 3–4 with its pass@3 / pass^3 bars for anything going to the
shared template).

## Hard rules

- Never write a vague rule ("be careful with X") — it will be ignored, by you.
- Never duplicate a rule across layers — one primary home, others reference it.
- This procedure edits **Ring-3 / team-owned** files; it must never touch template-managed
  (Ring-2) files — those change via PRs to the template repo.
