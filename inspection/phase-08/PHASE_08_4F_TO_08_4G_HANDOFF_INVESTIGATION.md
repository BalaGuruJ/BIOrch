# Phase 08.4F → 08.4G Handoff Ownership Decision Investigation

## 1. 08.4F → 08.4G Boundary Evidence
- **Consumer/Producer:** Contract `BIORCH-SYNTH-001` (Section 2, 3) defines the handoff from the 08.4F Join Gate to the 08.4G Result Synthesis phase.
- **Handoff Object:** `BIORCH-SYNTH-001` (Section 3) explicitly mandates the consumption of the `WorkflowResult` object produced by the 08.4F Join Gate.
- **Evidence Classification:** GROUNDED (Contractual) / PARTIALLY GROUNDED (Runtime Implementation).

## 2. Authoritative Producer/Consumer
- **Producer:** Phase 08.4F Join Gate.
- **Consumer:** Phase 08.4G Result Synthesis.
- **Evidence:** `contracts/synthesis/SYNTHESIS_CONTRACT.md` (Section 2).
- **Evidence Classification:** GROUNDED.

## 3. Synthesis Eligibility Ownership Evidence
- **Owner:** `BIORCH-SYNTH-001` (Section 4) explicitly assigns synthesis eligibility determination to the 08.4F Join Gate.
- **Contradiction:** While the contract *assigns* this to 08.4F, the implementation of `WorkflowResult` in `src/biorch/orchestration/result.py` does not currently include a `synthesis_eligible` field.
- **Evidence Classification:** PARTIALLY GROUNDED (Contractual assignment is clear, runtime support is missing).

## 4. Task Metadata Propagation Evidence
- **Current State:** `WorkflowResult` handles task outputs and status via `Dict[str, Any]` (`results`, `step_results`). It does not explicitly serialize the `Task` object or its full metadata (e.g., `is_essential`, `agent_id`) directly.
- **Contract Requirement:** `BIORCH-SYNTH-001` (Section 7) mandates preservation of `agent_id` and attribution.
- **Gap:** Implicit mapping between `step_results` dictionary and `Task` model is required, but explicit model-based propagation is absent.
- **Evidence Classification:** PARTIALLY GROUNDED (Requirement exists, mechanism is implicit/undefined).

## 5. Minimum Required Handoff Fields
As defined in `BIORCH-SYNTH-001` and required for synthesis:
- `task_id` (Attribution)
- `agent_id` (Attribution)
- `status` (Terminal status for synthesis logic)
- `findings` (Task output data)
- `artifacts` (Task output files)
- `errors` (Consolidated error list)

## 6. Contradictions between Current Runtime and SYNTHESIS_CONTRACT.md
- **Contradiction 1:** `SYNTHESIS_CONTRACT.md` (Section 3, 4) assumes `synthesis_eligible` is supplied by `WorkflowResult`, but `src/biorch/orchestration/result.py` defines no such field.
- **Contradiction 2:** `SYNTHESIS_CONTRACT.md` assumes an structured attribution mapping (`task_id`, `agent_id`, etc.), whereas the current `WorkflowResult` stores results in weakly-typed dictionaries (`results`, `step_results`).

## 7. Explicit HUMAN DECISIONS Still Required
1. **Handoff Schema Update:** Should `synthesis_eligible` be added to `WorkflowResult`, or should eligibility determination be moved into 08.4G?
2. **Task Metadata Preservation:** Should `WorkflowResult` be updated to include explicit `Task` attribution metadata (e.g., `task_id`, `agent_id`, `is_essential`) instead of relying on `step_results` dictionary lookups?

## 8. Safety of SYNTHESIS_CONTRACT.md Correction
The contract CANNOT be safely corrected now. The handoff object (`WorkflowResult`) is currently incomplete relative to the contract's requirements (`synthesis_eligible`, structured task metadata). The boundary definition in 08.4F must precede the correction of `SYNTHESIS_CONTRACT.md`.
