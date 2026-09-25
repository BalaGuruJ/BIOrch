---
name: biorch-implementation
description: Standardize bounded implementation tasks based on an approved scope.
---

# BIOrch Implementation

## Purpose
Ensure that implementation tasks are executed within their bounded scope, preserving existing architecture and avoiding unrelated refactoring.

## When to Use
When executing an approved implementation task (i.e., writing code, updating logic) according to a predefined `TASK.md`.

## Inputs
- Approved `TASK.md` specification.

## Procedure
1. Start strictly from the approved task.
2. Inspect the existing implementation.
3. Identify affected files.
4. Implement the requested scope exactly as defined.
5. Preserve the current architecture and design patterns.
6. Avoid unrelated refactoring or "cleanups".
7. Document exactly which files were changed.
8. Document execution performed.
9. Report any limitations or issues encountered during implementation.

## Expected Outputs
- Modified source code / files.
- Summary of changes and execution record.

## Rules
- Do not silently expand implementation scope.
- Maintain deterministic-first principles.

## Boundaries
Must strictly adhere to the provided task scope. No opportunistic future-phase implementation.

## Evidence / Traceability
Files changed list and implementation summary in the corresponding `RESPONSE.md`.

## Future Refinement
Tooling to automatically verify implementation against the task boundaries.
