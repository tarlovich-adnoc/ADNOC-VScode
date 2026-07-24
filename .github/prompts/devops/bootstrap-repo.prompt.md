---
description: 'DevOps — stand up a NEW Azure DevOps repository on the AI-workflow standard: generate a script + runbook that creates the repo, applies the Copier template, and sets the standard branch policies. Generates provisioning-as-code; a human runs it. The MCP server cannot create repos.'
agent: 'agent'
---

# /bootstrap-repo — new repo, on the standard, as code

For a **DevOps / platform engineer** standing up a new repository. Produces a **provisioning script
plus a portal runbook** that: creates the repo in Azure DevOps, applies this Copier template, makes
the first commit, and sets the standard branch policies. It does **not** apply anything itself —
the MCP server cannot create a repository. You review the script and run it (PAT-authenticated `az`),
or follow the runbook in the portal.

Grounded in the **`ado-provisioning`** skill (auth, exact commands, REST/portal fallbacks).

## Steps

1. **Gather inputs.** From the user's message (ask only for what is missing — never guess):
   - repo name; target `project`; `org` (default to `azure_org` in `.copier-answers.yml` / the
     `azure-devops` server in `.vscode/mcp.json` if this is run from an existing standard repo);
   - the **stack** (`dotnet` / `react-web` / `react-native` / `flutter` / `none`) and which **packs**
     to turn on (`use_devops_pack`, `use_qa_pack`, …) — these become Copier `--data` answers;
   - the template source URL (the `ai-sdlc-template` repo's `git+https://…` path).
2. **Confirm auth path.** Per the `ado-provisioning` skill: `az devops login` with
   `AZURE_DEVOPS_EXT_PAT` (NOT `az login`). If the user cannot run `az`, produce the **portal
   runbook** branch instead and say so.
3. **Generate the bootstrap script.** A single reviewable script (default bash; offer PowerShell on
   request) that runs, in order:
   - `az repos create --name "<repo>" --project "<project>"`
   - `git clone` the new repo, then `copier copy --trust "<template-url>" .` with the gathered
     answers passed as `--data key=value` (one per answer), so it scaffolds non-interactively;
   - `git add -A && git commit -m "chore: scaffold AI workflow standard" && git push`;
   - the **standard branch-policy bundle** on `main` (delegate to the `/branch-policies` output, or
     inline Recipe 5 from `ado-provisioning`: build validation, min reviewers + reset-on-push,
     required-reviewer path filter protecting `.github/ci-validators/*`, `.github/skills/*`
     (core only — the Ring-3 `skills/team-local/` zone is excluded), `.copier-answers.yml`).
   - **No secret literals** — the PAT is read from the environment (`$AZURE_DEVOPS_EXT_PAT`).
4. **Emit the portal runbook** as the fallback: create repo in *Repos*, clone + `copier copy`
   locally, push, then set the same policies under *Repos > Branches > main > Branch policies*.
5. **State the boundary** plainly: "Copilot wrote the script + runbook; you run it. The MCP server
   cannot create the repo or set the policies — those are PAT-authenticated `az`/REST or portal
   actions."

## Output

Write the script to `provisioning/bootstrap-<repo>.sh` (or `.ps1`) and the runbook to
`provisioning/bootstrap-<repo>.md` in **your platform/ops repo** (create the folder if absent), and
summarize what a human must do to apply it. If the user prefers, present both inline instead of
writing files. Raw, runnable, commented — no prose padding.

## Rules

- **Generate, don't apply.** Never claim the repo or policies exist — the script is inert until run.
- **PAT auth, least privilege** (Code R/W + Project Manage to create + set policies); never `az login`.
- **No committed secrets** — `$AZURE_DEVOPS_EXT_PAT` / variable group only (`validate-no-secrets`).
- **Both paths** — always include the portal runbook so it works without `az`.
- The branch-policy detail lives in `/branch-policies`; the pipeline register/wire lives in
  `/provision-pipeline`; the canonical commands live in the `ado-provisioning` skill — reuse, don't
  diverge.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "bootstrap-repo"`).
