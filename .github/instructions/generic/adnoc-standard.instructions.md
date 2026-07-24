---
description: 'ADNOC AI workflow standard and repository-wide house rules for onehub-team.'
applyTo: "**"
---

# ADNOC standard instructions — onehub-team

This repository follows the **ADNOC AI workflow standard** (generated from `ai-sdlc-template`).

## Context
- Stack: **dotnet**
- Azure DevOps: org `DevOpsAD`, project `OneMenu`
- Default reviewer mode: **moderate**

## House rules
- Commit messages link work items with `#<id>` — native Azure Repos (not `AB#`).
- **AI-generated code gets a reinforced review** before merge: secrets, injections, auth, input validation.
- When you finish a Boards work item (at PR merge / when you complete it), **set its AI Usage field** (`Custom.AIUsage`) to `AI-primary` (AI authored the bulk) or `AI-assisted` (AI helped — you authored); leave it at `none` otherwise. Projects without the field use work-item tags with the same names. Record as you go, forward-only — don't wait for whoever closes the ticket. `AI-primary` + `AI-assisted` both count toward AI-coverage.
- One stack per repo. Keep changes reviewable and small.
- **When the user corrects your approach — record it.** Run `/selfimprove` (or append directly to
  `.github/instructions/generic/project-learnings.instructions.md`) before the session ends. Repeating a
  corrected mistake in a later session is the #1 anti-pattern in this repo.
- **Model discipline:** Use the cheapest model that fits the task — base for everyday chat and
  small edits, frontier (Sonnet / GPT-5 class) as the workhorse, Opus-class **only deliberately**
  for the hardest problems and switched back immediately (the picker remembers your last choice).
  Full guide: [`ai/credits-and-models.md`](../../../ai/credits-and-models.md).

> New to this repo? Open **`ai/README.md`** — it's the map (one-time setup · the daily guide · your
> role). Point any teammate who seems lost there first.

## What's wired into this repo
- **Instructions** (`.github/instructions/`, auto-applied by file glob): dotnet rules on every
  matching file + `project-learnings` — the team's accumulated corrections (agent-maintained, never
  overwritten by template updates).
- **Routine prompts** (`.github/prompts/`): `/copilot-doctor` (30-second setup health check),
  `/ado-intake` (Boards item → intake file), `/fix-bug` (reproduce-first discipline),
  `/git-deliver` (branch · `#<id>` commit · push · draft PR), `/selfimprove` (record a
  correction), `/migrate-to-standard` (brownfield adoption assistant), `/explain` (layered code walkthrough), `/refactor` (propose then apply, behavior-preserving).
- **Skills** (`.github/skills/`, auto-discovered by their `description`): copier-update (safe one-command template update), dotnet patterns, TDD workflow, verify (stack-aware build/test gate), ado-work-items (lean CLI reads of Boards items), pipeline-author.
- **Confluence MCP** (`confluence` in `.vscode/mcp.json`): the repository's only Confluence connection; use its tools directly and do not invoke `confluence-cli`.

- **Agents** (`.github/agents/`): `code-reviewer` + `code-reviewer-deep` (Pre-Report Gate, default-FAIL discipline).
- **QA role-pack** (`.github/agents/qa/`, manual QA): `checklist-confluence` (a feature's requirements → a QA checklist → the Confluence page) and `checklist-ado` (that checklist → Azure DevOps test cases in a Test Plan). Test automation is the separate AQA track.
- **BA role-pack** (`.github/agents/ba/`): ba-analyst · req-validator (adversarial), orchestrated by `/transcript-to-backlog`; `ba-ado-ticket-structure` scaffolds the ADO Feature→Story→Task hierarchy under an Epic (approval-gated write).
- **DevOps pack** (`.github/skills/devops/pipeline-author/`): author/modify Azure Pipelines YAML (stages, the standard gates, secrets via variable groups).

- **Prompt**: `/incident-response` for sev1/sev2 incidents.
- **Spec-Driven Development**: start a feature from a spec in `ai/specs/` (specify → clarify → plan → tasks → implement).
- **Team-local** additions: drop custom prompts in `.github/prompts/team-local/`, skills in `.github/skills/team-local/`, agents in `.github/agents/team-local/`, scoped instructions in `.github/instructions/team-local/` — the template never overwrites these directories.

## Telemetry & governance
Each agent / orchestrator run appends **one JSON line** to `ai/governance/agent-runs.jsonl`
(schema in `ai/governance/README.md`). Run `python ai/governance/dashboard.py` for the per-agent / per-team
cost dashboard. The CI validators in `.github/ci-validators/` gate every change to these files.
