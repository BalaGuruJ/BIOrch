# Phase Closure Workflow Design Review

## 1. Governance Gap Identified
Currently, the BIOrch project tracks phase completion via evidence artifacts (`TASK.md`, `REVIEW.md`, `PHASE_CLOSURE.md`), but there is no governed, automated, or explicit command-driven mechanism to transition the authoritative phase state in `governance/gemini/PHASE_INDEX.md` from `READY_FOR_CLOSURE` to `CLOSED` and transition the project state to the next phase.

While evidence is generated correctly, updating the master index is a manual step, which risks inconsistency and human error.

## 2. Proposed Mechanism: `/biorch-close`

A dedicated governed command, `/biorch-close`, is required to provide a safe, human-controlled phase state transition.

### Proposed Command Workflow
1.  **Validation:** Scan `governance/gemini/phase-{ID}-*/` for the mandatory set of historical artifacts: `TASK.md`, `RESPONSE.md` (where applicable), `REVIEW.md`, and `PHASE_CLOSURE.md`.
2.  **State Verification:**
    *   Confirm the current phase state in `PHASE_INDEX.md` is `READY_FOR_CLOSURE` (or similar).
    *   Fail if mandatory artifacts are missing.
3.  **Proposal:** Present the intended modification to `governance/gemini/PHASE_INDEX.md`.
4.  **Human Approval:** Require explicit user confirmation before applying changes.
5.  **State Update:** Apply changes to `PHASE_INDEX.md`.
6.  **Immunity:** The command MUST NOT modify evidence artifacts, application source code, or contracts.
7.  **No Git:** The command MUST NOT automatically trigger `git` operations.

### Relationship to Existing Workflow
*   **`/biorch-sync`:** Remains exclusively for synchronizing derived projections (`docs/PROJECT_STATE.md`, `docs/ROADMAP.md`, `README.md`) *after* the authoritative state update.
*   **`/biorch-status`:** Continues to report state without modifying it.

## 3. Recommended Implementation Steps

### Command Configuration
Create `.gemini/commands/biorch-close.toml` with a structured prompt enforcing the safety boundary:
*   Use a prompt similar to `biorch-sync.toml`, emphasizing:
    *   Read-only audit of evidence.
    *   Strict enforcement of mandatory artifact existence.
    *   Explicit proposal of `PHASE_INDEX.md` changes.
    *   Required human approval phase.
    *   Strict modification boundary (only `PHASE_INDEX.md`).

### Skill Support
*   Create a new skill: `.agents/skills/biorch-phase-closure/` (if not already existing as a structure) to guide the agent in checking artifact completeness and integrity before recommending closure.

## 4. Conclusion
The introduction of `/biorch-close` completes the governed lifecycle, ensuring that phase state transitions are as rigorously controlled as implementation and review tasks.
