# Investigation Report: Minimal Phase 08.4F → 08.4G Input Boundary

## 1. Minimal 08.4F → 08.4G Input Fields
08.4F (Join Gate) must provide to 08.4G (Synthesis):
- `workflow_id`: Unique execution identifier.
- `workflow_version`: Declared definition version.
- `status`: Reconciled terminal workflow status (`SUCCESS`, `FAILED`, `REJECTED`, `NOT_EXECUTED`).
- `step_results`: Raw per-step execution data (status, findings, errors for every declared step).
- `provenance`: Full execution history and join-gate metadata.

## 2. Fields That Must NOT Be Moved Upstream (08.4G Outputs)
- `task_attributions`: These must NOT be constructed by 08.4F. They are a *synthesis transformation* (collating raw status, metadata, and results).
- `aggregated_findings`: This is a structural transformation of raw task findings.
- `synthesis_eligible`: The *gate* determines if synthesis proceeds, but the *synthesis result status* is an outcome of the synthesis process itself based on input eligibility.

## 3. Evidence Traceability
| Field | Source | Responsibility |
| :--- | :--- | :--- |
| `workflow_id`, `version` | `ORCHESTRATOR_CONTRACT` | Produced by 08.4F |
| `status` | `ORCHESTRATOR_CONTRACT` | Produced by 08.4F |
| `step_results` | `WorkflowResult` / `ORCHESTRATOR_CONTRACT` | Produced by 08.4F |
| `provenance` | `ORCHESTRATOR_CONTRACT` | Produced by 08.4F |
| `task_attributions` | `SYNTHESIS_CONTRACT` (Sec 8.2) | **Created by 08.4G** |
| `aggregated_findings`| `SYNTHESIS_CONTRACT` (Sec 8.1) | **Created by 08.4G** |

## 4. Does `WorkflowResult` Require Modification?
**NO.** 
Based on a strict interpretation, `WorkflowResult` *already contains* the minimum input fields (`workflow_id`, `version`, `status`, `step_results`, `provenance`). 

The current implementation *lacks* explicit `Task` metadata preservation (`agent_id`, `is_essential`) inside `step_results`, which are required to construct the 08.4G outputs (`task_attributions`). However, the handoff *boundary* itself does not need a new object structure if `step_results` can be expanded to include the necessary `Task` metadata during 08.4F construction.

## 5. Remaining Human Architectural Decision
- **Metadata Preservation vs. Schema Extension:** Should we explicitly extend `WorkflowResult` to include `Task` metadata (like `agent_id`) directly in `step_results` at construction time in 08.4F, or should 08.4G look up this metadata from the `Workflow` definition? (The contract implies `Task` metadata must be *preserved*, suggesting it should be present at the boundary).
