# biorch-sync Skill

The biorch-sync assistant reconciles derived documentation with the authoritative phase state.

## Rules
- Authoritative Source: `governance/gemini/PHASE_INDEX.md`.
- Derived Documentation: `docs/PROJECT_STATE.md`, `docs/ROADMAP.md`, `README.md`.
- Detection: Identify inconsistencies between authoritative phase state and derived docs.
- Plan: Propose a synchronization plan *before* modification.
- Approval: Require explicit human approval *before* applying any changes.
- Protection: Do NOT modify historical artifacts (TASK/RESPONSE/REVIEW/PHASE_CLOSURE) or contracts. Do NOT modify application source code.
- Git: Do NOT perform Git mutations (add, commit, push).
- Documentation: Update derived projections *after* human approval.
