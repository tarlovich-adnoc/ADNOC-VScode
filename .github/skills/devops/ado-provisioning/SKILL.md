---
name: ado-provisioning
description: >
  Provision Azure DevOps resources as code — create a repository, register a pipeline, create
  variable groups, service connections and environments, and set branch policies — via
  PAT-authenticated `az devops` CLI (or REST), with a portal runbook as the fallback. Use when
  DevOps needs to create / register / wire ADO infrastructure, not just author pipeline YAML.
  The Azure DevOps MCP server cannot do any of these; this skill produces the script and the
  runbook that a human applies. Pairs with pipeline-author (which writes the YAML this registers).
origin: ADNOC
---

# ADO Provisioning (as code)

The work a DevOps engineer actually does — **stand up repos, register pipelines, wire variable
groups / service connections / environments, set branch policies** — is provisioning, not writing
per-app YAML. This skill covers how to do that *as reviewable code*, honestly.

## The Hard Constraint (state this every time)

**The Azure DevOps MCP server cannot provision anything.** It is read + work-items + some
repo/PR operations — it does **not** create repositories, register pipelines, create variable
groups / service connections / environments, or set branch policies. So Copilot cannot "click the
buttons" for you.

What it **can** do: generate the **provisioning-as-code** (an `az devops` / REST script) **and a
portal runbook**, which a **human applies**. Never claim a resource exists because the script was
written — the script is inert until someone runs it (same rule pipeline-author states for YAML).

## Authentication — PAT, not `az login`

Provisioning here uses the **`az devops` CLI extension** (or the REST API), authenticated by a
**Personal Access Token**. This is a **different path** from `az login` (Entra / Azure Resource
Manager). That matters because some environments block interactive `az login` at the network layer
while the PAT path to `dev.azure.com` still works (PAT-mode repos sign the MCP server in the same way).

```bash
# the PAT is supplied from the environment / a prompt — NEVER written into a file or script literal
export AZURE_DEVOPS_EXT_PAT="${AZURE_DEVOPS_EXT_PAT:?set this env var to your PAT first}"
echo "$AZURE_DEVOPS_EXT_PAT" | az devops login --organization "https://dev.azure.com/<your-org>"  # PAT via stdin, non-interactive (NOT az login)
az devops configure --defaults organization="https://dev.azure.com/<your-org>" project="<your-project>"
```

- PAT scopes — **least privilege** for the job: *Code (Read & Write)* to create repos, *Build (Read
  & Execute)* + *Project and Team (Read, Write & Manage)* to register pipelines and set policies.
  Do not mint a full-access PAT.
- **Dual path / graceful degrade:** if `az` (or the `azure-devops` extension) is not available in
  your environment, every recipe below has a **portal runbook** equivalent, and most have an `az
  devops invoke` / `curl` **REST** form. Pick whichever your environment allows — the *intent* and
  the *review artifact* are the same.
- Confirm exact flags with `az <group> <command> -h`; the `azure-devops` extension's flag names
  vary slightly by version. Treat the commands below as the shape, not a frozen contract.

## Recipe 1 — Create a repository

```bash
az repos create --name "<repo>" --project "<project>"
```
- REST: `POST https://dev.azure.com/<org>/<project>/_apis/git/repositories?api-version=7.1`.
- Portal: *Repos > (repo dropdown) > New repository*.
- Then apply the standard with Copier (this is what makes it an *AI-workflow* repo, not an empty one):
  ```bash
  git clone "https://dev.azure.com/<org>/<project>/_git/<repo>" && cd "<repo>"
  copier copy --trust "git+https://dev.azure.com/<org>/<project>/_git/ai-sdlc-template" .
  git add -A && git commit -m "chore: scaffold AI workflow standard" && git push
  ```
- See the `/bootstrap-repo` prompt for a full create-repo-to-standard script + runbook.

## Recipe 2 — Register a pipeline

A committed `.yml` is inert until registered (see pipeline-author). Registration is provisioning:

```bash
az pipelines create \
  --name "<repo> CI" --repository "<repo>" --repository-type tfsgit \
  --branch main --yml-path "azure-pipelines/ci.yml" --skip-first-run true
```
- REST: `POST .../_apis/pipelines?api-version=7.1` with the YAML path in the body.
- Portal: *Pipelines > New pipeline > Azure Repos Git > Existing Azure Pipelines YAML file*.
- Registering is **not** the same as gating a PR — that needs a **branch-policy build validation**
  (Recipe 5). See the `/provision-pipeline` prompt for the full register + wire-secrets flow.

## Recipe 3 — Variable group (for pipeline secrets)

Secrets in a pipeline come from a **variable group** in *Library*, never inline in YAML (the
`validate-no-secrets` gate fails inline tokens, and they live in git history forever).

```bash
az pipelines variable-group create --name "copilot-governance" \
  --description "secrets consumed by AI-workflow pipelines" \
  --variables placeholder=unused --authorize true   # --variables is required; seed a throwaway, delete after
# mark a variable secret (or do it in the portal, which never echoes the value back):
az pipelines variable-group variable create \
  --group-id <id> --name "adoPatWorkItemsRW" --secret true --value "${SOME_PAT_FROM_ENV}"
```
- Portal: *Pipelines > Library > + Variable group*; add the var and tick the lock icon (secret).
- The value is passed **from the environment**, never typed into a committed script.

## Recipe 4 — Service connection

