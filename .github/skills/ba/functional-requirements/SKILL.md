---
name: functional-requirements
description: "Transform raw problem statements and clarification outputs into structured, traceable, prioritized functional requirements using MoSCoW prioritization and KATA-focused speed. Use when: write requirements, functional requirements, requirements analysis, requirements document, prioritize requirements, MoSCoW, MVP requirements, KATA requirements, system shall statements, traceable requirements, ASR, architecturally significant requirements, requirements from problem statement, requirements analyst, structured requirements, business rules extraction, integration requirements, AI/ML requirements."
argument-hint: "Paste the problem statement and/or clarification output to analyze"
---

# Requirements Analyst

Transform raw problem statements and clarification outputs into structured, traceable, prioritized functional requirements. Optimized for KATA-speed sessions — identifies the most architecturally significant requirements first.

## Before You Start

If the project supplies a domain vocabulary, glossary, or terminology reference (for example `.github/docs/domain-vocabulary.md` or an equivalent supplied by the user), read it first and use it as the authoritative source for entity names, role names, status values, and lifecycle states when writing requirements. If no such reference exists, derive terminology only from the provided inputs and keep it consistent across all requirements — do not invent canonical terms.

## When to Use

- Converting a problem statement into formal functional requirements
- Prioritizing requirements using MoSCoW for MVP scoping
- Identifying Architecturally Significant Requirements (ASRs) that drive design decisions
- Producing a traceable requirements document with source references
- Defining AI/ML requirements with model type and data needs

## Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| Problem Statement | Raw description of the problem to solve | Required |
| Clarification Output | Output from a Clarification Agent or stakeholder Q&A | Optional |

---

## KATA Focus: Speed and Prioritization

For time-bound sessions, the goal is **rapidly identifying and prioritizing the most architecturally significant requirements** — not an exhaustive document.

- **Focus on MUST HAVEs first.** Defer detailed analysis of SHOULD HAVE and COULD HAVE items.
- **Identify the Core User Journey.** What is the single most important end-to-end path a user will take? Detail those requirements first.
- **Be testable, not exhaustive.** Every requirement must be specific enough to test — but do not list every edge case. Focus on rules that impact the architecture.
- **ASRs are key.** Spend more time on requirements that heavily influence technology choice or design patterns (e.g., "real-time data sync", "offline-first capture", "AI-based prediction").

---

## Requirements Writing Standard

Write every functional requirement in this form:

> "The system SHALL [perform an action] so that [business value is achieved]."

Requirements that describe **HOW** (implementation details) are design decisions — keep them separate from requirements.

---

## Procedure

### Step 1 — Parse Inputs and Map Coverage

- Identify all capability areas mentioned in the problem statement.
- Map any clarification outputs to those capability areas.
- Note inferred requirements (logically necessary but not explicitly stated).

### Step 2 — Identify the Core User Journey

State the single most important end-to-end path a user will take. Requirements for this journey are detailed first and must all be MUST HAVE.

### Step 3 — Write Requirements by Category

Cover all applicable categories:

| Category | What to Capture |
|----------|----------------|
| **Functional** | What the system does |
| **Business Rules** | Constraints on how the system does it |
| **Integration** | How the system connects to external systems — include protocol and data format |
| **Data** | What data is created, stored, or processed |
| **AI/ML** | Where intelligent automation is needed (see AI/ML format below) |
| **Accessibility** | Multilingual, low-literacy, offline users |
| **Regulatory** | Mandatory compliance behaviors |

### Step 4 — Apply MoSCoW Prioritization

Assign each requirement a priority:

| Priority | Rule |
|----------|------|
| **MUST HAVE** | Without this, the solution fails its core purpose. Non-negotiable for MVP. |
| **SHOULD HAVE** | High value, expected by stakeholders, but solution can launch without it. |
| **COULD HAVE** | Nice to have — adds value but low cost of exclusion. |
| **WON'T HAVE** | Explicitly out of scope for this release; may be a future phase. |

### Step 5 — Apply Traceability Tags

Every requirement must reference its source:

| Tag | Meaning |
|-----|---------|
| `[PS]` | Directly from the problem statement |
| `[CA]` | Derived from Clarification Agent output |
| `[INFERRED]` | Logically inferred — state the inference reason |

### Step 6 — Define the MVP Boundary

An item belongs in the MVP if **all three** are true:
1. It is MUST HAVE priority
2. It is on the critical path to first user value delivery
3. Excluding it means the system cannot be used at all for its primary purpose

State the MVP boundary explicitly as a summary after the requirements list.

### Step 7 — Quality Checklist

Before finalizing, verify every item in this checklist:

- [ ] Every capability area from the problem statement is covered
- [ ] Every MUST HAVE requirement is testable
- [ ] No requirement contains "fast", "easy", or "user-friendly" without quantification
- [ ] AI/ML requirements include model type and data source
- [ ] MVP boundary is explicitly stated
- [ ] Every integration point has a protocol and data format noted

---

## AI/ML Requirement Special Format

For any requirement involving AI, additionally specify:

```
- Requirement: The system SHALL [action] so that [value]. [source tag]
- Why AI/ML (vs rule-based): <reason>
- Model type implied: <classification | regression | NLP | generative | computer vision | other>
- Training data needed: <description>
- Output / prediction: <what the model produces>
```

---

## Output Format

```
## Core User Journey
<Single sentence describing the primary end-to-end user path>

## Requirements

### MUST HAVE
- REQ-001: The system SHALL [action] so that [value]. [PS]
- REQ-002: The system SHALL [action] so that [value]. [CA]

### SHOULD HAVE
- REQ-010: The system SHALL [action] so that [value]. [INFERRED — reason]

### COULD HAVE
- REQ-020: ...

### WON'T HAVE (this release)
- REQ-030: ...

## MVP Boundary
<Explicit statement of what is and is not in the MVP>

## Quality Checklist
- [ ] All capability areas covered
- [ ] All MUST HAVEs testable
- [ ] No unquantified quality adjectives
- [ ] AI/ML requirements include model type and data source
- [ ] MVP boundary stated
- [ ] All integration points include protocol and data format
```
