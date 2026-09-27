---
name: skill-biorch-task
description: Standardize creation of implementation and investigation tasks for Gemini CLI.
---

# BIOrch Task

## Purpose
Standardize the creation of implementation and investigation tasks for Gemini CLI to ensure clarity, scope boundaries, and traceability.

## When to Use
When creating a new task specification (`TASK.md`) for Gemini CLI to execute a specific phase or sub-phase.

## Inputs
- Phase objective
- Desired scope
- Restrictions

## Procedure
Define the following in the task document:
- Task identifier
- Objective
- Scope
- Allowed files
- Prohibited actions
- Expected outputs
- Validation expectations
- Completion criteria
- Execution mode
- Clear distinction between investigation vs implementation

## Expected Outputs
A fully structured `TASK.md` artifact.

## Rules
- A task should be specific enough that another agent can execute it without guessing the intended scope.
- Maintain a clear distinction between an investigation task (evidence gathering) and an implementation task (code changes).

## Boundaries
Does not execute the task. It only creates the specification.

## Evidence / Traceability
The created `TASK.md` file.

## Future Refinement
Automated generation or templating of standard task definitions.
