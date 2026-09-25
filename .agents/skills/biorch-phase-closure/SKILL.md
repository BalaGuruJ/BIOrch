---
name: biorch-phase-closure
description: Determine whether a phase or major task is ready for closure based on implementation and reviews.
---

# BIOrch Phase Closure

## Purpose
Evaluate all artifacts and tasks associated with a development phase to determine if it is ready to be formally closed.

## When to Use
When all implementation tasks for a phase are believed to be complete, and reviews have been conducted.

## Inputs
- Phase definition and goals.
- All related `TASK.md`, `RESPONSE.md`, and `REVIEW.md` documents.

## Procedure
Inspect the following:
1. The original task and phase definition.
2. The implementation result.
3. The validation records.
4. The review findings.
5. The presence of required artifacts.
6. Any unresolved issues.
7. Any known limitations.

Determine the state:
- NOT_READY
- READY_FOR_REVIEW
- READY_FOR_CLOSURE
- CLOSED
- BLOCKED

## Expected Outputs
A clear determination of the phase's status.

## Rules
- A phase is not complete merely because implementation files exist.
- Do not automatically change phase status without explicit evaluation of reviews and validation.

## Boundaries
Evaluation only. Does not perform the actual work needed to unblock a phase.

## Evidence / Traceability
Updates to `governance/gemini/PHASE_INDEX.md` (via human or status sync).

## Future Refinement
Automated checks for missing review documents before closure is permitted.
