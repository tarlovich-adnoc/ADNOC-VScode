---
name: verify
description: >
  Run this repo's verification gate (dependency restore, format check, static analysis,
  tests with coverage) and report build + test evidence. On a stack:none repo there is no
  application code, so the script reports nothing to run and verification is manual. Use ONLY
  when the user wants to verify or validate the working tree before a commit or PR, or asks
  to show passing build/test output. Not for casual "check this file" requests.
origin: ADNOC (adapted from a Flutter project's verify skill)
---

# Verify


Run the verification script for this repo and report the result with evidence.

## When to Activate

- User asks to "verify", "validate", or "run the checks" before committing
- User is about to open or update a PR and wants green build + test evidence
- A delivery prompt or agent needs proof the working tree passes the gate

## How

- Windows: `.\.github\skills\generic\verify\verify.ps1`
- macOS / Linux: `./.github/skills/generic/verify/verify.sh`

Gates run fail-fast in order: deps, format-check, static analysis, then test + coverage.

**Report any failure with the exact line of output that failed. No green output, no delivery.**
