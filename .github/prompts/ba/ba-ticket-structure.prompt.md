---
description: Scaffold the Azure DevOps Feature -> User Story -> Task hierarchy under an existing Epic (BA standard). A shortcut to the ba-ado-ticket-structure agent.
agent: 'agent'
tools: ['execute/runInTerminal', 'azure-devops/*']
---
# /ba-ticket-structure

A shortcut to the **`ba-ado-ticket-structure`** agent — all the naming, Area/Iteration and field rules
live there (one source of truth). Fill this in and it creates the hierarchy under an **existing Epic**,
behind an approval gate (nothing is written until you approve the planned tree).

```text
epicId: <number>
feature:
  isCR: <true|false>
  systemName: <text>
  functionalArea: <text>
  description: <text>
  scope: <text>            # required — becomes the Feature description
stories:
  - suffix: <optional>     # blank => story title is "[BA] <Feature Name>"
    tasks: <optional>      # omit => default bundle: Request Designs / Review Designs / Update Requirements / Approve requirements
```

Run the **`ba-ado-ticket-structure`** agent with the values above.
