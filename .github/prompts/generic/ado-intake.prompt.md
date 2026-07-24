---
description: 'Fetch an Azure Boards work item via MCP and write a structured intake file under ai/plans/ — the single starting point for any ticket-driven task.'
agent: 'agent'
---

# /ado-intake — work item → intake file

Turn an Azure Boards work item into a structured `intake.md` other prompts and the orchestrator
can build on. Never start planning from a half-remembered ticket.

## Steps

1. **Parse the work item id** from the user's message (`#1234`, `1234`, or a Boards URL).
   If none present, ask for it.
2. **Fetch via the `azure-devops` MCP server**: the work item (title, type, state, description,
   acceptance criteria, parent/linked items, latest relevant comments).
   - On 401/auth failure: stop — the `azure-devops` MCP server must be **Running** first. Point the
     user to **`ai/SETUP-COPILOT.md`** (PAT expired or wrong scope).
3. **Create the folder** `ai/plans/<ID>-<short-slug>/` (slug = 2-4 kebab words from the title).
4. **Write `ai/plans/<ID>-<slug>/intake.md`**:

   ```markdown
   # <ID> — <title>
   Origin: Azure Boards · Type: <type> · State: <state> · Fetched: <date>

   ## Description
   <cleaned-up description — strip HTML, keep structure>

   ## Acceptance criteria
   - <one per line — verbatim from the ticket>

   ## Linked context
   - Parent: <id/title or "none">
   - Related: <ids or "none">

   ## Open questions
   - <anything ambiguous, contradictory, or missing>
   ```

5. **No acceptance criteria?** Write `## Acceptance criteria` as
   `(!) NONE ON TICKET — confirm with PO before implementation` — never invent AC silently.
6. **Report**: file path + a 3-line summary (what, why, the riskiest open question).

## Rules

- Intake is **read-only** towards the codebase — no code edits in this prompt.
- One folder per work item; re-running refreshes `intake.md` in place (git keeps history).
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "ado-intake"`).
