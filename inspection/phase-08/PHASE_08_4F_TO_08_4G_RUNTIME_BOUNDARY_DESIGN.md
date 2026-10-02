# Investigation Report: Phase 08.4F → 08.4G Runtime Boundary Design

## 1. Current `WorkflowResult` Construction Path
`WorkflowResult` is constructed in `DeterministicOrchestrator.execute()`:
1.  **Validation Failure:** In the initial validation check, returning a `WorkflowResult` with `WorkflowResultStatus.REJECTED`.
2.  **Terminal Failure:** In `_create_terminal_failure()` when essential tasks fail or time out.
3.  **Successful Completion:** At the end of `execute()`, aggregating `results`, `step_results`, and provenance.

## 2. Proposed Minimal Handoff Shape (Schema Extensions)
`WorkflowResult` must be updated in `src/biorch/orchestration/result.py`:
- `synthesis_eligible: bool`: (New) Gate-determined eligibility flag.
- `task_attributions: List[TaskAttribution]`: (New) Structured per-task mapping replacing/supplementing weakly typed `Dict[str, Any]` in `results`/`step_results`.
  - `TaskAttribution` Pydantic model: `{task_id: str, agent_id: str, status: str, findings: Any, artifacts: Any, errors: List[str]}`.

## 3. Field-by-Field Evidence (Requirement vs. Current Path)
| Field | Requirement (`SYNTHESIS_CONTRACT.md`) | Current Status (in `WorkflowResult`) |
| :--- | :--- | :--- |
| `synthesis_eligible` | Must be explicit flag (Section 4) | Missing |
| `task_attributions` | Structured mapping (Section 3, 12) | Weakly typed `step_results` dictionary |
| `agent_id` | Must retain task attribution (Section 7) | Implicit in `Task` definition, lost at handoff |
| `is_essential` | Critical for failure logic (Section 9.2) | Lost at handoff (only used in `orchestrator.py` runtime) |

## 4. Exact Runtime Insertion Points
- **Point A (Eligibility):** In `DeterministicOrchestrator.execute()` and `_create_terminal_failure()`, immediately after terminal reconciliation, calculate `synthesis_eligible` based on `WorkflowResult.status` and essential task failures.
- **Point B (Attribution):** Create a mapping function `_map_task_attributions(workflow, step_results)` called at construction time (`execute` end, `_create_terminal_failure`) to bridge the `Task` object definitions (including `agent_id` and `is_essential`) with the reconciled `step_results`.

## 5. Unresolved Architectural Questions
1. **Provenance Responsibility:** Should `synthesis_eligible` be part of `provenance` or a top-level `WorkflowResult` field? (Contract mandates top-level representation, this is settled by the contract but needs schema confirmation).
2. **Metadata Source:** Is `Task` object persistence sufficient for `task_attributions` mapping, or does `WorkflowResult` need to explicitly clone the required metadata?

## 6. Files Requiring Future Modification
- `src/biorch/orchestration/result.py`: Define `TaskAttribution` model and update `WorkflowResult` schema.
- `src/biorch/orchestration/orchestrator.py`: Implement `synthesis_eligible` logic and `_map_task_attributions` logic at handoff construction points.
