---
description: 'Deliver finished work the team way: feature branch, surgical staging, work-item-linked commit, push, PR. Never pushes to main.'
agent: 'agent'
---

# /git-deliver — branch · commit · push · PR

The single delivery routine. Other prompts (and the orchestrator) delegate here instead of
re-implementing git steps.

## Preconditions (verify, don't assume)

1. **Evidence of green tests/build for the touched modules.** If none exists in this session,
   run the stack's verify command first and show the output. No evidence → no delivery.
2. A work item id (`#<id>`) — ask if missing; ADNOC commits must trace to Boards.

## Steps

1. **Branch**: `feature/<id>-<short-slug>` off the agreed base (default `main`).
   If already on a feature branch matching the work item — keep it.
2. **Stage surgically**: list the files traced to THIS task and stage only them (`git add <paths>`,
   never `git add -A`). Show the list. Anything unexpected in `git status` → stop and ask.
   If an orchestrator plan is active, include its updated `ai/plans/<folder>/plan.md`.
3. **Commit**:
   - Title: `<type>: <imperative summary> #<id>` (≤ 72 chars; `#<id>` links the Boards item —
     native Azure Repos linking).
   - Body: 2-4 bullets explaining **why**, not what.
4. **Push**: `git push -u origin <branch>`. Never push `main`/`master`. Push rejected
   (non-fast-forward / policy) → stop and report; do not force-push.
5. **PR**: open via `az repos pr create --draft --work-items <id>` (or tell the user the exact
   UI steps if the CLI isn't available). The PR will run the AI-workflow gate
   (6 validators) — that is expected and required.
6. **Report**: branch, commit hash, PR link/id, and what the reviewer should look at first.

## Hard rules

- Never `--force` / `--no-verify`. Never amend someone else's commit.
- Never deliver with failing or unrun tests "to save time".
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "git-deliver"`).
