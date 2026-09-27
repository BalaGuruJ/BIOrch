# Phase State Model Validation Report

## 1. Executive Summary
The proposed three-part state model (LAST_COMPLETED, ACTIVE, NEXT_PLANNED) is a robust improvement over the existing "Current Phase" terminology. It provides a clearer lifecycle projection and better aligns with the governance model.

## 2. Model Representation
The proposed model correctly represents the current BIOrch lifecycle. It distinguishes past work from current effort and future planning, which reduces ambiguity.

## 3. Derivation from PHASE_INDEX.md
- **LAST_COMPLETED:** The most recent phase with status `CLOSED`.
- **ACTIVE:** The phase with status `IN_PROGRESS`.
- **NEXT_PLANNED:** The first phase with status `PLANNED`.

## 4. State Unification (CLOSED vs. COMPLETED)
- **Recommendation:** Unify to `CLOSED`. The current mixing of "FOUNDATION COMPLETE" and "CLOSED" is inconsistent. Authoritative state should use `CLOSED`.

## 5. Status: READY_FOR_CLOSURE
- **Recommendation:** Retain as a distinct authoritative lifecycle state. It is a necessary transition point for the governed closure workflow (Implementation -> Review -> Closure Evidence Verification -> Transition to CLOSED).

## 6. Command Implications
- **/biorch-close:** Must update the authoritative status in `PHASE_INDEX.md` from `READY_FOR_CLOSURE` to `CLOSED`.
- **/biorch-sync:** Should reconcile derived documentation based on the new `LAST_COMPLETED`, `ACTIVE`, `NEXT_PLANNED` projections derived from `PHASE_INDEX.md`.
- **/biorch-status:** Should report the new projection: LAST_COMPLETED, ACTIVE, NEXT_PLANNED.
- **/biorch-next:** Should determine the next action based on the `ACTIVE` phase or, if none are active, the `NEXT_PLANNED` phase.

## 7. Historical and Technical Impact
- **Historical Artifacts:** No impact. Historical evidence artifacts (TASK/RESPONSE/REVIEW/PHASE_CLOSURE) are immutable and must not be modified.
- **Git Synchronization:** Git synchronization *must* remain separate from documentation synchronization. The proposed state model is purely descriptive and does not require Git mutations for phase transitions.
- **"Current Phase" Terminology:** Multiple commands and documentation (e.g., `biorch-status.toml`) currently use "Current Phase". These will need to be refactored to use the new `ACTIVE` phase terminology.

## 8. Conclusion
The proposed state model is highly recommended for adoption. The primary implementation task will be refactoring the command-line interface to support the new state projection and unifying the phase status terminology within `PHASE_INDEX.md`.
