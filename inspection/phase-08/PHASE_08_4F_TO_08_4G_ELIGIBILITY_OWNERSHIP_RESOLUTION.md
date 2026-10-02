# Phase 08.4F → 08.4G Eligibility Ownership Conflict Resolution

## 1. Executive Summary & Investigation Objective

This strictly read-only investigation resolves conflicting conclusions regarding `synthesis_eligible` ownership and the Phase 08.4F → Phase 08.4G handoff boundary. 

Recent inspection reports in `inspection/phase-08/` presented divergent interpretations:
- `PHASE_08_4F_TO_08_4G_HANDOFF_INVESTIGATION.md` found that `SYNTHESIS_CONTRACT.md` assigns eligibility determination to 08.4F, but noted runtime omission in `WorkflowResult`.
- `PHASE_08_4F_TO_08_4G_CONTRACT_DEFINITION.md` incorrectly placed 08.4G output structures (`task_attributions`, `aggregated_findings`) into the 08.4F upstream handoff.
- `PHASE_08_4F_TO_08_4G_INPUT_BOUNDARY.md` claimed `synthesis_eligible` is strictly an output of 08.4G and claimed `WorkflowResult` requires no modification.

This investigation evaluates all ten authoritative sources to ground every conclusion in contracted mandates and current runtime reality, explicitly distinguishing between:
- **Contractually required**
- **Runtime-supported**
- **Inferred**
- **Unresolved**

---

## 2. Examination of Authoritative Sources

### 2.1 Contracts (`SYNTHESIS_CONTRACT.md` & `ORCHESTRATOR_CONTRACT.md`)
1. **`contracts/synthesis/SYNTHESIS_CONTRACT.md`**:
   - **Section 2 (Architectural Position):** Specifies the canonical pipeline: `Parallel Worker Execution (08.4D) → Terminal Outcome Reconciliation (08.4E) → Deterministic Join Gate (08.4F) → Result Synthesis (08.4G) → Provenance Validation & Audit (08.4H)`. Mandates that 08.4G operates strictly downstream of 08.4F and strictly upstream of 08.4H.
   - **Section 3 (Authoritative Input Boundary):** Mandates that Phase 08.4G consumes exclusively `WorkflowResult` produced and handed off by Phase 08.4F. The section enumerates the incoming fields of `WorkflowResult`: `workflow_id`, `workflow_version`, `status`, `completed_tasks`, `failed_task`, `not_executed_tasks`, `results`, `step_results`, `errors`, and `provenance`. (Note: `synthesis_eligible` is NOT listed in this Section 3 enumeration).
   - **Section 4.1 (Eligibility Flag Verification):** Explicitly states: *"The 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`). If `synthesis_eligible == False`, synthesis MUST fail closed or produce a designated terminal failure result with no synthesized findings."*
   - **Section 4.2 (Terminal Status Compatibility):** Requires 08.4G to inspect workflow status and allow `PARTIAL` synthesis only if all failed tasks are classified as non-essential under `BIORCH-ORCH-001` Section 9.2.
   - **Section 7.2 (Attribution):** Mandates that every task record retain `agent_id`.
   - **Section 8 (Permitted Synthesis Transformations):** Explicitly permits ONLY: 1. Deterministic Aggregation (collating task findings into `aggregated_findings`); 2. Attribution Mapping (generating `task_attributions`); 3. Error Consolidation; 4. Metadata & Provenance Forwarding.
   - **Section 12 (Output Contract):** Mandates output as `SynthesisResult` conforming to `schemas/synthesis_result.schema.json`, which contains `synthesis_eligible: boolean`, `task_attributions`, `aggregated_findings`, etc.
   - **Section 14.1 & 14.2 (Conformance):** Mandates consuming exclusively `WorkflowResult` from 08.4F and enforcing fail-closed behavior when `synthesis_eligible` is false.

2. **`contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`**:
   - **Section 9.2.2:** *"Final synthesis/reconciliation validity belongs to the 08.4E join/reconciliation stage; 08.4D is responsible for execution-state classification only and MUST NOT attempt synthesis."*
   - **Section 12 & 13:** Defines structured orchestrator result carrying `workflow_id`, `workflow_version`, `status` (`SUCCESS`, `REJECTED`, `FAILED`, `NOT_EXECUTED`), completed/failed/skipped steps, step results, errors, provenance.
   - **Section 25.4 (Join Gate / Reconciliation):** Mandates that before final synthesis, the orchestrator MUST implement a deterministic join gate that performs 7 steps, ending with: *"7. Determine if synthesis is permitted based on the orchestration policy."*

