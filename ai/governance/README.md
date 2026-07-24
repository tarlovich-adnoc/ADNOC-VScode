# ai/governance/ — usage telemetry and the review loop

This folder makes the team's AI usage **visible and reviewable**: who runs which agents,
how often, with what estimated cost — and a standing cadence that turns those numbers into
optimizations.

## What's here

| File | Purpose |
|---|---|
| `dashboard.py` | Reads `agent-runs.jsonl`, writes `dashboard.html` — runs/spend per agent/team. Zero deps (stdlib only). |
| `agent-runs.jsonl.example` | Sample telemetry — shows the schema. |
| `agent-runs.jsonl` | The live log agents append to — **committed**, created by the first agent run (absent on a fresh render = no agent has self-reported yet). |
| `dashboard.html` | Generated output of `dashboard.py` (gitignored). |
| `how-to-eval-a-skill.md` | The quality ladder for skills/instructions before they enter the standard. |
| `CHAMPIONS.md` | Who the team's champion is + the contact path. |

## The telemetry contract

Every agent run appends **exactly one JSON line** to `agent-runs.jsonl`:

```json
{
  "ts": "2026-06-08T17:00:22+00:00",
  "agent": "code-reviewer",
  "round": 1,
  "inTok": 1582,
  "outTok": 1866,
  "costUsd": 0.004128,
  "model": "copilot",
  "ok": true,
  "workflow": "pr-review",
  "team": "orders",
  "repo": "orders-api",
  "skills": ["dotnet-patterns"]
}
```

| Field | Required | Meaning |
|---|---|---|
| `ts` | yes | ISO 8601 UTC timestamp of the agent run |
| `agent` | yes | Agent name from `.github/agents/<name>.agent.md` |
| `round` | yes | Retry round (1 = first attempt) |
| `inTok` | yes (estimate) | Input tokens — **model-estimated**, not metered |
| `outTok` | yes (estimate) | Output tokens — **model-estimated**, not metered |
| `costUsd` | yes (estimate) | Estimated cost — **a relative signal, not a bill** |
| `model` | yes | Model identifier as reported by the IDE |
| `ok` | yes | `true` if the agent reported success, `false` if errored |
| `workflow` | recommended | The routine (`pr-review`, `qa-checklist`, `transcript-to-backlog`…) |
| `team` | recommended | Team slug (matches `CHAMPIONS.md`) — enables org-wide rollup |
| `repo` | optional | Repository slug |
| `skills` | optional | Which skills loaded that run — feeds post-ship skill eval (see `how-to-eval-a-skill.md`) |

**Honesty box — read once:** the line is written by the agent itself (self-reporting via the
`editFiles` tool); nothing physically enforces it, and GitHub Copilot does not expose real
token/billing numbers to the model — so `inTok`/`outTok`/`costUsd` are **estimates**. They are
good for *relative* comparisons (which agent is heavy, which team adopted what) — they are not
an invoice. The **authoritative** numbers are GitHub Copilot's own usage/seat reports, which
the CoE reads alongside this log. `/copilot-doctor` reminds you to check the log is growing.
**No per-developer identity is recorded in the schema** — it is per-agent/per-team/per-repo by
design. One honest caveat: because the log is committed, git authorship of the appended lines is
reconstructable — treat the data as pseudonymous and use it for team-level decisions only.

## Running the dashboard

```bash
# Default — reads ./agent-runs.jsonl, writes ./dashboard.html
python ai/governance/dashboard.py

# Custom paths (e.g. a combined multi-team log)
python ai/governance/dashboard.py --input data/all-teams.jsonl --output reports/2026-06-08.html
```

The output is a single self-contained HTML file — email it, paste it in a wiki.

## Bi-weekly review cadence

The dashboard alone changes nothing; the review cycle does:

1. **Every other Friday** — the champion runs `dashboard.py` (org-wide: the CoE reads each
   repo's **committed** log via REST — the same collection path as the learnings radar).
2. Identify the **top-3 heaviest agents** and any agent with a high failure share (`ok:false`).
3. Decide on **at least one optimization** — in the Copilot world that means:
   - tighten an agent's prompt or an instruction file to cut context (narrow `applyTo` masks);
   - split an over-broad skill so it stops loading where it isn't needed;
   - demote a noisy agent to opt-in, or fix its top failure mode (`/selfimprove`);
   - check AI-credit (token) consumption in the org's Copilot usage report for the heavy flows.
4. Record the decision in `optimization-log.md` (observation → hypothesis → action → result),
   and check the next review whether it moved the number.

This log is the evidence that usage is **reviewed**, not just collected.

## What is committed vs ignored

`agent-runs.jsonl` is **committed by design** — the committed log IS the org-wide collection
path (the CoE reads it via REST, no extra infrastructure). The shipped `ai/governance/.gitignore`
excludes only the generated `dashboard.html`. If your team's `optimization-log.md` contains
internal numbers, add it to the gitignore yourself — and tell the CoE where the numbers live
instead.
