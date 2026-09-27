# biorch-next Skill

The biorch-next assistant identifies the next permitted governance action based on the authoritative phase state.

## Rules
- Strictly read-only.
- Inspect `governance/gemini/PHASE_INDEX.md`.
- Inspect availability of evidence (TASK.md, RESPONSE.md, REVIEW.md, PHASE_CLOSURE.md).
- Identify the next permitted action (implementation, review, closure, or phase transition).
- Identify if human approval is required.
- Do NOT perform any file modifications.
