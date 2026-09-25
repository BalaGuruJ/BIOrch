---
name: biorch-investigation
description: Standardize read-only technical investigation and evidence gathering.
---

# BIOrch Investigation

## Purpose
Standardize read-only technical investigation to establish current state, identify gaps, and gather evidence before any implementation changes occur.

## When to Use
When exploring architecture, security, parsers, repository state, or integration points (e.g., architecture investigation, integration investigation).

## Inputs
- Specific investigation objective or question.
- Scope of files/components to analyze.

## Procedure
1. Inspect before modifying.
2. Establish the current state of the target system or codebase.
3. Identify relevant files and components.
4. Trace architecture or data flow.
5. Gather factual evidence.
6. Identify gaps or limitations.
7. Document findings and produce an investigation report.

## Expected Outputs
A detailed, factual investigation report.

## Rules
- Make no implementation changes.
- Investigation is evidence gathering, not implementation.
- Base all findings on collected evidence, not assumptions.

## Boundaries
Strictly read-only mode regarding application source code.

## Evidence / Traceability
The resulting investigation report or findings summary.

## Future Refinement
Standardized templates for different types of investigations (e.g., security vs architecture).
