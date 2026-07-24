# Plan: <feature name>

**Plan for spec:** ./spec.md
**Author(s):** <names>
**Date:** YYYY-MM-DD
**Status:** Draft | Approved

---

## 1. Architecture decisions

For each non-trivial choice, what was picked and why. Anchors the implementer agents to
the right shape.

- **Decision A:** <e.g. use the repository pattern, not data-access scattered through services>
  - **Why:** <e.g. matches existing code in OrdersService, makes the new code reviewable>
  - **Alternative considered:** <e.g. ad-hoc queries inline — rejected, breaks team convention>

## 2. File-by-file change list

| File | Change | Linked spec requirement(s) |
|---|---|---|
| `src/Api/Controllers/<New>Controller.cs` | new | R1, R2 |
| `src/Domain/Services/<New>Service.cs` | new | R1, R3 |
| `src/Domain/Repositories/I<New>Repository.cs` | new | R3 |
| `src/Infrastructure/Sql/<New>Repository.cs` | new | R3 |
| `tests/Domain.Tests/<New>ServiceTests.cs` | new | R1, R2, R3 |
| `src/Api/Program.cs` | modify | DI registration for I<New>Repository |

## 3. Test plan

For each spec requirement, one test (or table for parametrized). The `tester` sub-agent
treats this as its checklist.

- **R1:** `<New>ServiceTests.MethodName_Scenario_ReturnsExpected`
- **R2:** `<New>ServiceTests.MethodName_InvalidInput_ThrowsArgumentException`
- **R3:** integration test in `Integration.Tests/<New>RepositoryTests.cs` using Testcontainers SQL Server (or a MongoDB test double for Cosmos-backed repos)

## 4. Definition of done

- [ ] All file changes from §2 implemented
- [ ] All tests from §3 passing
- [ ] `verify` skill green (build + lint + format + test)
- [ ] Reviewer agent verdict APPROVE (default-FAIL discipline)
- [ ] No new entries in `ai/governance/optimization-log.md` for this PR's agent costs (i.e.
      no cost regression)
- [ ] Spec status updated to "Implemented"

## 5. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| <risk> | low/med/high | low/med/high | <mitigation> |

## 6. Rollback plan

If this ships and breaks production:

1. <step>
2. <step>

Worst-case undo time: <minutes/hours>

## 7. Telemetry / observability

What this feature emits, and how we check it post-deploy.

- **New log fields:** <fields>
- **New metrics:** <metrics + dashboard link>
- **Alerts:** <if any>

## 8. Migration impact

- Database migrations: <yes/no> (if yes, one-way or reversible?)
- Config flag: <yes/no>
- Breaking API change: <yes/no>

## 9. Sequencing

Order in which `tasks.md` should be executed:

1. Repository scaffolding (foundation)
2. Service logic
3. Controller surface
4. Tests
5. Wiring (DI, OpenAPI annotations)

Tasks are dependency-ordered so the `coder` sub-agent can do one at a time without
backtracking.

## 10. Out of scope (for this plan)

Explicit non-features this plan does NOT cover (mirror `spec.md` §4):

- <thing>
- <thing>
