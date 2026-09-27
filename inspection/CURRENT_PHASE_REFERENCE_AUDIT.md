# Current Phase Reference Audit

This audit identifies all remaining "Current Phase" (and equivalent) references in the repository to prepare for refactoring the project to use the new LAST_COMPLETED / ACTIVE / NEXT_PLANNED phase state model.

## Classification Guide
- **A**: ACTIVE LOGIC
- **B**: DERIVED DOCUMENTATION
- **C**: COMMAND LOGIC
- **D**: GOVERNANCE MODEL
- **E**: HISTORICAL ARTIFACT
- **F**: HISTORICAL/EXPLANATORY TEXT
- **G**: LEGITIMATE USAGE

## Audit Results

| File | Line/Context | Classification | Action | Reason |
| :--- | :--- | :--- | :--- | :--- |
| .gemini/commands/biorch-close.toml | L14, L36 | C | Yes | Refactor to use ACTIVE/PLANNED model. |
| .gemini/commands/biorch-review.toml | L6 | C | Yes | Refactor to display ACTIVE phase. |
| .gemini/commands/biorch-roadmap.toml | L7, L10 | C | Yes | Refactor to inspect ACTIVE phase. |
| .gemini/commands/biorch-task.toml | L6, L12 | C | Yes | Refactor to display/inspect ACTIVE phase. |
| docs/BIORCH_COMMAND_WORKFLOW.md | L90, L244 | B | Yes | Update documentation to reflect new model. |
| inspection/PHASE_CLOSURE_WORKFLOW_DESIGN_REVIEW.md | L15 | F | No | Historical design review. |
| inspection/PHASE_STATE_MODEL_DESIGN_REVIEW.md | L4, L8, L12, L29 | F | No | Historical design review. |
| inspection/PHASE_STATE_MODEL_FINAL_VALIDATION.md | L4, L25, L38-50 | F | No | Historical validation record. |
| inspection/PHASE_STATE_MODEL_VALIDATION.md | L4, L29 | F | No | Historical validation record. |

## Summary

1. **Total matches:** 25
2. **Matches requiring correction:** 10
3. **Matches that must remain unchanged:** 15
4. **Exact files that should be modified in the next correction:** 
    - `.gemini/commands/biorch-close.toml`
    - `.gemini/commands/biorch-review.toml`
    - `.gemini/commands/biorch-roadmap.toml`
    - `.gemini/commands/biorch-task.toml`
    - `docs/BIORCH_COMMAND_WORKFLOW.md`
5. **Whether the next correction can safely be limited to non-historical files:** Yes, the correction is limited to command logic and documentation, avoiding immutable historical inspection/design review files.
