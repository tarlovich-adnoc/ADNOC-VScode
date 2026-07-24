---
description: 'DevOps — register a committed pipeline YAML in Azure DevOps and wire its secrets: generate the az/REST script + portal runbook to create the pipeline, variable groups, service connections and the branch-policy build validation. Generates provisioning-as-code; a human runs it. The MCP server cannot register pipelines.'
agent: 'agent'
---

# /provision-pipeline — register and wire a pipeline, as code

The **second half** of `pipeline-author`. That skill writes the `.yml`; this prompt produces the
**script + runbook** that turns the inert file into a running, PR-gating pipeline: register it,
create the variable groups / service connections it needs, and add the branch-policy build
validation. It does **not** apply anything — the MCP server cannot register a pipeline.

Grounded in the **`ado-provisioning`** skill (auth, exact commands, REST/portal fallbacks).

## Steps

1. **Find the YAML.** From the user's message or the repo: the committed pipeline path (e.g.
   `azure-pipelines/ci.yml` or the shipped `azure-pipelines/ai-workflow-gate.yml`). If absent, stop
   and point to `pipeline-author` to write it first — you register YAML, you do not invent it.
2. **Confirm auth path.** `az devops login` with `AZURE_DEVOPS_EXT_PAT` (NOT `az login`); if `az` is
   unavailable, produce the portal runbook branch and say so.
3. **Register the pipeline:**
   `az pipelines create --name "<name>" --repository "<repo>" --repository-type tfsgit --branch main
   --yml-path "<path>" --skip-first-run true` (REST / portal fallback in the skill).
4. **Wire its secrets** — only if the YAML references a variable group or service connection:
   - variable group in *Library* (`az pipelines variable-group create`), each secret var marked
     secret and fed **from the environment**, never inline;
   - service connection (`az devops service-endpoint …` or portal), preferring workload-identity.
5. **Gate the PR.** Registering alone does **not** block a merge. Add a branch-policy **build
   validation** on `main` pointing at the new pipeline (delegate to `/branch-policies`, or inline
   Recipe 5 from `ado-provisioning`).
6. **Environments / approvals** — if the pipeline deploys: create the environment, and note that the
   **approval gate is a separate portal/REST step** (CLI cannot set it). Do not imply it is gated
   when only the environment shell exists.
7. **State the boundary**: "Copilot generated the register + wire script; you run it. A committed
   YAML is inert until registered, and a registered pipeline does not block a PR until it is a
   branch-policy build validation."

## Output

Write the script to `provisioning/register-<pipeline>.sh` (or `.ps1`) and a short runbook beside it,
or present both inline. Commented, runnable, no prose padding. Always include the portal fallback.

## Rules

- **Generate, don't apply.** Never claim the pipeline runs or gates merges until a human has run the
  register step **and** added the build-validation policy.
- **PAT auth, least privilege** (Build R/E + Project Manage); never `az login`.
- **No committed secrets** — variable group + `env:` mapping; the `validate-no-secrets` gate enforces it.
- **Both paths** — `az`/REST and portal.
- Canonical commands live in `ado-provisioning`; branch policies in `/branch-policies`; YAML in
  `pipeline-author` — reuse, don't diverge.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "provision-pipeline"`).
