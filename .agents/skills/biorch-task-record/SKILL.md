---
name: biorch-task-record
description: Maintain traceability of tasks, responses, validation, and reviews throughout the project lifecycle.
---

# BIOrch Task Record

## Purpose
Ensure that major work remains traceable from initial objective to final decision and project state.

## When to Use
Whenever documenting the lifecycle of a task to ensure historical preservation.

## Inputs
- Task details, response artifacts, validation, and review artifacts.

## Procedure
Ensure the traceability chain is intact:
```text
TASK
 ↓
RESPONSE
 ↓
VALIDATION
 ↓
REVIEW
 ↓
DECISION
 ↓
PROJECT STATE
```

Cover and verify the following components:
- Task identifier
- Objective
- Scope
- Gemini response
- Files changed
- Validation evidence
- Review findings
- Decision
- Phase relationship

## Expected Outputs
A fully traceable chain of markdown documents governing the task.

## Rules
- Historical task records should be preserved rather than silently rewritten.

## Boundaries
Documentation management and verification.

## Evidence / Traceability
The unbroken chain of referenced documents.

## Future Refinement
Scripts to validate the referential integrity of task records.
