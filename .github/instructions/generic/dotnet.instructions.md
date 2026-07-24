---
description: '.NET coding and test rules auto-applied to every C# file. Style, async, DI, logging, data-access and test discipline for this repo.'
applyTo: '**/*.cs'
---

# .NET rules (auto-applied to *.cs)

## Code

- Nullable reference types stay **enabled**; never silence warnings with `!` — fix the flow or
  widen the type honestly.
- Async all the way: suffix async methods with `Async`, accept and **pass through a
  `CancellationToken`** on every I/O path; never `.Result` / `.Wait()` (deadlock + thread-pool burn).
- Dependency injection via **constructor parameters** only; no service locator, no `new`-ing
  dependencies inside business code.
- DTOs and value-shaped data are `record` types; domain entities stay classes.
- Structured logging only: `_logger.LogWarning("Order {OrderId} rejected", id)` — never string
  interpolation inside the message template (kills log querying).
- Guard clauses at the top of methods; return early — no arrow-shaped nesting.
- No secrets in `appsettings*.json` — configuration comes from environment / Key Vault;
  `appsettings.Development.json` may hold local-only stubs.

## Data access

- Dapper over SQL Server: **always parameterized** queries — never string-concatenate or interpolate
  values into SQL (injection + plan-cache churn).
- Map results to DTOs / `record` types; do not leak raw `DataRow` / `dynamic` out of the data layer.
- Open connections late and dispose them — `await using var connection = ...`; let the pool do the rest.
- No N+1: never run a per-row query inside a loop. Batch the keys into one `IN`-style query, or use
  Dapper multi-mapping (`QueryAsync<A, B, ...>`) to pull the graph in a single round-trip.
- MongoDB / Cosmos DB Mongo API: filter on **indexed** fields and project only what you need; an
  unindexed predicate forces a full collection scan and burns RU.
- Mind RU cost — page large reads, avoid unbounded `Find({})`-style scans, and prefer point reads by
  partition/`_id` when the access pattern allows.

## Tests

- Name tests for the behavior under test (e.g. `Method_Scenario_ExpectedOutcome`); Arrange-Act-Assert,
  no logic (loops/ifs) inside a test.
- Follow whichever test framework and assertion/mocking libraries the project already uses — **don't mix
  frameworks**, and match the existing style rather than introducing a new one.
- The team owns its detailed test conventions (assertion library, mocking, integration-test approach,
  coverage targets) — record them in `copilot-instructions.md` or a `skills/team-local/` skill; this file
  does not mandate a specific toolset.
- New behavior ships **with** tests in the same change — test-first is encouraged, but the order is your call.
