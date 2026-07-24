---
name: meeting-summary-stakeholders-full
description: "Produce a clear, structured meeting summary from a transcript, raw notes, chat log, agenda, or attached files. Use when: meeting summary, meeting notes, summarize meeting, meeting recap, meeting minutes, executive summary, action items from meeting, decisions from meeting, key discussions, meeting transcript summary, stakeholder meeting notes, call summary, workshop summary, sprint review notes, kick-off notes."
argument-hint: "Paste or attach the meeting transcript, raw notes, chat log, or agenda"
---

# Meeting Summary

Produce structured, styled meeting summary notes from any input — transcript, raw notes, chat log, or agenda. Captures agenda, key discussions, decisions, unresolved questions, and action items in a consistent format.

## When to Use

- Summarizing any type of meeting: stakeholder calls, sprint reviews, kick-offs, workshops, design sessions
- Converting a raw transcript or chat log into executive-ready notes
- Extracting decisions and action items from an unstructured recording or notes file
- Producing a shareable summary after a call

## Inputs Accepted

| Input type | Examples |
|------------|---------|
| Transcript | Auto-generated or manual call transcript |
| Raw notes | Bullet points or free-text notes taken during the call |
| Chat log | Slack / Teams message thread from the call |
| Agenda | Pre-meeting agenda doc (use as scope reference) |
| Files | Any attached document with meeting content |

Use **only the provided information**. Do not invent details. If something is missing or not stated, write "Not specified".

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use the terminology defined there throughout the output. If no such reference exists, derive terminology only from the provided inputs and keep it consistent — do not invent canonical terms.

---

## Output Formatting Rules

Apply these rules to every output — no exceptions:

1. **Headers** must be all caps and bold: `**MEETING INFO**`, `**KEY DISCUSSIONS**`, etc.
2. Within each discussion topic, these labels must be bold: `**Topic:**`, `**Discussion points:**`, `**Options considered:**`, `**Constraints/risks:**`, `**Decisions:**`, `**Questions:**`
3. Do **not** use bold anywhere else in the output.
4. Do **not** use italics, underlines, tables, or special styling.
5. Use plain text with consistent bullet formatting throughout.
6. Every sentence must start with a capital letter.
7. Write action items as executable tasks starting with a verb (e.g., "Update the spec", "Schedule a follow-up").
8. Merge duplicate points — keep only unique items.
9. Prefer concrete names, dates, and numbers when available in the source.
10. Use domain-specific terminology consistently. If a domain vocabulary reference is supplied, treat it as authoritative and do not substitute its terms with generic alternatives.

---

## Extraction Rules

### Decisions
- List a decision only if it is **explicitly stated** or **clearly agreed upon** in the source.
- Do not infer decisions from discussion tone alone.
- Place each decision under the relevant discussion topic — not in a separate global section.

### Questions / Open Items
- List a question only if it is **unresolved by the end of the meeting**.
- Resolved questions become decisions or discussion points, not open questions.
- Place under the relevant topic.

### Action Items
- Capture all tasks assigned during the meeting.
- Format: `[Owner if stated]: <verb> <task> (deadline if stated)`
- If no owner is stated, omit the owner prefix.

---

## Output Structure (Use Exact Headers)

```
**MEETING INFO**
- Date:
- Duration:
- Title/topic:
- Purpose:
- Participants:

**AGENDA / SCOPE**
- Item 1:
- Item 2:
- Item 3:

**KEY DISCUSSIONS**
- **Topic:**
  - **Discussion points:**
  - **Options considered:**
  - **Constraints/risks:**
  - **Decisions:**
  - **Questions:**

**ACTION ITEMS**
- Action 1:
- Action 2:
- Action 3:
```

Repeat the `**Topic:**` block for each distinct discussion topic identified in the source.

If a sub-field (e.g., `**Options considered:**`, `**Constraints/risks:**`) has nothing to report, write "Not specified" rather than omitting the label — this keeps the structure consistent.

---

## Procedure

### Step 1 — Parse Inputs
- Identify the meeting date, duration, title/purpose, and participants from the source.
- Extract any explicit agenda items. If no agenda is provided, infer scope from the topics discussed.

### Step 2 — Group Discussions by Topic
- Cluster related discussion points under a single named topic.
- Name each topic concisely (3–6 words).
- For each topic, extract: discussion points, options considered, constraints/risks, decisions made, and unresolved questions.

### Step 3 — Extract Action Items
- Scan for assigned tasks, follow-ups, and commitments.
- Consolidate duplicates.
- Format each as an executable verb phrase with owner and deadline when stated.

### Step 4 — Apply Formatting Rules
- Apply all output formatting rules from the section above before writing the final output.
- Verify: no bold outside headers/labels, no tables, no italics; all sentences start with a capital letter.

### Step 5 — Write Output
- Use the exact output structure above.
- Do not add extra sections or sub-headings beyond those in the template.
