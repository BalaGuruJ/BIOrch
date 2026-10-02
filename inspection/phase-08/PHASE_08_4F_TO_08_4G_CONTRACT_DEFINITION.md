# Investigation Report: Phase 08.4F → 08.4G Handoff Contract

## 1. Minimum Required Information (08.4F → 08.4G)
Based on `SYNTHESIS_CONTRACT.md` (Section 3, 12) and `BIORCH-ORCH-001`, the Join Gate must provide:
- `workflow_id` (Unique identifier)
- `workflow_version` (Version)
- `status` (Terminal workflow status: SUCCESS, FAILED, REJECTED, NOT_EXECUTED)
- `synthesis_eligible` (Gate-determined flag)
- `task_attributions` (Structured mapping for each task: `task_id`, `agent_id`, `status`, `findings`, `artifacts`, `errors`)
- `aggregated_findings` (Task-order-preserved finding collection)
- `errors` (Consolidated error list)
- `provenance` (Full execution provenance)

**Grounding:** GROUNDED (Directly required by `SYNTHESIS_CONTRACT.md` Sections 3 & 12).

## 2. Information Retained in Existing `WorkflowResult`
`WorkflowResult` (as defined in `src/biorch/orchestration/result.py`) currently satisfies:
- `workflow_id`
- `workflow_version`
- `status` (as `WorkflowResultStatus`)
- `errors`
- `provenance`

**Grounding:** GROUNDED.

## 3. Information Added/Preserved at 08.4F Boundary
- `synthesis_eligible`: Must be calculated at the Join Gate.
- `task_attributions`: Must be structured per-task, mapping `task_id`, `agent_id`, `status`, `findings`, `artifacts`, and `errors`. Currently, these are weakly typed in `WorkflowResult` (`results` and `step_results` dictionaries).
- Explicit preservation of `agent_id` and `is_essential` metadata from the `Task` object at the boundary.

**Grounding:** GROUNDED (Required by `SYNTHESIS_CONTRACT.md` Section 3, 4, 7).

## 4. Handoff Object Structure
Evidence supports extending `WorkflowResult` rather than inventing a separate handoff object. `SYNTHESIS_CONTRACT.md` explicitly names `WorkflowResult` as the consumer's expected input object.

**Grounding:** PARTIALLY GROUNDED (Supported by `SYNTHESIS_CONTRACT.md` text, but requires `WorkflowResult` schema update to satisfy requirements).

## 5. Representation of `synthesis_eligible`
`synthesis_eligible` must be represented as an explicit field within the handoff object (e.g., `WorkflowResult.synthesis_eligible`). This flag is calculated by the 08.4F Join Gate based on execution outcomes (Section 4 of `SYNTHESIS_CONTRACT.md`).

**Grounding:** GROUNDED (Required by `SYNTHESIS_CONTRACT.md` Section 4).

## 6. Remaining HUMAN ARCHITECTURAL DECISIONS
1. **Schema Update:** Authorize the expansion of `WorkflowResult` schema to include `synthesis_eligible` (boolean) and a more structured `task_attributions` list instead of relying on `Dict[str, Any]` for `results`/`step_results`.
2. **Implementation Responsibility:** Define where exactly in `DeterministicOrchestrator` (the current implicit Join Gate implementation) the `synthesis_eligible` calculation logic resides.
3. **Data Mapping:** Determine the mapping logic that extracts and structures task metadata (`agent_id`, `is_essential`, etc.) from the `Task` object into `WorkflowResult.task_attributions` during the final reconciliation phase of 08.4F.
