# Tasks: <feature name>

**Tasks for spec:** ./spec.md
**Plan:** ./plan.md
**Generated:** YYYY-MM-DD

Each task is a discrete unit the `coder` sub-agent picks up one at a time. Tasks are
**dependency-ordered** — task N+1 may rely on task N's output.

The `tester` sub-agent picks up the test task immediately after each implementation task.
The `reviewer` sub-agent gates at the end of each round, not per-task.

---

## Task 1 — <name>

**Linked spec req:** R1
**Files touched:** `src/.../Foo.cs`
**Depends on:** —
**Definition of done:** Code compiles. Unit test from §3 of plan passes for R1.

**Steps for `coder`:**
1. <step>
2. <step>

**Test (`tester` after coder):**
- Create `tests/.../FooTests.cs` with `Theory` covering R1's scenarios from spec §9

---

## Task 2 — <name>

**Linked spec req:** R2, R3
**Files touched:** `src/.../Bar.cs`, `src/.../IBar.cs`
**Depends on:** Task 1
**Definition of done:** Code compiles. Tests pass for R2 and R3.

**Steps for `coder`:**
1. <step>
2. <step>

**Test (`tester` after coder):**
- Add `BarTests.cs` with cases for R2 and R3

---

## Task 3 — wiring

**Linked spec req:** R1, R2, R3 (integration)
**Files touched:** `src/Api/Program.cs`
**Depends on:** Tasks 1 and 2
**Definition of done:** DI container resolves new services. Integration test (Testcontainers
DB) passes.

**Steps for `coder`:**
1. Register `IFoo` → `Foo` (Scoped)
2. Register `IBar` → `Bar` (Scoped)
3. Add Minimal API endpoints calling the services

**Test (`tester` after coder):**
- `WebApplicationFactory<Program>` integration test exercising the new endpoint end-to-end

---

## Round budget

The `/spec-to-impl` orchestrator (an optional CoE-maintained pattern — not shipped by default)
allows max 3 rounds. Each round = all tasks above run through coder → tester → reviewer.

- **Round 1:** straightforward execution
- **Round 2:** address reviewer's BLOCK findings from round 1
- **Round 3:** last chance; if BLOCK persists, stop and ask human

## Telemetry hooks

Per task, the coder/tester/reviewer chain appends 3 JSONL lines minimum to
`ai/governance/agent-runs.jsonl` with `workflow=chained-spec-to-impl`. Use this to spot which
tasks consume disproportionate token budget (candidate for spec refinement).