### 2.2 Current Codebase Runtime
1. **`src/biorch/orchestration/result.py` (`WorkflowResult`)**:
   - Defines `WorkflowResult` with: `workflow_id: str`, `workflow_version: str`, `status: WorkflowResultStatus`, `completed_tasks: List[str]`, `failed_task: Optional[str]`, `not_executed_tasks: List[str]`, `results: Dict[str, Any]`, `step_results: Dict[str, Any]`, `errors: List[str]`, `provenance: Dict[str, Any]`.
   - Does NOT contain `synthesis_eligible`.
   - Does NOT contain structured task models (e.g. `TaskAttribution`).

2. **`src/biorch/orchestration/orchestrator.py` (`DeterministicOrchestrator`)**:
   - Populates `WorkflowResult.step_results` as dictionaries containing `{"status": ..., "findings": ..., "errors": ...}`.
   - Populates `WorkflowResult.results` mapping `task_id` to `findings`.
   - Discards `artifacts` returned by `Result`.
   - Does not preserve `agent_id` or `is_essential` into `step_results` or `WorkflowResult`.
   - Does not compute or populate `synthesis_eligible`.

3. **`src/biorch/core/task.py` (`Task`)**:
   - Contains `task_id`, `objective`, `agent_id`, `inputs`, `dependencies`, `metadata`, `status`, `is_parallel_eligible`, `is_essential`.

4. **`src/biorch/core/workflow.py` (`Workflow`)**:
   - Contains `workflow_id`, `version`, `tasks: List[Task]`, `status`, `current_state`, `termination_info`.

5. **`governance/gemini/PHASE_INDEX.md`**:
   - Phase 08.4E (Join/Reconciliation) is marked `CLOSED`.
   - Phase 08.4F (Join Gate) is marked `PENDING`.
   - Phase 08.4G (Result Synthesis) is marked `PENDING`.

---

## 3. Resolution of Questions

### Question 1: Does SYNTHESIS_CONTRACT.md explicitly assign synthesis_eligible ownership to 08.4F?
**YES.**
- **Contractual Mandate:** `SYNTHESIS_CONTRACT.md` Section 4.1 states verbatim:
  > *"The 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`). If `synthesis_eligible == False`, synthesis MUST fail closed or produce a designated terminal failure result with no synthesized findings."*
- **Corroborating Orchestration Contract:** `ORCHESTRATOR_CONTRACT.md` Section 25.4 item 7 states that the join gate before final synthesis must:
  > *"Determine if synthesis is permitted based on the orchestration policy."*
- **Ownership Classification:** The determination of synthesis eligibility is explicitly owned by Phase 08.4F (the Join Gate).

### Question 2: Is synthesis_eligible an input to 08.4G or an output produced by 08.4G?
**It is an INPUT to 08.4G that is also reflected as an OUTPUT field of 08.4G's `SynthesisResult`.**
- **As an Input:** 
  - `SYNTHESIS_CONTRACT.md` Section 4.1 mandates that Phase 08.4G *evaluates* eligibility based on the 08.4F Join Gate output: if `synthesis_eligible == False`, synthesis fails closed.
  - 08.4G does not originate or own the eligibility policy decision; it receives the determination from the 08.4F Join Gate.
- **As an Output:** 
  - `SYNTHESIS_CONTRACT.md` Section 12 and `schemas/synthesis_result.schema.json` require `SynthesisResult` to expose `synthesis_eligible: boolean`.
  - The schema description explicitly confirms this origin: *"Flag indicating whether the workflow output met the 08.4F Join Gate eligibility criteria for synthesis."*
- **Distinction from Transformation:** `SYNTHESIS_CONTRACT.md` Section 8 explicitly limits 08.4G's permitted transformations to aggregation, attribution mapping, error consolidation, and provenance forwarding. Determining eligibility is not a permitted synthesis transformation.

