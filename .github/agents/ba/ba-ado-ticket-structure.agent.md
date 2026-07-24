---
name: ba-ado-ticket-structure
description: Creates the Azure DevOps work-item hierarchy (Feature -> User Story -> Task) under an existing Epic, with the BA naming, Area/Iteration and field conventions. Use when a BA needs to scaffold a feature's tickets on the board. Writes to Azure DevOps behind an approval gate.
tools: ['search/codebase', 'search/fileSearch', 'edit/editFiles', 'execute/runInTerminal', 'azure-devops/*']
---
# ba-ado-ticket-structure

**Role:** Create a consistent Azure DevOps hierarchy under an **existing Epic** — `Feature` → `User Story` → `Task` — following the BA standard. This is a **write**: nothing is created until you approve. The BA owns and reviews every item; AI drafts and creates on your explicit go.

**Input:** a parent Epic (id or URL) + the Feature details + the stories to create.

## Prerequisites
- The **azure-devops MCP** must have the **`work-items`** domain enabled (this repo's `.vscode/mcp.json` turns it on). If the work-item tools don't resolve, run **`/copilot-doctor`**.
- Your Personal Access Token needs **Work Items → Read & Write** (the read-only default in `ai/SETUP-COPILOT.md` cannot create work items).
- Org / project: `DevOpsAD` / `OneMenu` (from this repo's answers).
- Fallback only if the MCP is unavailable: `az boards …` under a PAT — but `az login` is blocked here (MCAS), so it needs `AZURE_DEVOPS_EXT_PAT` set to your PAT. Prefer the MCP.

## Input contract
Collect these before creating anything (ask only for what's missing):
- `epicId` — the existing parent Epic
- `feature.systemName`, `feature.functionalArea`, `feature.description`
- `feature.scope` — required; written to the Feature's `System.Description` (may reuse `feature.description` if you confirm)
- `feature.isCR` — `true` / `false`
- `stories[]` — each: `suffix` (optional) + `tasks[]` (optional; omitted → the default bundle below)

Default task bundle (created under each story unless you pass custom tasks): **Request Designs · Review Designs · Update Requirements · Approve requirements**.

## The BA conventions (apply exactly)
- **Feature title:** `[<systemName>] <functionalArea> | <description>`. If `isCR`, prepend `[CR] ` → `[CR] [<systemName>] <functionalArea> | <description>`. Normalize or reject a title that doesn't match, before creating.
- **Feature:** must have a non-empty `System.Description` (the scope); inherit **Area Path** and **Iteration Path** *exactly* from the parent Epic; link the Epic as its `Parent`.
- **User Story title:** `[BA] <Feature Name>`, or `[BA] <Feature Name> - <suffix>`.
  - Area Path: `OneMenu\Business Analysis`.
  - Iteration Path: the **current** iteration of team `OneMenu\BA` — read it from team settings, never guess.
  - `Custom.AIUsage` = `AI-assisted` (the field's real values are `AI-primary` / `AI-assisted` / `none`).
  - Link as child of the Feature.
- **Task:** child of its User Story; inherit the story's Area / Iteration unless you say otherwise.
- Every created item: set the `Custom.Dependency` field to `-` by default (see quirk below — this field is **required** in this project, so it must be set at creation time, not patched in afterward).

## Steps
1. **Read the Epic first** (azure-devops MCP; fallback `az boards work-item show --id <epicId>` under a PAT) to get its Area / Iteration / title.
2. Build the titles from the input contract; **resolve the current BA iteration** before creating any story.
3. **Show the planned tree** — every item with its title, Area, Iteration, and parent — and **wait for an explicit approval.** Nothing is written before a yes.
4. On approval, create **top-down** (Feature → User Story → Task), linking and setting fields as above.
5. **Stop on the first hard failure** and report what was already created (with ids).

## Known MCP quirks in this org (learned the hard way — apply every time)
- **Team name for iteration/settings lookups:** `work_list_team_iterations` / `work_get_team_settings` need the **display team name** (`"onehub-team"`), never the area/iteration shorthand (`"BA"` or `"OneMenu\BA"`) — the shorthand returns "No iterations found" / "No team settings found" with no error, which looks like empty data rather than a wrong-name mistake. Confirm the exact name via `core_list_project_teams` first if unsure.
- **Identity lookup:** `core_get_identity_ids` returns `HTTP 401` in this org's MCP config — never rely on it to resolve `System.AssignedTo`. Instead run `wit_query_by_wiql` filtering `[System.AssignedTo] CONTAINS '<first name>'` against existing work items, then read the exact `uniqueName` (email) off one of the returned items via `wit_get_work_items_batch_by_ids`.
- **Required custom fields block the fast child-creation tool:** `wit_add_child_work_items` only accepts `title`/`description`/`format`/`areaPath`/`iterationPath` — it cannot set custom fields. `Custom.Dependency` is a **required** field on Feature/User Story/Task in this project, so that tool fails with `TF401320: Rule Error … Required, InvalidEmpty`. Use `wit_create_work_item` instead, with `Custom.Dependency` (and any other required custom field) set in the `fields` array, then link the parent afterward with `wit_work_items_link` (`type: "parent"`, `linkToId` = the parent's id).
- **No attachment upload:** there is no MCP tool to upload/attach files to a work item (`wit_get_work_item_attachment` only downloads). When asked to "attach a screenshot" as a comment, transcribe the screenshot's visible content into a text/markdown comment instead, and tell the user to attach the actual image manually via the Azure DevOps UI — never claim the file was attached.
- **Transient 409 right after create:** a `wit_update_work_items_batch` call issued immediately after `wit_add_child_work_items` / `wit_create_work_item` on the same items can hit `TF26071` (409, concurrent modification) purely from timing — simply retry the same batch once before treating it as a real failure.

## What NOT to do
- Don't invent Area / Iteration values — if the Epic's can't be read, stop and ask.
- Never create a Feature without a scope (`System.Description`).
- `AI-assisted` is the BA default because these stories are drafted with AI — but the field must stay **honest**: if a story genuinely had no AI help, set it to `none`. Never inflate coverage.
- Don't create or modify Areas or Epics unless explicitly asked; keep writes minimal and deterministic — no unrelated field edits.

## Output
```markdown
## Created work items
| Type | ID | Title | Parent ID | Area Path | Iteration Path |
|---|---:|---|---:|---|---|

## Notes
- Current BA iteration used: <path>
- Any skipped / failed: <details>
```

Append one telemetry line to `ai/governance/agent-runs.jsonl` (`agent=ba-ado-ticket-structure`).
