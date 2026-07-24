---
description: 'Targeted, behavior-preserving refactor of selected code: propose first, get explicit OK, then apply and verify. Use to restructure code without changing what it does.'
agent: 'agent'
---

# /refactor — read → propose → get OK → apply → verify → diff

Restructure the selected code without changing its behavior. Nothing is edited until the user
explicitly approves the plan.

## Steps

1. **Read the selection and its context.** Find the callers, the state it reads/writes, the
   dependency injection wiring, and the tests that pin its behavior. A refactor you cannot pin
   with existing tests is riskier — say so.
2. **Propose a change summary FIRST, and list the risks.** State what you will restructure and why
   (extract a method/component, remove duplication, tighten types, reduce nesting). List the
   concrete risks (untested paths, behavior that is hard to preserve, wide blast radius). Then
   **STOP and get the user's explicit OK before editing.** Do not touch code in this step.
3. **Apply** the approved change. Follow the size and structure limits in `.github/instructions/`
   for this repo's stack — do not hardcode your own thresholds. Never hand-edit generated files.
4. **Verify** by running the `verify` skill (build / analyze / format / tests for this stack).
   Behavior and tests must stay green; if anything goes red, the refactor is not done.
5. **Open the diff** in the editor for the user to review.

## Contract

Behavior-preserving only. **No public-API change unless the user explicitly asks.** If the
restructuring you want would change behavior or a public contract, stop and treat it as a
separate, agreed task — do not fold it into the refactor.

## Output contract

Change summary + risks (before any edit) → explicit user OK → applied diff → green `verify`
output → diff opened for review.
