---
description: 'Layered explanation of selected code or the current file, grounded in real library behavior. Read-only — never modifies code. Use to understand unfamiliar code before changing it.'
agent: 'agent'
---

# /explain — purpose → step-by-step → types/state/side-effects → gotchas

Explain the selected code (or the current file if nothing is selected). This mode is read-only:
you build understanding, you do not change code.

## Steps

1. **Read for accuracy.** Read the selection and enough surrounding context to be correct, not
   just plausible: callers, the state it reads/writes, dependency injection wiring, and any tests
   that pin its behavior. If the behavior depends on code you have not read, read it before
   explaining.
2. **Explain in layers** (each layer one short block):
   - **One-line purpose** — what this code is for, in a single sentence.
   - **Step by step** — how it works in order, referencing the exact symbols and line numbers.
   - **Key types / state / side-effects** — the important types, what state it mutates, and what
     it touches outside itself (I/O, DB, network, logging, shared/static state).
   - **Gotchas and edge cases** — null/empty/boundary handling, error paths, concurrency,
     ordering assumptions, anything surprising or easy to break.
3. **For any third-party library's behavior**, if a Context7-style documentation MCP is
   configured, use it to fetch current library docs — resolve the library, read the relevant
   docs, and explain the real semantics. Otherwise, note that the library behavior is from
   training knowledge and may be version-stale — do not present versioned behavior as certain.
4. Keep it concise and concrete. Cite exact symbols and line numbers so the reader can follow
   along in the file. Do **not** modify code in this mode.

## Output contract

Four labelled layers (purpose / step-by-step / types-state-side-effects / gotchas), every claim
anchored to a symbol or line, and any library behavior backed by a Context7-style documentation
MCP lookup when one is configured — otherwise flagged as training-knowledge that may be
version-stale.
