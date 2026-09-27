# Status Synchronization Design Review

## Executive Summary
This report investigates the BIOrch project-status synchronization workflow, identifying inconsistencies and proposing a new authoritative source-of-truth model. The current system relies on multiple manual, disconnected documentation updates which lead to inconsistencies across governance files (`PHASE_INDEX.md`, `PROJECT_STATE.md`, `ROADMAP.md`).

## 1. Current Command Responsibilities
- `/biorch-status`: Provides a snapshot summary (read-only) of the environment and current Git/governance state.
- `/biorch-sync`: A multi-phase governed workflow for auditing, classifying, and committing changes. Heavily dependent on human approval.
- `/biorch-next`: Analyzes current state to propose the next governed action (read-only).

## 2. Identified Inconsistencies
- Documentation Desynchronization: `PHASE_INDEX.md` and `PROJECT_STATE.md` describe phase transitions, but require manual updates which can diverge.
- Roadmap Divergence: `ROADMAP.md` reflects intent, not necessarily the implemented state, which is often mismanaged during phase progression.
- Historical Artifact Pollution: There is no clear segregation between historical records (e.g., `RESPONSE.md` files) and the derived status documents (`PROJECT_STATE.md`), leading to confusion on what should be updated versus archived.

## 3. Proposed Source-of-Truth Model
1. **Authoritative Source:** `governance/gemini/PHASE_INDEX.md` is the only source-of-truth for phase state.
2. **Derived Projections:** `docs/PROJECT_STATE.md`, `README.md`, and `ROADMAP.md` MUST be treated as projections. The status synchronization workflow must be responsible for updating these projections based on `PHASE_INDEX.md`.
3. **Historical Evidence:** All `TASK.md`, `RESPONSE.md`, `REVIEW.md` files in `governance/gemini/` are immutable historical records. They must NEVER be rewritten.

## 4. Proposed Command Responsibility Model
- `/biorch-status`: Remains a read-only snapshot generator.
- `/biorch-sync`: Must be upgraded to perform the "Governance Synchronization" (Phase 3) automatically. It should read `PHASE_INDEX.md` and apply updates to `docs/PROJECT_STATE.md`, `README.md`, and `ROADMAP.md` where evidence allows.
- `/biorch-next`: Remains a read-only advisor.

## 5. Proposed /biorch-sync Workflow
1. **Audit:** Automated audit of project/Git state.
2. **Governance Update:** Automated check: Is `PHASE_INDEX.md` consistent with documented completion in phase records? If yes, sync projections (`PROJECT_STATE.md` etc.).
3. **Approval Gate:** Human approval required for all Git mutations and any modifications to projections.

## 6. Proposed Human Approval & Git Boundary
- **Governance Update:** Requires human approval if changes are suggested to documentation.
- **Git Commit/Push:** Explicitly gated as currently defined in `biorch-sync.toml`.

## 7. Required Changes
- Modify `biorch-sync.toml`: Add mandatory logic to parse `PHASE_INDEX.md` and update dependent documents (`PROJECT_STATE.md`, `README.md`, `ROADMAP.md`) before the Git commit phase.

## 8. Risks and Open Questions
- Automated parsing of markdown files in `biorch-sync.toml` may be brittle without structured data support.
- How to handle "partial" documentation updates if one file fails synchronization?

## 9. Recommended Implementation Sequence
1. Define a structured format for `PHASE_INDEX.md` to make automated parsing reliable.
2. Update `biorch-sync.toml` to include automated document synchronization.
3. Update governance docs (`docs/PROJECT_STATE.md`, etc.) to clearly mark them as "Derived from `governance/gemini/PHASE_INDEX.md`".
