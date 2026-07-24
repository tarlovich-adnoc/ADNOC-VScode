---
description: 'DevOps — generate the standard Azure Repos branch-policy bundle for main as code: build validation on the AI-workflow gate, minimum reviewers with reset-on-push, comment resolution, merge strategy, and a required-reviewer path filter that protects template-managed files. Generates az/REST + a portal runbook; a human applies it. The MCP server cannot set policies.'
agent: 'agent'
---

# /branch-policies — the standard merge bar for `main`, as code

For **DevOps**. Produces the **script + portal runbook** that sets the standard branch-policy bundle
on `main` — the rules that actually block a bad PR from merging. It does **not** apply anything; the
MCP server cannot set branch policies. You review and run it (PAT-authenticated `az`/REST) or follow
the runbook in the portal.

Grounded in the **`ado-provisioning`** skill (Recipe 5 — auth, exact commands, REST/portal forms).

## The standard bundle (on `main`)

1. **Build validation** — the registered AI-workflow gate pipeline must pass before merge. This is
   the line that turns `azure-pipelines/ai-workflow-gate.yml` from "exists" into "enforced".
2. **Minimum reviewers** — at least 2; **creator vote does not count**; **reset approvals on a new
   push** (so a late commit cannot ride in on stale approvals).
3. **Comment resolution required** — all PR comments resolved before merge.
4. **Merge strategy** — squash (or the team's chosen single strategy), for a linear history.
5. **Required reviewer by path** — any change under `.github/ci-validators/*`, `.github/skills/*`
   (core, not `team-local/`), or `.copier-answers.yml` routes to a **platform reviewer**. This is how a
   team is stopped from silently editing the validators or the standard — the one place the
   `.github`-side merge bar can be enforced, since branch policies (not files in the repo) are what
   ADO actually obeys.

## Steps

1. **Gather inputs.** Repo (→ repository id via `az repos show --query id`), the **build-definition
   id** of the registered AI-workflow gate (from `/provision-pipeline` or *Pipelines*), and the
   platform reviewer id/group for the path filter. Ask only for what is missing.
2. **Confirm auth path.** `az devops login` with `AZURE_DEVOPS_EXT_PAT` (NOT `az login`); if `az` is
   unavailable, produce the portal runbook branch.
3. **Emit the bundle as one script** — `az repos policy build create`, `… approver-count create`,
   `… comment-required create`, `… merge-strategy create`, `… required-reviewer create
   --path-filter …` (exact flags in the `ado-provisioning` skill; REST via `az devops invoke --area
   policy`). Each policy `--blocking true --enabled true`.
4. **Emit the portal runbook**: *Repos > Branches > main (…) > Branch policies* — the same five
   rules, in order.
5. **State the boundary**: "Copilot generated the policy script; you run it. The MCP server cannot
   set branch policies."

## Output

Write the script to `provisioning/branch-policies-<repo>.sh` (or `.ps1`) and a short runbook beside
it, or present both inline. Runnable, commented, no prose padding. Always include the portal fallback.

## Rules

- **Generate, don't apply.** A policy does not exist until the script is run / the portal steps done.
- **PAT auth, least privilege** (Project and Team: Manage); never `az login`.
- **No committed secrets** (`validate-no-secrets`).
- **Both paths** — `az`/REST and portal.
- Build validation depends on a **registered** pipeline (see `/provision-pipeline`); canonical
  commands live in `ado-provisioning` — reuse, don't diverge.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "branch-policies"`).
