# BIOrch Phase State Model Design Review

## 1. Problem Statement
The current representation of the "Current Phase" in `docs/PROJECT_STATE.md` is overloaded. When a phase (e.g., Phase 02) is `CLOSED`, it remains listed as the "Current Phase" until the next phase is explicitly initiated. This creates ambiguity: is the project in a transition state, or is it stalled?

## 2. Analysis of Existing Artifacts
- `governance/gemini/PHASE_INDEX.md`: Authoritative but mixes status terminology (e.g., `CLOSED` vs `COMPLETED`).
- `docs/PROJECT_STATE.md`: Uses an ambiguous "Current Phase" field.
- `docs/ROADMAP.md`: More explicit using `[COMPLETED]`, `[IN PROGRESS]`, `[PLANNED]`.

## 3. Proposed Governed State Model
To eliminate ambiguity, we propose replacing the singular "Current Phase" concept with an explicit three-part model in `PROJECT_STATE.md`:

### Explicit State Fields
1.  **`LAST_COMPLETED`**: The identifier of the most recently `CLOSED` phase in `PHASE_INDEX.md`.
2.  **`ACTIVE`**: The identifier of the phase currently in progress. If no phase is in progress (e.g., between phases), this is `NONE`.
3.  **`NEXT_PLANNED`**: The identifier of the next phase slated for initiation.

### Consistency Improvements
- Standardize all status labels across `PHASE_INDEX.md` and `ROADMAP.md` to:
    - `COMPLETED` (Replaces `FOUNDATION COMPLETE` and `CLOSED`)
    - `ACTIVE` (Replaces `IN PROGRESS` where applicable)
    - `PLANNED`
    - `DEFERRED`

## 4. Recommendations
1.  **Update `PROJECT_STATE.md`**: Implement the 3-part state model.
2.  **Harmonize `PHASE_INDEX.md`**: Update status labels for consistency with `ROADMAP.md`.
3.  **Governance Tooling**: Update `biorch-status` and `biorch-sync` to validate these new explicit states rather than relying on a potentially ambiguous "Current Phase".