### Question 3: What is the authoritative 08.4F → 08.4G handoff object?
**The authoritative handoff object is `WorkflowResult`.**
- **Contractual Mandate:** `SYNTHESIS_CONTRACT.md` Section 3 states:
  > *"Phase 08.4G MUST consume exclusively the `WorkflowResult` object produced and handed off by the Phase 08.4F Join Gate."*
  Section 14.1 reinforces:
  > *"It consumes exclusively `WorkflowResult` from Phase 08.4F."*
- **Negative Invariant:** Section 2 and Section 3 prohibit bypassing the 08.4F Join Gate or consuming raw worker outputs directly from 08.4D or 08.4E.

### Question 4: Which task metadata is actually available at that boundary?
**Analysis of boundary availability:**

1. **Present in current runtime `WorkflowResult`:**
   - `task_id`: Present as keys of `results` and `step_results`, and in `completed_tasks`, `failed_task`, `not_executed_tasks`.
   - Terminal `status`: Present in `step_results[task_id]["status"]`.
   - `findings`: Present in `step_results[task_id]["findings"]` and `results[task_id]`.
   - `errors`: Present in `step_results[task_id]["errors"]` and `errors: List[str]`.

2. **Absent from current runtime `WorkflowResult` (Lost at Handoff):**
   - `synthesis_eligible`: Absent from `WorkflowResult`.
   - `agent_id`: Defined on `Task`, but discarded during `orchestrator.py` execution; absent from `WorkflowResult`.
   - `is_essential`: Defined on `Task`, utilized in `orchestrator.py` control flow, but absent from `WorkflowResult`.
   - `artifacts`: Defined on `Result` (agent execution output), but discarded in `orchestrator.py` lines 332-337; absent from `step_results`.
   - `objective`, `inputs`, `dependencies`, `metadata`: Present on `Task`, absent from `WorkflowResult`.

3. **Required by `SYNTHESIS_CONTRACT.md` at or across this boundary:**
   - `synthesis_eligible` (Section 4.1): Required to enforce fail-closed entry.
   - `agent_id` (Section 7.2, Section 12): Required for `task_attributions`.
   - `artifacts` (Section 8.2, Section 12): Required for `task_attributions`.
   - `is_essential` classification (Section 4.2): Required by 08.4G to distinguish whether a `FAILED` workflow allows `PARTIAL` synthesis.

### Question 5: Are the existing investigation reports consistent with the authoritative contracts?
**No. Significant inconsistencies exist across the prior reports:**

1. **`PHASE_08_4F_TO_08_4G_HANDOFF_INVESTIGATION.md`**:
   - **Consistency:** High. Correctly identified that `SYNTHESIS_CONTRACT.md` assigns eligibility to 08.4F, identified that `WorkflowResult` is the authoritative handoff object, and correctly noted the runtime gap in `result.py`.

2. **`PHASE_08_4F_TO_08_4G_CONTRACT_DEFINITION.md`**:
   - **Consistency:** Low / Contradictory.
   - **Error:** Section 1 asserts that the 08.4F Join Gate must provide `task_attributions` and `aggregated_findings` to 08.4G.
   - **Contract Reality:** `SYNTHESIS_CONTRACT.md` Section 8 explicitly defines `task_attributions` and `aggregated_findings` as transformations performed **by** 08.4G, not inputs provided by 08.4F. This report conflated 08.4G's input boundary with its output schema.

3. **`PHASE_08_4F_TO_08_4G_INPUT_BOUNDARY.md`**:
   - **Consistency:** Low / Contradictory.
   - **Error 1:** Section 2 claims `synthesis_eligible` must NOT be moved upstream because it is an outcome of the synthesis process. This directly contradicts `SYNTHESIS_CONTRACT.md` Section 4.1 ("The 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`)") and `ORCHESTRATOR_CONTRACT.md` Section 25.4 item 7.
   - **Error 2:** Section 4 claims `WorkflowResult` does not require modification ("Does `WorkflowResult` Require Modification? NO."). This contradicts the contractual reality that `WorkflowResult` lacks `synthesis_eligible`, `agent_id`, `artifacts`, and `is_essential`.

### Question 6: Identify any contradiction between the contract and current runtime without proposing a fix.