```bash
# Azure RM (deployments) — prefer workload-identity / Managed Identity over key-based:
az devops service-endpoint azurerm create --name "<conn>" \
  --azure-rm-service-principal-id "<spId>" --azure-rm-subscription-id "<subId>" \
  --azure-rm-subscription-name "<subName>" --azure-rm-tenant-id "<tenantId>"
```
- Other endpoint types: `az devops service-endpoint create --service-endpoint-configuration <json>`,
  or the portal: *Project settings > Service connections > New service connection*.
- The SPN secret / federated credential is configured on the identity side, **not** in this repo.

## Recipe 5 — Branch policies (the gate that actually blocks a PR)

This is what makes a PR mandatory-checked. The standard bundle on `main` — five policies:

```bash
RID=$(az repos show --repository "<repo>" --query id -o tsv)
# 1. build validation: the registered AI-workflow gate must pass before merge
az repos policy build create --branch main --repository-id "$RID" \
  --build-definition-id <pipelineId> --display-name "AI workflow gate" \
  --blocking true --enabled true --queue-on-source-update-only true --valid-duration 720 \
  --manual-queue-only false
# 2. minimum reviewers + reset stale approvals on a new push (--allow-downvotes is required)
az repos policy approver-count create --branch main --repository-id "$RID" \
  --minimum-approver-count 2 --creator-vote-counts false --reset-on-source-push true \
  --allow-downvotes false --blocking true --enabled true
# 3. all PR comments resolved before merge
az repos policy comment-required create --branch main --repository-id "$RID" \
  --blocking true --enabled true
# 4. one merge strategy (squash here) for a linear history — set one true, the rest false
az repos policy merge-strategy create --branch main --repository-id "$RID" \
  --allow-squash true --allow-no-fast-forward false --allow-rebase false \
  --allow-rebase-merge false --blocking true --enabled true
# 5. protect template-managed files: a change under these paths needs the platform reviewer.
#    Core skills only — the team-owned Ring-3 skills/team-local/ zone is excluded (see note below).
az repos policy required-reviewer create --branch main --repository-id "$RID" \
  --message "Template-managed files — needs platform review" \
  --required-reviewer-ids "<platform-team-or-reviewer>" \
  --path-filter "/.github/ci-validators/*;/.github/skills/*;!/.github/skills/team-local/*;/.copier-answers.yml" \
  --blocking true --enabled true
```
- REST fallback: `az devops invoke --area policy --resource configurations --http-method POST
  --route-parameters project=<project> --in-file policy.json`.
- Portal: *Repos > Branches > main (…) > Branch policies*.
- The `required-reviewer` path filter is how you stop a team from silently editing the validators or
  core skills, instead of leaving that part of the merge bar unenforced. ADO's `*` matches across
  `/`, so `/.github/skills/*` would also catch the team-owned Ring-3 `skills/team-local/` zone — the
  `!/.github/skills/team-local/*` exclusion (a positive include must precede it) keeps `team-local/` out of
  the platform-review net. See the `/branch-policies` prompt for the full bundle as one script.

## Recipe 6 — Environments + approvals (where `az` is thin)

There is **no `az pipelines environment` command group** — both the environment *and* its
approvals/checks are portal- or REST-only:

```bash
# create the environment (REST — there is no az CLI command for it)
az devops invoke --area distributedtask --resource environments --http-method POST \
  --route-parameters project="<project>" --in-file env.json --api-version 7.1
# add an approval / check on it (also REST-only)
az devops invoke --area pipelinesChecks --resource configurations --http-method POST \
  --route-parameters project="<project>" --in-file approval-check.json --api-version 7.1
```
- Portal is usually simplest here: *Pipelines > Environments > New environment*, then that
  environment's *Approvals and checks*.
- Be explicit when handing off: "REST or the portal creates the environment; the approval gate is a
  separate step" — do not imply the environment is gated when only the shell exists.

## Rules

- **Generate, don't pretend to apply.** Output a script *and* a runbook; the human runs it. The MCP
  server cannot create/register/policy anything — say so.
- **No secret ever lands in a committed file.** PAT/keys come from the environment (`$VAR`,
  `${input:...}`) or a variable group. The `validate-no-secrets` gate enforces this.
- **Least-privilege PAT**, scoped to the task; rotate after a one-off provisioning run.
- **Both paths, always.** Provide the `az` / REST form *and* the portal steps so the recipe works
  whether or not `az` is available in the user's environment.
- This skill provisions; **pipeline-author** writes the pipeline YAML it registers. Keep that split.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "ado-provisioning"`).

## Anti-Patterns to Avoid

| Pattern | Why | Fix |
|---|---|---|
| "I registered the pipeline" (via MCP) | MCP cannot register pipelines | Generate `az pipelines create` / portal steps; the human runs them |
| Hard-coded PAT / key in the script | Fails `validate-no-secrets`; leaks into history | `$AZURE_DEVOPS_EXT_PAT` from env or a variable group |
| `az login` to reach ADO | Entra/ARM path; may be blocked, and it is the wrong auth | `az devops login` with the PAT |
| Full-access PAT for one job | Over-broad blast radius if leaked | Least-privilege scopes, rotate after |
| Registering a pipeline and calling CI "done" | A registered pipeline still does not block a PR | Add a branch-policy build validation (Recipe 5) |
| Assuming an environment is gated because it exists | Approvals/checks are a separate REST/portal step | Set and verify the approval explicitly |
