---
description: 'Disciplined bug fix: reproduce with a failing test FIRST, root-cause, minimal fix, full verify, deliver. Use for any defect or regression report.'
agent: 'agent'
---

# /fix-bug — reproduce → root-cause → fix → verify → deliver

No guess-patches. A bug fix without a reproducing test is a future regression.

## Steps

1. **Intake.** If a work item id is mentioned → run `/ado-intake` first and read the intake file.
   Otherwise restate the bug in 2 sentences: expected vs actual.
2. **Reproduce — failing test FIRST** (see the `tdd-workflow` skill):
   - Write the smallest test that fails for the reported reason. Run it. Show the RED output.
   - **Cannot reproduce?** STOP. Report what you tried (inputs, env, versions) and ask for more
     context. Do NOT "fix" what you cannot reproduce.
3. **Root-cause.** Read the involved code paths until you can explain the failure in one sentence
   naming the exact line/condition. "It seems flaky" is not a root cause — if it is genuinely
   flaky, say so explicitly and investigate timing/shared-state instead.
4. **Minimal fix.** Change the least code that makes the test pass without breaking the contract.
   If the fix wants to spread across many files or rewrite a subsystem — STOP and propose a split
   (quick safe fix now + refactor ticket).
5. **Verify wide.** Run the affected module's full test suite, not just the new test. Show output.
6. **Regression guard.** Keep the reproducing test; name it after the work item
   (e.g. `Bug1234_...`) so future readers find the story.
7. **Learn.** If the bug came from a wrong assumption an agent/instruction encodes — run
   `/selfimprove` so it never repeats.
8. **Deliver** via `/git-deliver` (it enforces branch/commit/PR rules).

## Output contract

RED test output → root cause (1 sentence) → diff summary → GREEN suite output → delivery report.
Append one telemetry line to `ai/governance/agent-runs.jsonl` (`"agent": "fix-bug"`).
