---
description: 'Brownfield adoption assistant — classify the repo''s pre-existing Copilot files against the template (duplicate / custom / conflict) and produce the migration plan. Run on the adoption branch right after copier copy.'
agent: 'agent'
---

# /migrate-to-standard — finish a brownfield adoption safely

You run on the **adoption branch** of a repo that already had its own `.github/` before the
template arrived. Your job: nothing of the team's gets lost, everything custom lands in Ring-3,
and the diff the team reviews is honest.

## Preconditions (verify, else stop)

1. NOT on `main`/`master` — refuse to run there; adoption happens on a branch.
2. The raw `copier copy` result is **committed** on this branch — verify with `git log` (a commit
   newer than `main` containing `.copier-answers.yml`). An uncommitted tree makes every
   `git diff main HEAD` below empty and silently breaks classification — if missing, tell the
   user to run `git add -A && git commit -m "chore: adopt ai-sdlc-template (raw)"` first.
3. `main` still holds the pre-adoption state (`git rev-parse main` works).
4. If the default branch is not `main` (e.g. `master`, `develop`) — resolve it once via
   `git symbolic-ref refs/remotes/origin/HEAD` and substitute it everywhere `main` appears below.

## Procedure

1. **Inventory the pre-existing AI files** (what the team had before adoption):
   `git ls-tree -r --name-only main -- .github/ .mcp.json .vscode/mcp.json` (ignore `src/`, tests — the
   template never touches those). Treat a pre-existing `.github/copilot-instructions.md` as
   team-owned: the template does not ship that path, so it must remain unchanged and in place.
2. **Classify every pre-existing file** into exactly one bucket:

   | Bucket | Test | Action |
   |---|---|---|
   | **DUPLICATE** | same-named file is template-managed AND content now differs from `main` | show `git diff main HEAD -- <file>`; the template version stays; anything team-specific from the old version moves to Ring-3 or `project-learnings` |
   | **CUSTOM** | not a template-managed name (including `.github/copilot-instructions.md`) | **non-colliding names STAY IN PLACE** — Copier only manages files the template ships, so they are already update-safe; `*.instructions.md` must remain in `.github/instructions/`, root `copilot-instructions.md` must remain at `.github/`, and `*.agent.md` in `.github/agents/` or they stop loading. Move into `team-local/`/`skills/team-local/` only files that name-collide with template ones or have no working home |
   | **PROTECTED** | path already in `_skip_if_exists` (e.g. a pre-existing `project-learnings`) | confirm it survived unchanged (`git diff main HEAD -- <file>` is empty) — report as confirmed |
   | **OBSOLETE** | superseded by a shipped equivalent (their hand-rolled reviewer vs `code-reviewer`) | propose deletion, listing what replaces it |

3. **Write the migration report** to `ai/plans/adopt-standard/plan.md`: one table row per file
   (`file · bucket · action · status`), plus an "unresolved decisions" list for anything ambiguous.
4. **MANDATORY STOP** — present the report in chat and wait for explicit approval.
5. **Execute on approval**: perform the moves (`git mv`), restore team content into Ring-3 from
   `git show main:<file>` where needed, delete OBSOLETE files. Two JSON special cases that
   cannot live in Ring-3: because `.vscode/` is skip-protected, the template's settings pin
   never arrived — merge `"github.copilot.chat.codeGeneration.useInstructionFiles": true` into
   the existing `.vscode/settings.json`; and if the old repo had its own MCP servers, re-merge
   those server entries from the old config (`git show main:.mcp.json` or `main:.vscode/mcp.json`)
   into the template's `.vscode/mcp.json` (they only function there — Handbook recipe 7 sanctions
   this edit). One commit:
   `chore: migrate pre-existing Copilot files to Ring-3 (adoption)`.
6. **Verify**: run the six CI validators; all must pass. Tick rows in the report.
7. **Hand off**: tell the champion to push and open the adoption PR (`/git-deliver`); the PR body
   links `ai/plans/adopt-standard/plan.md`.

## Hard rules

- Never delete anything that is not OBSOLETE-with-replacement; when unsure → CUSTOM (Ring-3).
- Never replace, move, or merge a pre-existing `.github/copilot-instructions.md`; report it as
  preserved team-owned repository-wide guidance. Check it for contradictions with
  `.github/instructions/generic/adnoc-standard.instructions.md` and surface any decision to humans.
- Never run or recommend `copier copy --overwrite` outside an adoption branch.
- The team's old content is always recoverable via `git show main:<path>` — say this out loud in
  the report; it removes the fear.
- Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "migrate-to-standard"`).