1. **Contradiction on `synthesis_eligible` in `WorkflowResult`**:
   - `SYNTHESIS_CONTRACT.md` (Section 4.1) mandates that the 08.4F Join Gate determines `synthesis_eligible` and that 08.4G verifies this flag from the 08.4F output.
   - Current runtime `WorkflowResult` (`src/biorch/orchestration/result.py`) contains no `synthesis_eligible` field.
   - Current runtime `DeterministicOrchestrator` (`src/biorch/orchestration/orchestrator.py`) contains no logic computing `synthesis_eligible`.

2. **Internal Textual Ambiguity within `SYNTHESIS_CONTRACT.md`**:
   - Section 3 lists the fields carried by the incoming `WorkflowResult`: `workflow_id`, `workflow_version`, `status`, `completed_tasks`, `failed_task`, `not_executed_tasks`, `results`, `step_results`, `errors`, `provenance`. It omits `synthesis_eligible`.
   - Section 4.1 simultaneously states that the 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`) and that 08.4G verifies this flag.

3. **Contradiction on Attribution Metadata (`agent_id`)**:
   - `SYNTHESIS_CONTRACT.md` (Section 7.2, Section 12) mandates that synthesis output retain `agent_id` for every task.
   - `SYNTHESIS_CONTRACT.md` (Section 3) mandates that 08.4G consume exclusively `WorkflowResult` and not bypass the join gate.
   - Current runtime `WorkflowResult` does not capture `agent_id`.

4. **Contradiction on Failure Classification Metadata (`is_essential`)**:
   - `SYNTHESIS_CONTRACT.md` (Section 4.2) requires 08.4G to permit `PARTIAL` synthesis on a failed workflow only if all failed tasks were non-essential.
   - Current runtime `WorkflowResult` does not capture task essentiality.

5. **Contradiction on Task `artifacts`**:
   - `SYNTHESIS_CONTRACT.md` (Section 8.2, Section 12) requires `artifacts` in `task_attributions`.
   - Current runtime `DeterministicOrchestrator` discards `Result.artifacts` during result collection; `WorkflowResult` contains no task artifact data.

6. **Phase Lifecycle Status Contradiction**:
   - `SYNTHESIS_CONTRACT.md` references the 08.4F Join Gate as an operational upstream provider.
   - `governance/gemini/PHASE_INDEX.md` records Phase 08.4F as `PENDING`.

---

## 4. Explicit Classification Matrix

| Item / Concept | Status Classification | Basis / Evidence |
| :--- | :--- | :--- |
| 08.4F owns `synthesis_eligible` determination | **Contractually required** | `SYNTHESIS_CONTRACT.md` Sec 4.1; `ORCHESTRATOR_CONTRACT.md` Sec 25.4 item 7 |
| 08.4G consumes exclusively `WorkflowResult` | **Contractually required** | `SYNTHESIS_CONTRACT.md` Sec 3, Sec 14.1 |
| 08.4G outputs `SynthesisResult` with `synthesis_eligible` | **Contractually required** | `SYNTHESIS_CONTRACT.md` Sec 12; `schemas/synthesis_result.schema.json` |
| 08.4G constructs `task_attributions` & `aggregated_findings` | **Contractually required** | `SYNTHESIS_CONTRACT.md` Sec 8.1, 8.2 |
| `WorkflowResult` carries `workflow_id`, `status`, `step_results`, `provenance` | **Runtime-supported** | `src/biorch/orchestration/result.py` |
| `WorkflowResult` carries `synthesis_eligible` | **Unresolved** (Contradiction) | Required by contract Sec 4.1; absent in runtime `result.py` and omitted in contract Sec 3 list |
| `WorkflowResult` carries `agent_id`, `is_essential`, `artifacts` | **Unresolved** (Contradiction) | Required by contract Sec 4.2, 7.2, 12; absent in runtime `result.py` and `orchestrator.py` |
| Phase 08.4F provides `task_attributions` as input | **Inferred (False)** | Proposed in `CONTRACT_DEFINITION.md`; refuted by `SYNTHESIS_CONTRACT.md` Sec 8 |
| `WorkflowResult` needs no modification | **Inferred (False)** | Claimed in `INPUT_BOUNDARY.md`; refuted by runtime inspection of missing fields |
| Implementation of Phase 08.4F Join Gate | **Unresolved** | Marked `PENDING` in `governance/gemini/PHASE_INDEX.md` |

---

## Authoritative conclusion
1. **Ownership:** Synthesis eligibility determination (`synthesis_eligible`) is explicitly owned by Phase 08.4F (the Join Gate) under `SYNTHESIS_CONTRACT.md` Section 4.1 and `ORCHESTRATOR_CONTRACT.md` Section 25.4 item 7. It is an input evaluation flag to Phase 08.4G and an output property of `SynthesisResult`.
2. **Handoff Object:** The sole authoritative handoff object from 08.4F to 08.4G is `WorkflowResult` (`SYNTHESIS_CONTRACT.md` Section 3).
3. **Report Discrepancies:** Prior reports in `inspection/phase-08/` introduced conflicting conclusions by erroneously assigning 08.4G synthesis transformations to 08.4F (`CONTRACT_DEFINITION.md`) and by incorrectly claiming `synthesis_eligible` is an internal 08.4G decision while asserting `WorkflowResult` requires no changes (`INPUT_BOUNDARY.md`).
4. **Runtime Reality:** The current runtime `WorkflowResult` is incomplete relative to `SYNTHESIS_CONTRACT.md`: it lacks `synthesis_eligible`, `agent_id`, `is_essential`, and `artifacts`.

## Evidence supporting it
- `contracts/synthesis/SYNTHESIS_CONTRACT.md`: Section 2, Section 3, Section 4.1, Section 4.2, Section 7.2, Section 8, Section 12, Section 14.
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`: Section 9.2.2, Section 12, Section 13, Section 25.4 (specifically item 7).
- `schemas/synthesis_result.schema.json`: Properties definition for `synthesis_eligible` ("Flag indicating whether the workflow output met the 08.4F Join Gate eligibility criteria for synthesis").
- `src/biorch/orchestration/result.py`: Field definitions of `WorkflowResult` demonstrating absence of `synthesis_eligible` and task metadata.
- `src/biorch/orchestration/orchestrator.py`: Lines 152–483 demonstrating that `artifacts`, `agent_id`, and `is_essential` are not stored in `step_results`, and `synthesis_eligible` is neither computed nor assigned.
- `governance/gemini/PHASE_INDEX.md`: Status of Phase 08.4F recorded as `PENDING`.

