---
name: skill-biorch-status
description: Define the future human-controlled BIOrch project-status synchronization workflow.
---

# BIOrch Project Status Synchronization

## Purpose
Maintain the local BIOrch governance state and, after explicit human confirmation, synchronize the resulting repository state to GitHub.

## When to Use
Triggered when the human explicitly requests:
> Update BIOrch project status

## Inputs
None specific other than the human trigger.

## Procedure
1. Inspect project state (`docs/PROJECT_STATE.md`, `governance/gemini/PHASE_INDEX.md`, task records, etc.)
2. Update local governance documentation based on completed work.
3. Show proposed changes (files changed, status updates, commit message).
4. Request and wait for explicit human approval.
5. Perform Git synchronization (add, commit, push) upon approval.

## Expected Outputs
- Updated local documentation (`docs/PROJECT_STATE.md`, `governance/gemini/PHASE_INDEX.md`).
- A commit pushed to GitHub.
- Completion record detailing commit ID and push result.

## Rules
- Human-triggered only.
- No automatic push.
- Explicit approval before commit/push.
- Evidence-based status.
- No source-code modification.
- Historical task records preserved.
- No force push or destructive Git operations.

## Boundaries
Does not rewrite history, does not modify application code.
Actual Git implementation is intentionally deferred to a future Gemini CLI task.

## Evidence / Traceability
Updates to `PROJECT_STATE.md` and `PHASE_INDEX.md`.

## Future Refinement
Implementation of the actual git synchronization logic.
