---
name: biorch-validation
description: Standardize validation of completed work based on expected behavior and factual evidence.
---

# BIOrch Validation

## Purpose
Standardize the process of verifying completed implementation work to ensure it meets the defined criteria and functions as intended.

## When to Use
After implementation is complete and before review or phase closure.

## Inputs
- Expected behavior / Acceptance criteria.
- Implementation output (files, scripts, logs).

## Procedure
1. Review the expected behavior defined in the task.
2. Identify the required evidence to prove success.
3. Perform output inspection.
4. Execute permitted validation steps (e.g., test runs, if allowed by restrictions).
5. Compare actual vs expected results.
6. Assign a status: PASS, FAIL, or BLOCKED.
7. Document any limitations encountered.
8. Record the specific evidence used to reach the decision.

## Expected Outputs
A validation record detailing the outcome and evidence.

## Rules
- Never claim validation that was not actually performed.
- Successful file creation does not constitute successful validation.

## Boundaries
Validation must stay within execution mode limits (e.g., FILE-ONLY mode means no runtime test execution).

## Evidence / Traceability
Documented actual vs expected results.

## Future Refinement
Integration with automated CI/CD and test frameworks.
