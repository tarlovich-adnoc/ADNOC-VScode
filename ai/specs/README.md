# `ai/specs/` — Spec-Driven Development workspace

This folder is where **GitHub Spec Kit** writes feature specifications, plans, and task
breakdowns. It's the upstream half of our spec-driven delivery pipeline.

> **What ships vs. what's optional — read this first.** This template ships the `ai/specs/`
> workspace + `_template/`. The `/speckit.*` commands come from **GitHub Spec Kit itself** —
> install it separately; `use_spec_kit` creates this workspace, it does not vendor Spec Kit. The
> downstream orchestrators named below — `/spec-to-impl`, `/pr-review`, `/chained-spec-to-impl`
> and the coder/tester/reviewer agents — are **optional patterns maintained by the CoE alongside
> the template**, **not** shipped into your `.github/`. Treat the pipeline diagram as
> the target shape; ask your champion to wire those in only if your team adopts them.

The full pipeline (Note: the `/spec-to-impl`, `/pr-review`, `/chained-spec-to-impl` steps are optional, not shipped by default):

```
User intent
    └─ /speckit.specify   ─► ai/specs/<feature>/spec.md       (the WHAT)
       /speckit.clarify   ─► resolves ambiguities in spec.md
       /speckit.plan      ─► ai/specs/<feature>/plan.md       (the HOW)
       /speckit.tasks     ─► ai/specs/<feature>/tasks.md      (the ORDER)
       /spec-to-impl       ─► coder → tester → reviewer (POC1 pattern)
       /pr-review          ─► adversarial PR review
                       │
                       └─► draft PR open in Azure Repos, linked to Boards work item
```

An end-to-end runner for this pipeline (`/chained-spec-to-impl`) exists as an **optional
CoE-maintained pattern** — it is NOT shipped into this repo. The shipped day-to-day entry point
is the `orchestrator` agent (human-gated plan approval).

## Why this matters

Spec-Driven Development is one of our advanced AI-assisted development practices — it moves
intent into a reviewable spec before any code is written, so the AI executes against a
clear contract instead of ad-hoc prompts.

It also gives the Refinement/Planning phase a concrete, auditable artifact. Without this
folder live, that whole phase leaves no spec trail behind.

## Layout

```
ai/specs/
├── README.md                         ← this file
├── _template/                        ← starting point Spec Kit copies from
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── <feature-slug>/                   ← created per feature by /speckit.specify
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── (optional: research/, contracts/, etc. — Spec Kit adds these as needed)
```

Feature slugs use `<NNN>-<short-name>` (e.g. `001-user-export`, `002-payment-retry`) — Spec
Kit auto-generates the NNN prefix in order, giving a chronological audit trail.

## Workflow per feature

### 1. `/speckit.specify`
Co-create the spec with Copilot through structured dialogue. Output: `spec.md` with
numbered requirements, acceptance criteria, edge cases, non-functional requirements.

### 2. `/speckit.clarify`
Spec Kit re-reads `spec.md`, surfaces ambiguities, asks the user one focused Q at a time.
Updates spec.md in place. Repeat until no ambiguities remain.

### 3. `/speckit.plan`
Generate the implementation plan. Output: `plan.md` with:
- Architecture decisions
- File-by-file change list
- Risks and mitigations
- Definition of done

**Commit `spec.md` + `plan.md` to git here**, before any code is written. This commit is
the audit trail — it proves the spec preceded the code.

### 4. `/speckit.tasks`
Break the plan into ordered, dependency-aware tasks. Output: `tasks.md`.

### 5. `/spec-to-impl ai/specs/<feature>/spec.md`
Hand off to our multi-agent orchestrator (POC1 pattern):
- `coder` agent — implements one task at a time
- `tester` agent — adds tests for each numbered requirement
- `reviewer` agent — adversarial gate, default BLOCK if anything is UNVERIFIED
- Bounded retry: max 3 rounds

### 6. Final
If reviewer APPROVES → push the branch, mark draft PR ready, run `/pr-review` for formal
PR review.

If reviewer BLOCKs after 3 rounds → do NOT bypass. Update the spec, re-enter the chain at
step 2 or 3.

## How the team uses it

- **Day-to-day:** pick the `orchestrator` agent in Copilot Chat and type `implement #<id>` — it picks up the spec from
  `ai/specs/` when one exists. (The one-command `/chained-spec-to-impl` runner is an optional
  CoE-maintained pattern, not shipped here.)
- **Sprint planning:** PM/BA runs `/speckit.specify` for each new story before dev pickup.
- **Refinement meetings:** open `spec.md` and walk through. Edits via PR.
- **Code review:** reviewer reads `plan.md` first to understand intent, then the diff.

## Audit-trail evidence

For audit / governance review:

- Every feature lives as a folder under `ai/specs/<NNN>-<name>/`
- `git log ai/specs/` shows the date-ordered timeline of spec → plan → tasks → implementation
- The first commit in each feature branch references the spec path
- `ai/governance/agent-runs.jsonl` has telemetry lines tagged
  `workflow=chained-spec-to-impl` for each end-to-end run (only where the team adopted the
  optional runner; the shipped default logs `agent=orchestrator` runs instead)

Quantifiable per feature:
- Time from `/speckit.specify` to `/pr-review` APPROVE
- Number of clarify rounds (signal of spec quality at first draft)
- Number of `/spec-to-impl` retry rounds (signal of plan quality)
- Per-agent cost from `agent-runs.jsonl`

These are real numbers — paste them into the AI Adoption metrics evidence alongside dollar-cost from
`ai/governance/dashboard.py`.

## Anti-patterns to avoid

- **Editing `spec.md` directly without running clarify** — bypasses the discipline; a reviewer
  asks "where's the clarification trail?"
- **Skipping the spec commit before implementation** — the audit trail breaks; the spec
  could have been retrofitted after the code, which is the opposite of spec-driven
- **Running `/spec-to-impl` on a spec with TBD markers** — guarantees reviewer BLOCK at
  round 1; wastes a retry budget
- **Manual coding without going through the chain at all** — fine for tiny tweaks, but
  the feature won't have a spec trail behind it

## What we DON'T put in `ai/specs/`

- ADRs (those live in `docs/architecture/`)
- Onboarding docs (Confluence or repo `README.md`)
- API reference (auto-generated from OpenAPI)
- Meeting notes (Boards work item discussion section)

`ai/specs/` is **forward-looking, feature-specific specifications** only.
