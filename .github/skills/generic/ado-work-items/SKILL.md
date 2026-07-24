---
name: ado-work-items
description: >
  Read or query Azure DevOps work items (tickets, bugs, PBIs) via the `az boards` CLI under a PAT,
  so answers are grounded in what the board actually says. Use when the user wants to show a work
  item, list "my active items", or run a WIQL query via the CLI — a lean, on-demand alternative to
  the azure-devops MCP server that adds zero idle context (it loads only when invoked). Also use when
  the azure-devops MCP server is not enabled. The standard ticket->plan intake (/ado-intake) still
  uses the MCP by default.
origin: ADNOC (CLI skill vs MCP context cost — a lean CLI tool for AI agents)
---

# ADO Work Items (CLI read)

Read Azure DevOps Boards data with the `az boards` CLI instead of the MCP server. A skill costs
**zero context at idle** and loads only when you invoke it — unlike an always-registered MCP server,
whose tool metadata sits in context every request. This is the "lean read" path.

## When to use this vs the MCP

- **This skill** — occasional reads ("show WI 356", "what are my active bugs"), or any setup where you
  want to keep idle context lean, or the `azure-devops` MCP server is **not enabled** in `.vscode/mcp.json`.
- **The MCP server** — the default for `/ado-intake` (and the QA pack's `checklist-ado`), and better for
  high-frequency, back-to-back board interactions in one session.
- **Lean-context mode (opt-in, measure first):** a team that wants to reclaim the MCP's idle context
  can disable the `azure-devops` server in `.vscode/mcp.json` and rely on this skill for reads.
  (Work-item *mutations* still go via `/git-deliver` `#<id>` commits or the Boards UI — this skill
  never writes; ADO *infrastructure* provisioning, when the DevOps pack is on, is the separate
  `ado-provisioning` skill.) Before doing that, **measure** the actual MCP idle cost in your IDE
  — the large figures quoted for *Copilot CLI* (no lazy loading) are smaller in VS Code / Rider,
  where servers and tools can be toggled. Note `/ado-intake` is MCP-based, so lean mode also means
  pointing intake at this CLI path.

## Authentication — PAT, same as `ado-provisioning` (DevOps pack)

Reads use the `az boards` CLI (the `azure-devops` extension), authenticated by a **PAT** — the same
path as the `ado-provisioning` skill, and a **different** path from `az login` (Entra/ARM, often
blocked). Least-privilege scope here is just **Work Items (Read)**.

```bash
export AZURE_DEVOPS_EXT_PAT="${AZURE_DEVOPS_EXT_PAT:?set this env var to your PAT first}"
echo "$AZURE_DEVOPS_EXT_PAT" | az devops login --organization "https://dev.azure.com/<your-org>"  # PAT via stdin, non-interactive (NOT az login)
az devops configure --defaults organization="https://dev.azure.com/<your-org>" project="<your-project>"
```

Confirm exact flags with `az boards -h`; the extension's flags vary slightly by version.

## Recipe 1 — Show one work item

```bash
az boards work-item show --id 356 --output json
```
- Returns the fields the agent needs to ground an answer: title, state, type, description, assigned-to,
  and relations (linked items / hyperlinks). Use `--output json` so the agent can read fields cleanly.
- "Load work item 356" -> this skill -> `az boards work-item show --id 356 --output json`.

## Recipe 2 — Query with WIQL ("my active items", "active bugs")

```bash
az boards query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems \
  WHERE [System.WorkItemType] = 'Bug' AND [System.State] = 'In Development' \
  AND [System.AssignedTo] = @Me ORDER BY [System.ChangedDate] DESC" --output table
```
- `@Me` resolves to the authenticated user. Keep the `SELECT` list small — pull only the fields the
  answer needs, not the whole item, to keep context lean (the entire point of using the CLI).
- State names are process-specific — swap `'In Development'` for your board's in-progress state
  (stock processes use `'Active'`). A state name that doesn't exist on the board simply returns
  0 rows, so an empty result may mean a wrong state name, not "no items".

## Recipe 3 — Follow a link found in a work item

A work item's description or relations often point at a Confluence page or another item. Read the
item (Recipe 1), extract the URL, then hand off a Confluence page to the repository's configured
Confluence connection (MCP by default, or the `confluence` skill in CLI mode); a linked work item goes
back through Recipe 1. Never activate a second Confluence path as a fallback.

## Rules

- **Read-grounding, not mutation.** This skill reads to ground answers. Creating/closing work items
  is a deliberate act: the standard write paths are commits that link `#<id>` (via `/git-deliver`)
  and the Boards UI — do not silently mutate a ticket as a side effect of a read.
- **PAT via env, never inline.** `$AZURE_DEVOPS_EXT_PAT` / a placeholder only — the `validate-no-secrets`
  gate fails literal tokens. Least-privilege (Work Items Read).
- **`az devops login`, never `az login`** for ADO.
- **Pull only the fields you need** (small `SELECT`, specific `--id`) — the cost advantage over the
  MCP is lost if you dump whole items into context.
- Provisioning ADO resources is the **`ado-provisioning`** skill (DevOps pack); this one only reads Boards.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "ado-work-items"`).

## Anti-Patterns to Avoid

| Pattern | Why | Fix |
|---|---|---|
| `az login` to read boards | Entra/ARM path; may be blocked; wrong auth | `az devops login` with the PAT |
| Hard-coded PAT in a command | Fails `validate-no-secrets`; leaks to history | `$AZURE_DEVOPS_EXT_PAT` from env |
| `SELECT *` / dumping whole items | Burns the context the CLI was meant to save | Select only needed fields |
| Using this for the standard intake | `/ado-intake` (MCP) is the default intake path | Use `/ado-intake`; use this for ad-hoc reads |
| Mutating a ticket during a "read" | Surprising side effect | Mutations via `/git-deliver` `#id` or the Boards UI |
