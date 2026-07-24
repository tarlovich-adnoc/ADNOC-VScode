---
name: copilot-doctor
description: >
  Diagnose and repair this repository's Copilot workflow, including IDE discovery settings, Copier
  passport, Git initialization, Rider MCP mirroring, artifact layout, validators, telemetry, and
  user-guided Azure DevOps, Confluence and Figma MCP setup verification. Use when onboarding a
  repository, when Copilot cannot see an agent, prompt, skill or external service, or when the user
  invokes copilot-doctor.
---

# Copilot Doctor

Use Python only for deterministic local repository checks and repairs. Do not call an MCP tool or
external service. Inventory MCP configuration and give the user documentation-backed setup or
verification guidance instead.

## Mandatory flow

1. Do not create or announce a plan, todo list, checklist, or interpretation step.
2. Do not ask which IDE is in use. Select `--ide rider` for Rider/JetBrains, `--ide vscode` for VS
   Code, or `--ide auto` when the available context does not identify the IDE. Auto mode treats a
   repository with `.idea/` as Rider.
3. Immediately run the command matching the selected IDE from the repository root:

```text
python3 .github/skills/copilot-doctor/scripts/copilot_doctor.py --ide vscode
python3 .github/skills/copilot-doctor/scripts/copilot_doctor.py --ide rider
python3 .github/skills/copilot-doctor/scripts/copilot_doctor.py --ide auto
```

If `python3` is unavailable, retry the same selected IDE by replacing only `python3` with `python`
or, on Windows, `py -3`. Never change the selected IDE while retrying the Python launcher.

Use the repository as the working directory. Allow the script to finish all checks; do not stop at
the first failure. The script does not inspect, start, or call any MCP server.

4. Preserve the script's complete standard output for the final response. A non-zero exit code is an
   expected diagnostic result, not a reason to stop.
5. Read the `CONTEXT` line. Use its `os` and `ide` values when selecting platform-specific
   instructions.
6. Read `.vscode/mcp.json` and `.copier-answers.yml` only to inventory active MCP servers and read the
   canonical Azure DevOps project context. Read the exact `azure_project` value from
   `.copier-answers.yml`; do not guess it from the repository folder, `team_name` or another answer.
   Do not start a subprocess or inspect a token value.
7. Build an `MCP server inventory`:
   - List every key under `.vscode/mcp.json` → `servers`, including team-local or unknown servers.
     Mark each listed key `ACTIVE` and cite its exact `servers.<name>` path as evidence.
   - Do not add `azure-devops`, `confluence`, `figma` or any other server when its key is absent. An
     absent server is simply inactive and is not a failure, warning or setup problem.
   - If the `servers` object is empty or missing, say `No active MCP servers are declared in
     .vscode/mcp.json.` and do not add setup guidance.
   Configuration is not connectivity: never report `PASS`, `AUTH FAIL` or another live-service
   verdict from this inventory.
