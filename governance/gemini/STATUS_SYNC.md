# BIOrch Status Synchronization Governance

## Authoritative State
`governance/gemini/PHASE_INDEX.md` is the authoritative source for project phase status.

## Derived Projections
The following are derived documentation projections and must be synchronized with the authoritative state:
* `docs/PROJECT_STATE.md`
* `docs/ROADMAP.md`
* `README.md`

## Command Responsibilities

### /biorch-status (Read-Only)
- Reports current authoritative phase, completed phases, and next phase.
- Detects and reports documentation drift between authoritative state and derived projections.
- Performs NO file modifications.
- Performs NO Git mutations.

### /biorch-next (Read-Only)
- Identifies the next permitted governed action (implementation, review, closure, or transition).
- Identifies if human approval is required for the next action.
- Performs NO file modifications.

### /biorch-sync (Reconciliation)
- Detects inconsistencies in derived documentation (`PROJECT_STATE.md`, `ROADMAP.md`, `README.md`).
- Proposes a synchronization plan for human review.
- Requires explicit human approval before modifying derived projections.
- Performs NO Git mutations (commit, push).

## Immutable Evidence
The following historical artifacts MUST NOT be modified:
* `governance/gemini/**/TASK.md`
* `governance/gemini/**/RESPONSE.md`
* `governance/gemini/**/REVIEW.md`
* `governance/gemini/**/PHASE_CLOSURE.md`
* `contracts/**/*.md`

## Human Control Boundary
- Documentation synchronization and Git synchronization are strictly separate.
- Documentation updates require explicit human approval.
- Git operations (commit, push) require explicit human approval.

## Safety Rules
- No automatic push.
- No automatic commit.
- No implementation changes in application source code.
- No modification of historical evidence artifacts.
- No phase closure without governed lifecycle evidence (Implementation -> Review -> Closure).
- No modification of contracts.
- Synchronization only occurs *after* authoritative state update and human approval.