## Remaining human decision(s)
1. **Handoff Schema Update Mechanism:** Authorize how `WorkflowResult` in `src/biorch/orchestration/result.py` will supply the contractually mandated metadata:
   - Option A: Add `synthesis_eligible: bool`, and enrich `step_results` (or add a structured field) with `agent_id`, `is_essential`, and `artifacts`.
   - Option B: Introduce an explicit handoff payload model that packages `WorkflowResult` alongside the original `Workflow` definition for downstream attribution lookup.
2. **Phase 08.4F Scope & Execution Order:** Authorize whether Phase 08.4F implementation must formally define and test the join gate output and `synthesis_eligible` computation prior to initiating Phase 08.4G.

## Whether SYNTHESIS_CONTRACT.md is currently safe to correct: YES/NO, with evidence
**NO.**
- **Evidence:**
  1. Phase 08.4F ("Join Gate") is currently `PENDING` in `governance/gemini/PHASE_INDEX.md`. Modifying `SYNTHESIS_CONTRACT.md` before Phase 08.4F establishes its definitive join gate boundary would decouple the contract from an active, verified producer.
  2. The handoff object `WorkflowResult` (`src/biorch/orchestration/result.py`) currently lacks `synthesis_eligible`, `agent_id`, `is_essential`, and `artifacts`. Correcting `SYNTHESIS_CONTRACT.md` to align with the current runtime would downgrade mandatory attribution and fail-closed safety requirements; conversely, correcting it to mandate new fields before the human architectural decision is made would encode unapproved schema changes.
  3. `SYNTHESIS_CONTRACT.md` contains an internal discrepancy between Section 3 (which omits `synthesis_eligible` from the `WorkflowResult` field list) and Section 4.1 (which mandates checking `synthesis_eligible` from 08.4F). Resolving this textual discrepancy requires the human architectural decision on Option A vs. Option B above.