8. For every active standard server, open and read its canonical rendered documentation:
   - Azure DevOps: [Azure DevOps setup](ai/SETUP-COPILOT.md#azure-devops)
   - Confluence: [Confluence setup](ai/SETUP-COPILOT.md#confluence-setup)
   - Figma: [Figma setup](ai/BY-ROLE.md#designer)
9. For each active standard server, add `Test first; setup only if it fails` guidance. Put the
   copy-ready test prompt before any setup instructions and explicitly tell the user to run it in a
   new Agent-mode message. State that a successful actual tool response means no setup action is
   required. Emphasize that if the test fails, the user should follow the numbered setup instructions
   immediately below it:
   - **Azure DevOps test:** `Using the azure-devops MCP tools, list the teams in project
     "<azure_project>" and show the actual tool response.` Replace `<azure_project>` with the exact
     passport value. Explain that a real response verifies server startup, tool discovery,
     authentication and project access.
   - **Confluence test:** `Using the confluence MCP tools, search for an existing article and show the
     actual tool response.` Explain that a result verifies the request path. Do not substitute the
     Azure DevOps project name as a Confluence search term.
   - **Figma test:** `Using the figma MCP tools, show metadata for the current selection.` Explain that
     Figma Desktop must be open, signed in and have a file or node selected.
   After each test and failure instruction, provide the actual numbered setup steps derived from the
   relevant documentation—not only a link. Include only the documented prerequisite, token or sign-in,
   IDE secret placement, server start, restart, Agent-mode and tool-discovery steps for the `CONTEXT`
   OS and IDE. For Figma, state that the documented setup uses Figma Desktop sign-in rather than a PAT.
   Include the canonical documentation link as a source after the actual steps, never as a substitute
   for them. Exclude inactive servers, other operating systems, other IDEs and unrelated connection
   modes.
10. For an active unknown or team-local server, add `User verification guidance` suggesting `Using
    the <server-name> MCP tools, perform the smallest read-only list or search request and show the
    actual tool response.` Do not invent token/setup steps or claim what success means beyond
    receiving an actual tool response.
    These prompts are suggestions for the user to run in a new Agent-mode message. Do not run them
    yourself.
11. Return the complete local doctor output verbatim in a plain-text code block, followed by an
    `MCP server inventory` table with Server, Status and exact configuration Evidence. Then add the
    applicable actual `Test first; setup only if it fails` guidance for active standard servers and `User
    verification guidance` for active unknown/team-local servers. Do not mention inactive servers.
    End with one overall verdict that combines the local result with the active-server inventory and
    explicitly says MCP connectivity was not tested.

The following rules are mandatory:

- Do not summarize, paraphrase, reorder, shorten, or omit any output line.
- Do not invoke any MCP tool or test external connectivity. Do not run Python, shell commands, `npx`,
  `uvx`, HTTP requests or the deleted `mcp_probe.py` for an external-service check.
- Reading `.vscode/mcp.json` proves only configuration presence. Never present it as authentication,
  authorization, reachability or live-service evidence.
- Do not ask the user to paste a token into chat and never print, inspect or repeat a token value.
- Do not use a documentation link as setup guidance by itself; read the section and output its
  applicable numbered steps.
- Do not perform create, update, delete, publish, comment, or other write operations during a check.
- Do not copy MCP setup instructions into this skill or infer them from memory.
- Do not invent a command, menu path, token scope, or environment variable absent from the linked
  rendered documentation.
- Do not add headings such as `Summary` or `Done`.
- Do not add extra advice, offers to perform fixes, or follow-up questions.
- Do not use a task/todo tool for this skill.
- If a canonical file or section is missing, report the exact unresolved link and do not fabricate
  replacement instructions.
- If the launcher itself cannot run, report only the exact command attempted and its complete error;
  do not invent remediation that the deterministic script did not print.

## Local output meanings

- `PASS` means the check ran and succeeded.
- `FIXED` means the script made an idempotent repository repair.
- `NOTE` means an IDE-only state still needs manual confirmation.
- `FAIL` means a local action is required. Follow its deterministic local `fix` block.
- `SKIP` means the optional integration is not configured for this repository.

## Deterministic repairs

The doctor may make only these changes:

- add missing canonical Copilot entries to `.vscode/settings.json`;
- when Rider is selected, create or correct root `.mcp.json` from `.vscode/mcp.json`, omitting
  VS Code-only inputs and secret placeholders so Rider inherits secrets from the OS;
- initialize Git when the directory is not already a work tree, then create the initial commit after
  all doctor repairs and telemetry are present;
- append one `copilot-doctor` telemetry record to `ai/governance/agent-runs.jsonl`.

Do not put tokens into either MCP file. Do not push, create a remote, alter an existing repository's
history, or commit an existing repository's unrelated changes.

## Standalone helper

Use the Rider synchronizer independently when only the mirror needs repair:

```text
python3 .github/skills/copilot-doctor/scripts/sync_rider_mcp.py
```
