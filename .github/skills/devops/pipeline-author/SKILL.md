---
name: pipeline-author
description: >
  Author or modify an Azure DevOps Pipelines YAML for this org — add or change a CI stage,
  job, step, or gate (build, the AI-workflow validators, test + coverage, optional SAST);
  wire secrets through variable groups / service connections; and set trigger / PR-trigger
  hygiene. Use when the user wants to write or edit a pipeline `.yml`, add a CI gate, or
  bootstrap CI for a repo. Writes YAML only — it does NOT register the pipeline in Azure DevOps.
origin: ADNOC (mirror of ECC dotnet-patterns shape)
---

# Pipeline Author

Author and modify **Azure DevOps Pipelines** YAML for this org. Reuse the committed CI validators
and the standard gate already in the repo (`azure-pipelines/ai-workflow-gate.yml`) — do not reinvent
a build from scratch.

## When to Activate

- User asks to "write a pipeline", "add a CI stage / job / step / gate", or edit an existing `.yml`
- User wants to bootstrap CI for a new repo or add coverage / SAST to an existing one
- A migration or onboarding flow needs the AI-workflow gate wired as a build validation

## The Hard Constraint (state this every time)

**Copilot writes the YAML; it does NOT create the pipeline resource.** A `.yml` file in the repo
is inert until someone registers it as a pipeline in Azure DevOps. The flow is:

1. You author / edit the YAML and it gets **committed** (usually under `azure-pipelines/`).
2. A human **registers** it as a pipeline pointing at that YAML path — via PAT-authenticated
   `az pipelines create` (the `ado-provisioning` skill / `/provision-pipeline`), or in the ADO UI
   under *Pipelines > New pipeline > Azure Repos Git > Existing YAML*. The MCP server **cannot**
   register a pipeline.
3. Only then does it run, and only then can it be set as a **Branch Policy build validation**.

If asked to "set up the pipeline", produce the YAML and then hand off the registration step with
exact instructions — never claim the pipeline exists just because the file does. The *other half* —
actually registering it, wiring its variable groups / service connections, and adding the
branch-policy build validation — is provisioning: see the **`ado-provisioning`** skill and the
**`/provision-pipeline`** and **`/branch-policies`** prompts (DevOps pack). This skill writes YAML;
those provision the resources that run it.

## Structure

Top-level keys in roughly this order: `trigger`, `pr`, `resources`, `parameters`, `pool`,
`variables`, then `stages` (or a flat `jobs:` / `steps:` for a single-stage pipeline). Use
**stages** when there are distinct phases (build then deploy); a single CI gate can stay flat like
`azure-pipelines/ai-workflow-gate.yml`.

```yaml
stages:
- stage: ci
  displayName: 'CI'
  jobs:
  - job: build_test
    displayName: 'Build + test'
    pool: { vmImage: 'ubuntu-latest' }
    steps:
    - checkout: self
    - script: dotnet build -c Release   # illustrative (.NET); use this repo's stack build — the verify skill owns the canonical per-stack commands
      displayName: 'Build'
```

## The Standard Gates

Compose these as steps/jobs. They are the bar a PR must clear before merge:

- **Build** — `dotnet build -c Release` (.NET) or the stack's build command. Fail on warning-as-error
  where the repo enables it.
- **AI-workflow validators** — the committed, stdlib-only Node checks (no `npm install`), exactly as
  in `azure-pipelines/ai-workflow-gate.yml`: `validate-frontmatter`, `validate-skills`,
  `validate-no-personal-paths`, `validate-mcp-config`, `check-unicode-safety`, `validate-no-secrets`.
  Wire this gate as a **branch policy build validation on `main`**. Do not duplicate its logic inline.
- **Test + coverage** — run the same commands the **`verify`** skill ships (it owns the canonical
  `dotnet test --collect:"XPlat Code Coverage"` / Coverlet and Jest `--coverage` invocations for this
  repo). Reference the verify skill rather than hard-coding a divergent command, so CI and local agree.
  Tests are xUnit **or** NUnit per repo — don't assume one. Coverage bar is ≥ 80% on new code.
- **SAST (optional)** — only when the user asks for it. Add it as its own job; keep it non-blocking
  first (`continueOnError: true`) until the baseline is clean, then flip it to blocking.

## Secrets: Variable Groups / Service Connections — NEVER Inline

- **Never** put a token, password, connection string, or key literally in the YAML. The
  `validate-no-secrets` gate will fail the build, and it would be committed history forever.
- Pull secrets from a **variable group** (Library) and reference the secret var by name, e.g. the
  `copilot-governance` variable group pattern:

  ```yaml
  variables:
  - group: copilot-governance        # secret vars defined in ADO Library, not here
  steps:
  - script: ./deploy.sh
    env:
      ADO_PAT: $(adoPatWorkItemsRW)   # secret var surfaced as an env var for the step only
  ```

- Secret vars are **not** auto-mapped into the shell — surface each one explicitly via `env:` on the
  step that needs it.
- Deployments / external calls authenticate through a **service connection** (`azureSubscription:` on
  `AzureCLI@2` / `AzureWebApp@1`), never a connection string baked into the file. Prefer a Managed
  Identity / workload-identity service connection over key-based ones.

## Trigger and PR-Trigger Hygiene

- A CI gate that should run on PRs **and** on pushes to `main`:

  ```yaml
  trigger:
    branches: { include: [main] }
  pr:
    branches: { include: [main] }
  ```

- A pipeline that should run **only** on demand / schedule (e.g. a sweep job): set `trigger: none`
  and `pr: none` and add a `schedules:` cron.
- Scope noisy pipelines with `paths:` `include` / `exclude` so a docs-only change doesn't burn a build.
- `pr` triggers are honored for **Azure Repos** via Branch Policies, not by the `pr:` block alone — the
  policy is what actually blocks the merge. Authoring the `pr:` block is necessary but not sufficient;
  flag that the build-validation policy must also be added (step 3 of the hard constraint).

## Anti-Patterns to Avoid

| Pattern | Why | Fix |
|---|---|---|
| Inline secret / connection string | Leaks into history; fails `validate-no-secrets` | Variable group + service connection |
| Re-implementing the validator gate inline | Diverges from `ai-workflow-gate.yml` | Reference / reuse the committed gate |
| Hard-coding `dotnet test` flags that differ from local | CI and `verify` skill disagree | Use the `verify` skill's commands |
| Assuming the pipeline exists once the YAML is committed | YAML is inert until registered | Hand off the registration step explicitly |
| Trigger on every branch with no `paths` filter | Wasted runs on docs/unrelated changes | Scope `branches` + `paths` |

## Outputs Expected from This Skill

- The pipeline YAML (new or diffed), with the gate composition called out.
- A one-line note of where it goes (`azure-pipelines/<name>.yml`) and that it must be **committed**.
- The exact **registration** hand-off: register it in ADO (PAT-authenticated `az`/REST or the ADO UI
  — not the MCP server, which cannot register pipelines; see `ado-provisioning` / `/provision-pipeline`),
  then add it as a branch-policy build validation on `main` if it is a PR gate.
