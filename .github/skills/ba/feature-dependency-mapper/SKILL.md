---
name: feature-dependency-mapper
description: "Analyze a feature from the Feature List and Azure DevOps User Stories to recommend items for the 'Depend on' column, with evidence from both sources. Use when: depend on column, feature dependencies, feature list dependencies, map dependencies, recommend dependencies, ADO feature dependencies, user story dependencies, feature action dependencies, dependency analysis, feature list analysis, cross-feature dependencies, depend on recommendations, feature dependency mapping."
argument-hint: "Feature name to analyze (e.g., 'Split Receivers by GC')"
---

 **REQUIRED — do not skip:** Before producing any output (including questions, summaries, or drafts), you MUST load the Feature List using the `read` tool. Do not proceed until it is loaded.

Feature List source — apply the following fallback logic in order, using the path supplied by the project (for example `.github/docs/Feature initiation check list.txt`):
- **If the `.txt` exists**: read it directly and continue.
- **If the `.txt` does not exist but a `.docx` equivalent exists** (for example `.github/docs/Feature initiation check list.docx`): automatically read the `.docx` file as a binary file using the `read` tool, extract its plain-text content, save the result alongside it as a `.txt`, then use it and continue.
- **If neither file exists**: notify the user in the output and stop — *" Feature initiation check list not found. Please upload `Feature initiation check list.docx` to the `.github/docs/` folder so it can be converted for future use."* — then stop processing the request.

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use it as the authoritative source for terminology, role names, status values, and entity names when analyzing dependencies. If no such reference exists, derive terminology only from the provided Feature List and User Stories and keep it consistent — do not invent canonical terms.

---

# Feature List Depend-On Generator

Analyze a named feature from the Feature List and its linked Azure DevOps User Stories to produce evidence-backed recommendations for the 'Depend on' column — one row per feature action.

## When to Use

- Populating the 'Depend on' column in the Feature List for a specific feature
- Identifying which feature actions depend on other features, modules, or services
- Substantiating dependencies with evidence from both the Feature List and ADO User Stories
- Reviewing cross-feature or cross-module dependency coverage

## Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| `FEATURE_NAME` | The exact name of the feature to analyze | Required |
| Feature List | The Feature List with 'Features and actions' column. Stored at the project-supplied path (see REQUIRED section above for fallback logic). | Required |
| Azure DevOps | Access to the ADO Feature item and its child User Stories | Required |

---

## Procedure

### Step 1 — Locate Feature in Loaded Feature List

- Using the Feature List loaded at the start of this session, locate the feature `FEATURE_NAME`.
- Extract **all entries** from the 'Features and actions' column for that feature.
- These entries are the rows to be analyzed — treat each as a distinct feature action.

### Step 2 — Collect Azure DevOps Evidence

- Identify the ADO Feature item for `FEATURE_NAME`.
- Retrieve all **direct child User Stories** (include all states unless the user specifies otherwise).
- For each User Story, note the ID, title, and relevant acceptance criteria or description content.

### Step 3 — Analyze and Map Dependencies

For each feature action from Step 1:
- Cross-reference the action's description against the collected User Stories.
- Determine whether the action depends on another feature, module, or service — look for:
  - References to other modules or systems in the action description
  - User Stories that mention integration points, shared data, API calls, or shared workflows
  - Acceptance criteria that require behavior from another feature or service
- Record the User Story IDs that provide evidence for each dependency.

**Do not infer or assume dependencies** not supported by both the 'Features and actions' column content and at least one User Story. If no dependency is found for an action, mark it as "No dependency identified".

### Step 4 — Synthesize Recommendations

For each feature action with an identified dependency:
- Name the recommended 'Depend on' item using the Feature List's existing naming (module, feature, or service name).
- Cite the supporting User Story IDs.
- Briefly describe the relationship if the evidence makes it clear.

### Step 5 — Output Results

Present all results in the table format below. Include **every** feature action from Step 1 — even those with no dependency found.

---

## Output Format

```
| Feature Action | Depend on (recommended) | Evidence Reference(s) |
|----------------|------------------------|-----------------------|
| <Action from Feature List> | <Related feature/module/service> | <US-XXXXX, US-XXXXX> |
| <Action with no dependency> | No dependency identified | — |
```

---

## Constraints

- Only recommend dependencies supported by **both** the 'Features and actions' column **and** at least one User Story.
- Do not infer or assume dependencies not found in the provided evidence.
- Do not modify any other columns in the Feature List.
- Do not reference UI controls (buttons, fields, dropdowns) unless explicitly stated in the requirements.
- If a User Story's content is inaccessible, note it as "Content not available" and skip it from evidence — but still list the ID if it was found.
- Use domain-specific terminology consistently. If a domain vocabulary reference is supplied, treat it as authoritative and do not substitute its terms with generic alternatives.
