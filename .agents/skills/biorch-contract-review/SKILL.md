---
name: biorch-contract-review
description: Review BIOrch JSON and Python contracts against the architecture.
---

# BIOrch Contract Review

## Purpose
Review the BIOrch communication contracts to ensure they remain framework-neutral, strictly typed, and aligned with architectural principles.

## When to Use
When proposing changes to the `schemas/` directory or `src/biorch/core/` models.

## Inputs
- Proposed or existing contract files:
  - `agent.schema.json`
  - `task.schema.json`
  - `result.schema.json`
  - `tool.schema.json`
  - `workflow.schema.json`
  - Corresponding Python models.

## Procedure
Review the contracts for:
- Consistency
- Separation of concerns
- Framework neutrality
- Extensibility
- Traceability
- TabUI/PBIParser compatibility
- Coupling
- Security implications

## Expected Outputs
A review document summarizing adherence to or deviations from the architecture.

## Rules
- Do not modify contracts during review unless a separate implementation task explicitly requests it.

## Boundaries
Evaluation of the architectural boundaries represented by the schemas.

## Evidence / Traceability
The completed review findings artifact.

## Future Refinement
Automated schema validation pipelines.
