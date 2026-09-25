---
name: biorch-review
description: Standardize independent review of implementation and investigation results.
---

# BIOrch Review

## Purpose
Provide a standardized, independent evaluation of completed implementation or investigation tasks against architectural, security, and contract requirements.

## When to Use
When evaluating a completed task's `RESPONSE.md` and validation results to determine acceptability.

## Inputs
- Original `TASK.md`
- `RESPONSE.md`
- Validation evidence

## Procedure
Review the work against:
1. Original task scope
2. Architectural boundaries and principles
3. Security policies
4. Defined contracts (Agent, Task, Result, etc.)
5. Quality of evidence
6. Correctness of implementation
7. Identified gaps
8. Introduced risks

Assign a possible outcome:
- APPROVED
- CHANGES_REQUIRED
- BLOCKED

## Expected Outputs
A completed `REVIEW.md` containing the findings and decision.

## Rules
- Review is not implementation.
- Do not silently fix or modify code during a review; request changes instead.

## Boundaries
Reviewers do not implement the required changes.

## Evidence / Traceability
The completed `REVIEW.md` document.

## Future Refinement
More granular checklists for specific review types (security, architecture).
