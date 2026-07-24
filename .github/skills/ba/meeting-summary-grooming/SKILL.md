---
name: meeting-summary-grooming
description: "Analyze grooming (requirements refinement) call transcripts to extract tasks reviewed, story points assigned, and BA action items. Use when: grooming transcript, refinement call, sprint planning notes, story point extraction, SP estimation, BA actions from call, transcript summary, summarize grooming, extract story points, BA change items, grooming summary, grooming notes, refinement summary, estimation session, backlog refinement, extract SP from transcript. Handles Russian-language transcripts with automatic translation to English."
argument-hint: "Paste the grooming call transcript (and optionally: date, project name, participant list)"
---

# Grooming Transcript Analysis

Extract structured information from grooming (requirements refinement) call transcripts: tasks reviewed, story points assigned, and BA action items. Output is always in English — Russian transcripts are translated automatically.

## When to Use

- Summarizing a grooming or backlog refinement call
- Extracting story point estimates after an estimation session
- Identifying which tasks require BA changes or follow-up
- Producing a consolidated BA action list from call notes
- Clarifying open questions or ambiguities from the transcript

## Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| `TRANSCRIPT` | Full or partial grooming call transcript (text paste or attached file) | Required |
| `DATE` | Date of the call | Optional |
| `PROJECT` | Project or sprint name | Optional |
| `PARTICIPANTS` | List of participants and their roles | Optional |

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use the terminology defined there throughout the output. If no such reference exists, derive terminology only from the provided transcript and keep it consistent — do not invent canonical terms.

---

## Language Rule

- If any part of the transcript is in **Russian**, translate all extracted information into **English**.
- Output must be in **English regardless** of transcript language.
- Story points may be referenced in the transcript language rather than in English (Russian calls commonly use the local words for "points", "story points" and "estimate") — treat any such synonym as a story point value when estimation context is present.

---

## Procedure

### Step 1 — Identify Tasks

Scan the transcript for each distinct task, story, epic, or bug discussed. Use the most specific identifier available:
1. Jira/ADO ticket ID (e.g., `US-1234`, `BUG-567`)
2. Ticket URL or link
3. Title or description if no ID is present

Do **not** invent task identifiers. If none is stated, use a descriptive label like `[Unnamed task — <brief description>]`.

---

### Step 2 — Extract Story Points Per Task

For each identified task, extract:

| Field | Extraction Rule |
|-------|----------------|
| **Story points** | Numeric Fibonacci value (½, 1, 2, 3, 5, 8, 13, etc.), T-shirt size (XS, S, M, L, XL, XXL), or custom scale value — or "Not stated" if absent. Preserve the original format used in the call; do not convert between scales. |
| **Status** | `Final` — explicitly agreed in call; `Not finalized` — multiple values discussed without agreement; `Not stated` — no SP mentioned |
| **Estimator / Source** | Name or role of who assigned/confirmed the SP, or "Not stated" |
| **Multiple values** | If several SP values are mentioned for the same task, list **all** and mark as "Not finalized" unless one is explicitly confirmed as final |

**Trigger phrases for story points:** "SP", "points", "story points", and their equivalents in the transcript language — use when context indicates estimation.

**SP scale detection:** Identify which scale the team is using from the transcript context (Fibonacci numeric, T-shirt sizes, or custom). If mixed scales appear, note the inconsistency under Open Questions.

---

### Step 3 — Map Participant Roles

When participants are mentioned in the transcript:
- Map each participant to their role if it is **explicitly stated** in the transcript or provided in the `PARTICIPANTS` metadata.
- Known roles: `BA` (Business Analyst), `Dev` (Developer), `QA` (Quality Analyst), `PO` (Product Owner), `TL` (Tech Lead).
- If a participant's role is **not clearly identifiable**, record their name only and leave role as "Not stated" — do not infer or guess roles.
- Use mapped roles in the Estimator/Source field of Step 2 where applicable.

---

### Step 4 — Identify BA-Required Changes

For each task, determine whether the Business Analyst must make changes:
- **Yes** — if the transcript explicitly states changes, updates, clarifications, or revisions are needed from the BA
- **No** — if no BA action is mentioned
- List each required action as a concrete, actionable item (not a paraphrase of discussion)

---

### Step 5 — Capture Evidence

For each task, include a short supporting quote or concise paraphrase from the transcript that justifies the extracted SP value and BA action determination.

---

### Step 6 — Identify Open Questions / Ambiguities

Flag anything unclear that needs follow-up:
- Tasks mentioned without a clear identifier
- SP values that were discussed but never confirmed
- BA actions that were implied but not explicitly assigned
- Participants referenced without a clear role

---

## Output Format

### Summary

```
## Summary
- Total tasks reviewed: <number>
- Tasks with story points captured: <number>
- Tasks requiring BA changes: <number>
```

### Task Breakdown (one section per task)

```
### <Task ID or Name>
- Story points: <value or "Not stated">
- Status: <Final | Not finalized | Not stated>
- Estimator/Source: <name/role or "Not stated">
- BA changes required: <Yes | No>
- BA change details (if Yes):
  - <action item 1>
  - <action item 2>
- Evidence: "<short quote or concise paraphrase>"
```

### BA Action List (consolidated)

```
## BA Action List
- <Task ID/Name>: <required BA action> (deadline/priority if mentioned)
```

### Open Questions / Ambiguities

```
## Open Questions / Ambiguities
- <anything unclear that needs follow-up>
```

---

## Constraints

- **Do not invent** task IDs, story points, or BA actions. Use "Not stated" for missing information.
- If multiple SP values exist for the same task with no explicit agreement, list all and mark as "Not finalized".
- Keep evidence quotes concise — one sentence or a short paraphrase is sufficient.
- If `DATE`, `PROJECT`, or `PARTICIPANTS` are provided, include them as a header block before the Summary section.
- Use domain-specific terminology consistently. If a domain vocabulary reference is supplied, treat it as authoritative and do not substitute its terms with generic alternatives.
