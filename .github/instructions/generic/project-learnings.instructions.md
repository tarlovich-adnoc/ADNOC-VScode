---
description: 'Accumulated team corrections — concrete "Always X for Y" rules. Append-only learning log maintained BY THE AGENT via /selfimprove. Protected from template updates.'
applyTo: '**'
---

# Project learnings

Accumulated corrections for this repo. **The agent maintains this file, not just humans.**

The contract:

- When the user corrects your approach, append a one-line rule here **before ending the session**
  (or run `/selfimprove`, which does it properly across all layers).
- Write rules **concretely** — `Always use X for Y` / `Never do X when Y` — never vaguely
  ("be careful with Y" is banned).
- Before adding, **search this file**: if an existing rule already covers the correction,
  tighten that line in place instead of adding a near-duplicate.
- **Remove** a rule when the underlying cause is gone (dependency upgrade, refactor, process change).
- Order is chronological (oldest first); add `##` topic groups only when it improves scanning.
- **Rules graduate:** ≥5 rules on one topic → extract into an instruction/skill; a rule that would
  be true in ANY ADNOC repo → champion PRs it to `ai-sdlc-template` so every team gets it via
  `copier update` (see `/selfimprove` → Promotion paths).

This file is Ring-3-protected: `copier update` never overwrites it. It is THIS team's memory.

## Seed rules (replace with your own as they accumulate)

- Always append one JSON line to `ai/governance/agent-runs.jsonl` after every agent/orchestrator run —
  runs without telemetry are invisible to the cost dashboard and the AI-adoption evidence.
- Never hand-edit template-managed (Ring-2) files like `.github/agents/generic/code-reviewer.agent.md` —
  put team-specific behavior in `.github/prompts/team-local/` or `.github/skills/team-local/` instead;
  hand-edits cause merge conflicts on every `copier update`.
- When the user corrects the same mistake twice, that is a missing rule — record it here
  immediately via `/selfimprove` instead of apologizing and repeating it next session.
