---
name: feature-story-search
description: "Search a Feature List for all User Stories linked to a specific feature, then analyze and generate recommendations. Use when: find user stories for feature, search feature list, get US IDs for feature, user story lookup, feature user stories, feature list search, recommendations from user stories, analyze user stories, feature analysis, US search, find stories linked to feature, ADO user stories by feature."
argument-hint: "Feature name to search for (e.g., 'Split Receivers by GC') — Feature List is loaded automatically from the project docs folder"
---

 **REQUIRED — do not skip:** Before producing any output (including questions, summaries, or drafts), you MUST load the Feature List using the `read` tool. Do not proceed until it is loaded.

Feature List source — apply the following fallback logic in order, using the path supplied by the project (for example `.github/docs/Feature initiation check list.txt`):
- **If the `.txt` exists**: read it directly and continue.
- **If the `.txt` does not exist but a `.docx` equivalent exists** (for example `.github/docs/Feature initiation check list.docx`): automatically read the `.docx` file as a binary file using the `read` tool, extract its plain-text content, save the result alongside it as a `.txt`, then use it and continue.
- **If neither file exists**: notify the user in the output and stop — *" Feature initiation check list not found. Please upload `Feature initiation check list.docx` to the `.github/docs/` folder so it can be converted for future use."* — then stop processing the request.

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use it as the authoritative source for terminology, role names, status values, and entity names when searching and analyzing user stories. If no such reference exists, derive terminology only from the provided Feature List and User Stories and keep it consistent — do not invent canonical terms.

# User Stories Search for Feature List

Search a Feature List for all User Story IDs linked to a specified feature, then analyze those stories and produce structured recommendations.

## When to Use

- Finding all User Story IDs associated with a specific feature from the Feature List
- Analyzing the content of those User Stories for patterns, gaps, and improvement areas
- Generating recommendations grounded in the content of linked User Stories
- Identifying patterns, gaps, or improvement areas across stories for a feature
- Auditing feature coverage (excluding Done stories)

## Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| `FEATURE_NAME` | The exact or approximate feature name to search for | Required |
| Feature List | Loaded automatically from the project-supplied path (see REQUIRED section above for fallback logic) | Required |

---

## Procedure

### Step 1 — Locate Feature in Loaded Feature List

Using the Feature List loaded at the start of this session, locate all entries related to `FEATURE_NAME`:
- Attempt an **exact match** on feature name first.
- If no exact match is found, fall back to a **partial/fuzzy match**.
  - If **one** partial match is found, proceed with it and note the match used.
  - If **multiple** partial matches are found, **stop and ask the user to clarify** which feature they mean — list all candidate feature names and their IDs for the user to choose from. Do not proceed until confirmed.
  - If **no match** is found at all, report "No matching feature found for the specified name" and stop.
- Extract all User Story IDs directly associated with the confirmed matched feature.
- **Exclude** any User Stories in **Done** state.

If no User Stories are found after matching, report "No User Stories found for the specified feature" and stop.

### Step 2 — List Found User Story IDs

Output the found User Story IDs clearly before proceeding to analysis:

```
**Found User Story IDs:**
- US-00123
- US-00456
- US-00789
```

### Step 3 — Analyze the User Stories

Read the content of each identified User Story and analyze for:
- **Patterns** — recurring themes, similar acceptance criteria, repeated actors or workflows
- **Gaps** — missing requirements, undefined edge cases, incomplete acceptance criteria
- **Areas for improvement** — unclear descriptions, missing story points, untested scenarios, conflicting requirements

### Step 4 — Generate Recommendations

Produce structured recommendations based solely on the analysis in Step 3:
- Every recommendation must trace back to one or more of the found User Stories
- Do not include recommendations not derived from the provided User Stories
- Format as bullet points or numbered list, grouped by category (Gaps / Improvements / Patterns)

---

## Output Format

```
**Feature:** <feature name>

**Found User Story IDs:**
- US-XXXXX
- US-XXXXX

**Analysis Summary:**
- Patterns: <observations>
- Gaps: <missing or incomplete areas>
- Areas for improvement: <specific items>

**Recommendations:**
1. <Recommendation grounded in US analysis>
2. <Recommendation grounded in US analysis>
```

---

## Constraints

- Only include User Story IDs **directly associated** with the specified feature.
- Exclude all User Stories in **Done** state.
- All recommendations must be grounded in the analyzed User Stories — do not invent or assume behavior.
- Respond in structured format (lists or bullet points).
- If a User Story ID is found but its content is inaccessible, note it as "Content not available" and skip it from analysis (but still list the ID).
- Use domain-specific terminology consistently. If a domain vocabulary reference is supplied, treat it as authoritative and do not substitute its terms with generic alternatives.
