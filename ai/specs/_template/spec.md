# Feature: <feature name>

**Spec ID:** NNN-<slug>
**Author(s):** <names>
**Date:** YYYY-MM-DD
**Linked work item(s):** #<id>
**Status:** Draft | Clarified | Approved | Implemented

---

## 1. Problem statement

<1–3 sentences. What does this feature do, for whom, why now?>

## 2. Users and roles

| Role | What they do with this feature |
|---|---|
| <role 1> | <action> |
| <role 2> | <action> |

## 3. Acceptance criteria

List as numbered requirements. The downstream `coder` / `tester` / `reviewer` chain treats
each numbered req as an atomic unit. Be specific.

**R1.** <one acceptance criterion>
**R2.** <another>
**R3.** <…>

Avoid: vague verbs like "support," "handle," "manage." Prefer: "returns within 200ms,"
"persists across sessions," "rejects with HTTP 422."

## 4. Out of scope

What this feature does NOT do. State explicitly so reviewers don't flag missing-by-design
behavior.

- <thing 1>
- <thing 2>

## 5. Non-functional requirements

| Dimension | Target |
|---|---|
| Performance | <e.g. p95 latency < 500ms> |
| Security | <e.g. only authenticated users with role X> |
| Accessibility | <e.g. WCAG AA on new UI> |
| i18n | <e.g. EN + AR text strings> |
| Observability | <e.g. structured logs + 1 new metric> |

## 6. Edge cases

| Case | Expected behavior |
|---|---|
| Empty input | <…> |
| Concurrent edits | <…> |
| Network failure mid-operation | <…> |

## 7. Open questions (clarify before plan)

If anything below remains after `/speckit.clarify`, STOP and ask the user. Do not let
ambiguity through to the plan.

- [ ] <question 1>
- [ ] <question 2>

## 8. Out-of-band dependencies

Anything outside the team that needs to land for this feature:

- <e.g. another team's API change>
- <e.g. config flag rollout>

## 9. Acceptance test scenarios (gherkin or plain)

For each acceptance criterion, one scenario:

**R1 scenario:**
> GIVEN <precondition>
> WHEN <action>
> THEN <expected outcome>

(Repeat for R2, R3, …)

## 10. Notes (for the implementer)

Anything the implementing agents need to know that isn't in the rubric:

- <e.g. existing pattern in src/Foo to mirror>
- <e.g. flag this is gated behind a feature toggle>
