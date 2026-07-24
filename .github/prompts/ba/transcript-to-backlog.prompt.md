---
description: Turn a meeting transcript into validated backlog items — ba-analyst drafts, req-validator gates, bounded retry. Use after a refinement/discovery session.
agent: 'agent'
tools: ['search/codebase', 'search/fileSearch', 'edit/editFiles']
---
# /transcript-to-backlog

> Note: Data handling — meeting transcripts travel to the Copilot service. Strip names/PII not
> needed for requirements; follow the org's data-classification rules.

Orchestrate the BA role-pack. **Bounded: max 3 rounds.** Human owns the final accept.

1. **`ba-analyst`** — extract requirements + draft backlog items from the transcript.
2. **`req-validator`** — adversarially score each (ACCEPT ≥85 / REJECT + fix).
3. For REJECTs, feed the fixes back to `ba-analyst` and re-run — at most 3 rounds total.
4. If items still REJECT after round 3, STOP and hand the open list to the BA — do not force-accept.

## Output
The ACCEPTED backlog items (with acceptance criteria) + the still-open list with reasons.
Each sub-agent appends telemetry (`workflow=transcript-to-backlog`).
