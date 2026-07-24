---
name: kb-documentation
description: "Generate Knowledge Base documentation from an Azure DevOps Feature and publish it to a project-supplied Confluence workspace. Use when asked to document a feature, create a KB article in Confluence, write release notes, or summarize ADO User Stories into user-facing documentation. Accepts Feature ID, link, title, or exported content."
argument-hint: "ADO Feature ID, URL, or title"
---

# ADO Feature Documentation Generator

## When to Use

- User provides an ADO Feature (ID, URL, title, or exported content)
- User asks to "document a feature", "create a KB article in Confluence", or "write release notes"
- User wants to summarize multiple User Stories into unified documentation
- User needs acceptance-criteria-driven documentation suitable for direct publishing

**Workspace Scope**: This skill publishes documentation to the Confluence workspace configured for the project (space key, parent page ID, and instance). If the project does not supply these values, ask the user for them before publishing, or fall back to generating Markdown for manual publishing.

## Inputs

- **Required**: ADO Feature (ID / URL / title / exported content)
- **Optional**: A specific subset of User Stories to include (default: all child User Stories)
- **Optional**: Confluence target (space key, parent page ID, instance) if not already configured for the project

## Data Source

Azure DevOps is the single source of truth. Retrieve:

- Feature title, description, and acceptance criteria
- All child **User Stories** (exclude Tasks, Bugs, Spikes, and other work item types)
- User Story acceptance criteria, descriptions, and relevant fields

## Procedure

### Step 1 — Retrieve the Feature

Fetch the Feature content from ADO, including:

- Title, description, acceptance criteria
- List of child work items (filter to User Stories only)

If the user specified a subset of User Stories, collect **only those**; otherwise collect all child User Stories.

### Step 2 — Read and Annotate Each User Story

For each User Story:

1. Read it thoroughly: title, description, acceptance criteria, and relevant fields.
2. Write a brief internal chain-of-thought note summarizing:
   - What the story changes or enables
   - Key behaviors, validations, and edge cases from the acceptance criteria
   - Any constraints or dependencies mentioned
3. Do not make assumptions or add information not present in the story.

### Step 3 — Compile Key Points

After processing all User Stories, compile the chain-of-thought notes into a structured list of key points, grouped by functional area if applicable.

### Step 4 — Synthesize Documentation

Using only the compiled key points (no new assumptions), draft the document following the Document Format section below.

### Step 5 — Final Verification

Before presenting the output, verify:

- [ ] No information was added beyond what the User Stories explicitly state
- [ ] No assumptions or hallucinations are present
- [ ] All acceptance criteria are reflected in requirements, behaviors, or edge cases
- [ ] Screenshot placeholders are inserted wherever UI steps or configuration screens are described
- [ ] The User Story summary table at the end is complete

### Step 6 — Publish to Confluence

**Before publishing, load the configured Confluence MCP tools** with `tool_search` if needed:

- `confluence_create_page`
- `confluence_update_page`

Do not call `confluence-cli`; this repository deliberately ships only the MCP path.


**Publishing workflow:**

1. **Show preview**: Display the complete generated documentation to the user
2. **Ask for confirmation**: Present the publishing details:
   - Target: the project-configured space and parent page (ask the user if not configured)
   - Page title that will be used
   - Brief summary of content being published
3. **Wait for approval**: Ask the user if they want to:
   - Publish directly to Confluence
   - Just generate the Markdown for manual publishing
   - Make changes before proceeding
4. If publishing to Confluence:
   - Use `confluence_create_page` or `confluence_update_page`; the server accepts Markdown content
   - If MCP read-only mode blocks the write, stop and point to `ai/SETUP-COPILOT.md`

   - Page title: Use the Feature name
   - Confirm successful publication with the page URL
5. If just generating Markdown:
   - Output the finalized document in Markdown format
   - Provide instructions for manual publishing to the target workspace

---

## Document Format

### Structure Rules

- Section titles → Heading 1 (`#`)
- Subsections → Heading 2 (`##`)
- Use plain Markdown; no HTML except for screenshot placeholders

### Required Sections

```
# [Feature Name]

# Overview
<Single short paragraph: what this feature is and why it matters.>

# Key Changes

## [Change Item 1 Name]
<Detailed description of this change, behaviors, validations, and edge cases.>

<screenshot placeholder if applicable>

## [Change Item 2 Name]
<Detailed description.>

... (repeat for each distinct functional change)

---

# User Stories Referenced

| ID | Title | Summary |
|----|-------|---------|
| US-XXXX | Story title | One-line summary |
```

> If the Feature contains **more than one User Story with a distinct functional change**, each distinct change gets its own `# Overview` + `# Key Changes` block instead of a single global pair.

### Confluence Configuration

**Target Workspace** (project-supplied — configure once per project, or ask the user):

- **Space Key**: the Confluence space key for the project
- **Parent Page ID**: the parent page under which KB articles are created
- **Instance**: the Confluence instance host

All documentation generated by this skill is scoped to the configured workspace. Pages will be created as children of the configured parent page.

---

## Screenshot Placeholders

Insert at the exact location in the document where a screenshot would appear:

```
<p><strong>[[SCREENSHOT REQUIRED: What to capture | Location: page/step name]]</strong></p>
```

Rules:

- Insert only where UI steps, configuration screens, or dashboards are described
- Do not fabricate UI details or invent screen layouts
- If a step is purely behavioral (no UI), omit the placeholder

---

## Constraints

**User confirmation required**

- **ALWAYS** show a preview of the content before creating, updating, or deleting any artifacts (Confluence pages, ADO work items, etc.)
- **ALWAYS** ask for explicit user confirmation before executing any CRUD operation
- Display:
  - What will be created/updated/deleted
  - Where it will be published (space, parent page, etc.)
  - A summary of the key changes or content
- Wait for user approval before proceeding

**Work item filtering**

- Include **only User Stories** (not Tasks, Bugs, Spikes, or other work item types).
- If a subset of User Stories was requested, include **only that subset**.

**Content accuracy**

- Never invent requirements. If something is unclear or missing, add it to an **Open Questions** section at the end using the format:
  > _Not specified in ADO: [question]_
- Acceptance criteria must be incorporated — do not omit them.
- If acceptance criteria are **missing** for a User Story, include a placeholder in the Open Questions section:
  > _Not specified in ADO: acceptance criteria for Story #XXXX_

---

## Use Cases

- Producing comprehensive, fact-based KB articles from multiple User Stories
- Ensuring stepwise, verifiable summarization for complex system features
- Creating unified feature overviews from granular ADO specifications
- Generating release notes or feature announcements from ADO Features
