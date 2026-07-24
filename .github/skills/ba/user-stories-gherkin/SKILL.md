---
name: user-stories-gherkin
description: "Convert provided documents (FSD, answer lists, meeting notes, mockups, screenshots, stakeholder responses) into unambiguous, testable requirements formatted as 'The system should…' statements and Gherkin scenarios for user stories. Use when: writing requirements, extracting requirements from documents, converting FSD to acceptance criteria, turning stakeholder answers into user story requirements, writing Gherkin scenarios, creating acceptance criteria, requirements elicitation, requirements traceability, business rules extraction, testable requirements, system should statements, AC from FSD, acceptance criteria from spec, requirements from meeting notes, requirements from answers, feature requirements, user story requirements, document to requirements, spec to AC."
argument-hint: "Paste or attach the source document(s) — FSD section, answer list, meeting notes, or mockups"
---

# Requirements Formulation for User Stories

Convert source documents into structured, traceable, testable requirements — "The system should…" statements with optional Gherkin scenarios — ready to paste into user stories.

## Before You Start

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use it as the authoritative source for entity names, role names, status values, and lifecycle states when writing requirements. If no such reference exists, derive terminology only from the provided documents and keep it consistent across all requirements — do not invent canonical terms.

## Core Rules

- **Derive only from provided documents.** Do not invent behavior. If something is assumed, label it explicitly and ask the user to confirm.
- **One behavior per requirement.** Split compound statements.
- **Testable means:** clear actor + trigger + behavior + measurable outcome. Reject vague terms like "fast," "user-friendly," "as needed," "appropriately."
- **Never change intent** when converting to Gherkin — scenarios must directly map to the normalized requirement.

---

## Step 1 — Inventory and Structure Input Sources

Identify what documents were provided and summarize their scope.

**Actions:**
- List each document with a short label (e.g., "FSD §3.2", "Answers #1–20", "MoM 2026-05-14")
- Note: actors, key workflows, data entities, integrations, constraints

**Output:** A short **Source Map** table like:

| Label | Document | Covers |
|-------|----------|--------|
| FSD §2–5 | Functional Spec v1.3 | Workflows, validations, roles |
| Answers | Stakeholder Q&A list | 20 clarification items |

---

## Step 2 — Extract Candidate Requirements

Scan documents for:
- Explicit needs: "must/should/shall", "needs to", "we want"
- Business rules: validation, eligibility, calculations
- Workflow steps: preconditions, triggers, outcomes
- Data requirements: fields, formats, retention rules
- Error and edge cases: invalid input, timeouts, missing data

Rewrite each item as a **single atomic candidate** without adding new behavior.

**Example:**
> Document: "If the user enters an invalid email, show an error and block submission."
> Candidate: "The system should prevent form submission when the email format is invalid and display an email validation error message."

**Output:** A de-duplicated list of candidate statements, each traceable to a source label.

---

## Step 3 — Normalize into "The system should…" Format

Convert each candidate to a standardized requirement:
- Start with **"The system should…"**
- Embed conditions inline: `…when [trigger]…` / `…if [condition]…`
- Keep one behavior per statement — split if combined
- Use **consistent terms** across all requirements (same name for roles, objects, statuses)

**Split example:**
> Combined: "The system should save the record and notify the user."
> R1: "The system should save the record when the user submits the form with all required fields completed."
> R2: "The system should notify the user after the record is saved successfully."

**Output:** Numbered, atomic, normalized requirements list.

---

## Step 4 — Convert Eligible Requirements to Gherkin

Apply Gherkin when the requirement has **observable behavior** with clear preconditions and outcomes.

**When to use Scenario Outline:** same behavior repeats across multiple inputs, roles, or statuses.
**Include negative paths** only where the document mentions validation errors or permission failures.

**Template:**
```gherkin
Scenario: <short description>
  Given <precondition / system state>
  When <actor action or system trigger>
  Then <expected observable outcome>
  And <additional outcomes>
```

**Output:** Gherkin scenarios placed directly below the requirement they map to.

---

## Step 5 — Add Acceptance-Quality Details

If documents specify any of the following, include them in the requirement or scenario:
- Field constraints (min/max length, allowed values, required/optional)
- Permission rules (who can perform what action)
- State transitions (status changes with before/after values)
- Error handling (exact messages, retry behavior, fallbacks)
- Integration behaviors (what is sent/received, when, to which system)

**If a detail is missing but required for testability:** do NOT invent it and do NOT stop to ask mid-process. Instead, **log it as a numbered gap question** and continue processing the remaining requirements. All gap questions are collected and delivered together at the end of Step 6.

**How to log a gap:**
> Q1 (Source: Answers #12, affects R3): What text should the system display when the email format is invalid — a generic message or a specific string?

**Output:** Requirements enriched with every document-backed constraint that is present; a running list of numbered gap questions to be included in the Step 6 bundle.

---

## Step 6 — Package for User Story Usage

Assemble the final output bundle:

```
R1 (Source: FSD §3.2): The system should …
  Scenario: …
    Given …
    When …
    Then …

R2 (Source: Answers #7): The system should …

---
Open Questions / Assumptions
Q1 (Source: Answers #12): Clarify whether [X] applies to [role Y] or all users.
A1 [ASSUMPTION — confirm]: The system assumes [Z] unless stated otherwise.
```

**Checklist before delivery:**
- [ ] Every requirement has a source reference
- [ ] No vague terms remain (fast, user-friendly, as needed, appropriate)
- [ ] All compound requirements are split
- [ ] Gherkin scenarios map 1-to-1 to their requirement without adding behavior
- [ ] All missing testability details are listed as questions, not invented

---

## Examples

### Example 1: Stakeholder Answer List → Requirements

User: "Here's a list of answers from stakeholders. Turn them into requirements for user stories."

1. Label the list "Answers #1–N" in the Source Map.
2. Extract each actionable behavior as an atomic "The system should…" statement.
3. Add Gherkin for any item with conditions or validation rules.
4. List targeted questions for any item lacking measurable outcome.

### Example 2: FSD Workflow Section → Gherkin AC

User: "Use this FSD workflow section to create acceptance criteria in Gherkin for the user story."

1. Outline workflow steps and actors as stated (no additions).
2. Write Given/When/Then for each step reflecting described state and outcome.
3. Add negative scenarios only where the FSD mentions exceptions or validations.
4. Attach each scenario to its corresponding "The system should…" requirement.

---

## Troubleshooting

**Requirements sound vague or untestable**
Cause: Source uses subjective language or lacks conditions/outputs.
Fix: Rewrite into observable behavior (trigger + outcome). Ask a focused question for any missing measurable detail (e.g., exact validation rule, error text, numeric threshold).

**Too many overlapping requirements**
Cause: Source document repeats the same behavior in multiple places.
Fix: De-duplicate in Step 2 — keep the most specific version and note the additional source reference.

**Gherkin scenario adds behavior not in the document**
Cause: "Then" clause introduces logic not explicitly stated.
Fix: Remove or replace with a question asking the user to confirm the intended behavior.
