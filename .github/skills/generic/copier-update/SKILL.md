---
name: copier-update
description: >
  Update a repository from its Copier template safely and automatically, including prerequisite
  checks, preservation and restoration of unfinished work, an isolated update branch, conflict
  detection, telemetry, and a local update commit. Use when the user explicitly asks to run,
  perform, or apply copier update, update the AI SDLC template, or pull the latest template changes.
---

# Copier Update

Run the complete update for the user. Assume they may not know Git or package-management commands.
Handle reversible local state automatically, show concise progress, and stop only on a hard blocker.

## Workflow

1. Locate the repository root and read `.github/tested-copier-versions.txt` when present.
2. Run the portable helper at [scripts/copier_update.py](scripts/copier_update.py) with the current
   repository as the working directory.
3. If the helper reports `INSTALL_REQUIRED`, invoke the `ai-sdlc-template-install` skill. After it
   succeeds, rerun the helper automatically from the beginning.
4. If the helper reports missing Git `user.name` or `user.email`, ask only for the missing value,
   configure it locally for this repository, and rerun.
5. If a failed update reports a DNS, timeout, proxy, TLS/certificate, connection-refused, or similar
   transport problem involving `git.epam.com`, preserve the recovery stash, ask the user to check
   EPAM network or VPN access, and include this exact advice: `You might need to disable Zscaler.`
   Do not present Zscaler as the fix for an authentication or authorization failure.
6. If the helper reports conflicts, list the files and the retained recovery stash. Do not reset,
   discard, or overwrite anything.
7. On success, report the update branch, template version, commit, whether unfinished work was
   restored, and whether anything remains local-only.

Use one of these commands, choosing an available Python launcher:

```text
python3 .github/skills/generic/copier-update/scripts/copier_update.py
python .github/skills/generic/copier-update/scripts/copier_update.py
py -3 .github/skills/generic/copier-update/scripts/copier_update.py
```

Add `--reanswer` only when the user explicitly wants to answer Copier questions again. Add `--push`
only when the user explicitly asks to push the update branch.

## Safety contract

- Treat a dirty working tree as normal. The helper must stash tracked and untracked work, verify a
  clean tree, perform the update, then restore the exact stash.
- Never use `git reset --hard`, `git checkout .`, `git clean`, or any other discard operation.
- Never drop the recovery stash until restoration succeeds.
- Never mix the user's unfinished work into the template-update commit.
- Never install or repair Copier directly. Delegate that work to `ai-sdlc-template-install`.
- Never push unless the user explicitly requested it.
- Stop for an in-progress merge, rebase, or cherry-pick; missing `.copier-answers.yml`; unresolved
  update or stash conflicts; missing Git identity; failed installation; or failed commit.

## Status reporting

Before mutation, summarize repository, branch, worktree, upstream, Copier version/range, and passport
status. After completion, use plain language such as:

```text
Template update complete
- Update branch: copier-update/20260715-180000
- Template version: v1.2.3
- Update commit: abc1234
- Your unfinished work: restored
- Push: not requested; the branch is local
```

When blocked, lead with the preserved state and one next action. If a stash exists, always print its
reference and state that it has not been deleted.
