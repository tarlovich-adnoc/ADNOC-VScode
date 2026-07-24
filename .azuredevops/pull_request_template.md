<!-- ADNOC AI-workflow PR template — delete sections that don't apply, keep the checklist -->

## What & why

-

## Checklist

- [ ] Work item linked in the title or description (`#<id>`)
- [ ] Tests/build evidence attached or referenced (no "works on my machine")
- [ ] **AI-assisted?** → set the work item's AI Usage field to `AI-assisted` (or `AI-primary`) on completion (forward-only; tags only where the field is absent)
- [ ] Telemetry: agent/orchestrator runs for this change appended to `ai/governance/agent-runs.jsonl`
- [ ] If this PR changes `.github/` AI artifacts (skills / agents / prompts / instructions):
      eval ladder run per `ai/governance/how-to-eval-a-skill.md` (Tier 1–2 minimum; pass@3 ≥ 0.90
      for anything heading to the shared template)
- [ ] No hand-edits to template-managed (Ring-2) files — team-specific content lives in
      `.github/prompts/team-local/`, `.github/skills/team-local/`, `.github/agents/team-local/`, or `.github/instructions/team-local/`

<!-- The AI-workflow gate (6 CI validators) runs automatically on this PR. -->
