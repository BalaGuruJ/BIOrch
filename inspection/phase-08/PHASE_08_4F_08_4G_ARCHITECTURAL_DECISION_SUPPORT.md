# Phase 08.4F → 08.4G — Architectural Decision-Support Investigation

## 1. Executive Summary

### 1.1 Purpose
This investigation provides a comprehensive, strictly read-only architectural decision-support package for human review and approval. It evaluates the architectural consequences, contract implications, runtime data flows, failure paths, backward-compatibility impacts, and future-phase boundaries for the two unresolved architectural alternatives connecting **Phase 08.4F (Join Gate)** to **Phase 08.4G (Result Synthesis)**:

- **Option A (Enriched `WorkflowResult`):** Enrich `WorkflowResult` with `synthesis_eligible: bool`, task attribution metadata (`agent_id`, `is_essential`), and worker `artifacts`, preserving `WorkflowResult` as the sole handoff object between Phase 08.4F and Phase 08.4G.
- **Option B (Separate/Composite Handoff Payload):** Retain `WorkflowResult` in its current generic form as the orchestrator's execution result, and introduce a distinct composite model (e.g., `JoinGatePayload` / `HandoffPayload`) at the Phase 08.4F boundary carrying the workflow definition, execution results, eligibility flag, and task artifacts to Phase 08.4G.

### 1.2 Governance Baseline
- **Phase 08.4E (Join/Reconciliation):** CLOSED (`governance/gemini/PHASE_INDEX.md`).
- **Phase 08.4F (Join Gate):** PENDING (`governance/gemini/PHASE_INDEX.md`).
- **Phase 08.4G (Result Synthesis):** PENDING (`governance/gemini/PHASE_INDEX.md`).
- **Architectural Selection Status:** Unresolved and pending human architectural decision. Neither option is selected, recommended, or implemented in this investigation.

---

## 2. Current Contract Boundary Analysis

### 2.1 Synthesis Contract (`contracts/synthesis/SYNTHESIS_CONTRACT.md`)
- **Authoritative Input Boundary (Section 3):** Mandates verbatim:
  > *"Phase 08.4G MUST consume exclusively the `WorkflowResult` object produced and handed off by the Phase 08.4F Join Gate."*
  Section 3 enumerates the incoming fields of `WorkflowResult`: `workflow_id`, `workflow_version`, `status`, `completed_tasks`, `failed_task`, `not_executed_tasks`, `results`, `step_results`, `errors`, and `provenance`.
  *(Fact: `synthesis_eligible` is absent from this enumerated field list).*
- **Synthesis Eligibility Rules (Section 4.1):** Mandates verbatim:
  > *"The 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`). If `synthesis_eligible == False`, synthesis MUST fail closed or produce a designated terminal failure result with no synthesized findings."*
- **Terminal Status Compatibility (Section 4.2):** Mandates that if `WorkflowResult.status == FAILED`, synthesis is permitted only if all failed tasks are classified as non-essential under `BIORCH-ORCH-001` Section 9.2.
- **Attribution Preservation (Section 7.2):** Mandates that every task record retain `agent_id`.
- **Permitted Transformations (Section 8.2):** Mandates generating `task_attributions` containing `artifacts`.
- **Conformance Criteria (Section 14.1):** Mandates that an implementation complies only when *"It consumes exclusively `WorkflowResult` from Phase 08.4F."*

### 2.2 Orchestrator Contract (`contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`)
- **Failure Classification (Section 9.2):** Distinguishes essential failure/timeout (immediate workflow termination) from non-essential failure/timeout (independent tasks continue, dependents blocked, workflow proceeds toward reconciliation).
- **Reconciliation Authority (Section 9.2.2):** Mandates: *"Final synthesis/reconciliation validity belongs to the 08.4E join/reconciliation stage; 08.4D is responsible for execution-state classification only and MUST NOT attempt synthesis."*
- **Orchestrator Result Definition (Section 12):** Requires returning a structured result communicating `workflow_id`, `workflow_version`, execution `status`, completed steps, failed step, skipped steps, step results, errors, and execution provenance.
- **Join Gate / Reconciliation Requirements (Section 25.4 item 7):** Mandates that before final synthesis, the join gate must:
  > *"7. Determine if synthesis is permitted based on the orchestration policy."*

### 2.3 Hard Architectural Constraints Identified
1. **Contractual Input Constraint:** `SYNTHESIS_CONTRACT.md` Section 3 and Section 14.1 create a hard constraint requiring `WorkflowResult` as the sole input object. 
   - Under **Option A**, this constraint is satisfied directly because `WorkflowResult` is enriched to carry the required fields.
   - Under **Option B**, this constraint is violated unless `SYNTHESIS_CONTRACT.md` is formally amended to define the composite handoff payload as the required input.
2. **Orchestrator Abstraction Constraint:** `ORCHESTRATOR_CONTRACT.md` Section 12 defines `WorkflowResult` as a generic workflow execution summary across both sequential (Phase 04) and parallel (Phase 08) workflows.
   - Under **Option A**, `WorkflowResult` absorbs synthesis-specific gatekeeping flags (`synthesis_eligible`) and specialist attribution requirements (`agent_id`, `artifacts`).
   - Under **Option B**, `WorkflowResult` remains a generic execution summary, and synthesis-specific concerns are confined to Phase 08.4F and 08.4G.

---

## 3. Runtime Responsibility Map

The following map traces every required handoff field from its runtime origin to its terminal destination, noting retention and loss points in the current codebase (`src/biorch/`):

| Required Field | Source of Truth | Current Runtime Location | Current Retention Point | Current Loss Point | Logical Owning Component | Option A Ownership Change | Option B Ownership Change |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `workflow_id` | `Workflow.workflow_id` (`core/workflow.py:16`) | `orchestrator.py:158` | `WorkflowResult.workflow_id` (`result.py:15`) | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `workflow_version` | `Workflow.version` (`core/workflow.py:17`) | `orchestrator.py:157` | `WorkflowResult.workflow_version` (`result.py:16`) | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `status` | Execution loop & `_is_rejection` | `orchestrator.py:180, 382, 456` | `WorkflowResult.status` (`result.py:17`) | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `synthesis_eligible` | Join Gate policy evaluation | Not computed anywhere | Not retained anywhere | **Entirely absent** | Join Gate (08.4F) | Owned by `WorkflowResult` | Owned by `HandoffPayload` |
| Task ordering | `Workflow.tasks` (`core/workflow.py:18`) | `workflow.tasks` index order | Implicit in `Workflow.tasks` sequence | Lost if only `WorkflowResult` passed | Join Gate / Synthesis | Reconstructed or stored in `WorkflowResult` | Reconstructed from `Workflow.tasks` in payload |
| `task_id` | `Task.task_id` (`core/task.py:18`) | `step_results` keys (`orchestrator.py:333`) | `WorkflowResult.completed_tasks`, `results`, `step_results` | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `agent_id` | `Task.agent_id` (`core/task.py:20`) | `orchestrator.py:88, 281` (used for resolution) | Not stored in `results` or `step_results` | **Discarded** after task dispatch | `DeterministicOrchestrator` / Join Gate | Copied into `WorkflowResult.step_results` | Extracted into `HandoffPayload` from `Workflow` |
| Task status | Worker `Result.status` & timeout logic | `step_results[tid]["status"]` (`orchestrator.py:291, 334, 352, 434`) | `WorkflowResult.step_results` (`result.py:22`) | None (Retained as string) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `findings` | Worker `Result.findings` (`core/result.py:17`) | `results[tid]`, `step_results[tid]["findings"]` (`orchestrator.py:332, 335`) | `WorkflowResult.results`, `step_results` | Cleared on failure (`orchestrator.py:435`) | Specialist Worker / Orchestrator | Unchanged | Unchanged |
| `artifacts` | Worker `Result.artifacts` (`core/result.py:18`) | Worker return (`orchestrator.py:282`) | **Never assigned** | **Discarded** in completion loop (`orchestrator.py:332–337`) | Specialist Worker / Join Gate | Copied into `WorkflowResult.step_results` | Aggregated into `HandoffPayload` |
| Per-task errors | Worker `Result.errors` (`core/result.py:19`) | `step_results[tid]["errors"]` (`orchestrator.py:353, 436`) | `WorkflowResult.step_results` | None (Retained) | Specialist Worker / Orchestrator | Unchanged | Unchanged |
| `is_essential` | `Task.is_essential` (`core/task.py:27`) | `orchestrator.py:293, 314, 342` | Not stored in `step_results` | **Discarded** during result construction | `Task` definition / Join Gate | Copied into `WorkflowResult.step_results` | Extracted into `HandoffPayload` from `Workflow` |
| Consolidated errors | Aggregated errors list | `errors` in `execute()` and `_create_terminal_failure()` | `WorkflowResult.errors` (`result.py:23`) | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |
| `provenance` | Execution metadata dict | `provenance` dict (`orchestrator.py:187, 388, 459`) | `WorkflowResult.provenance` (`result.py:24`) | None (Retained) | `DeterministicOrchestrator` | Unchanged | Unchanged |

---

## 4. Field-by-Field Handoff Analysis

### 4.1 Comparison Across Implementation Models

| Field | Current Working Tree Behavior | Option A Implementation Model | Option B Implementation Model |
| :--- | :--- | :--- | :--- |
| `workflow_id` | Present on `WorkflowResult.workflow_id`. | Transferred directly via `WorkflowResult.workflow_id`. | Transferred via `HandoffPayload.workflow_result.workflow_id` or `HandoffPayload.workflow_id`. |
| `workflow_version` | Present on `WorkflowResult.workflow_version`. | Transferred directly via `WorkflowResult.workflow_version`. | Transferred via `HandoffPayload.workflow_result.workflow_version`. |
| `status` | Present on `WorkflowResult.status`. | Transferred directly via `WorkflowResult.status`. | Transferred via `HandoffPayload.workflow_result.status`. |
| `synthesis_eligible` | **Absent.** Not computed in `orchestrator.py`. | Computed by Join Gate logic in `orchestrator.py` and stored as `WorkflowResult.synthesis_eligible: bool`. | Computed by Join Gate and stored as `HandoffPayload.synthesis_eligible: bool`. `WorkflowResult` remains untouched. |
| Task ordering | Stored only in `Workflow.tasks` index. Lost if `WorkflowResult` is passed alone. | Must be preserved in `WorkflowResult` (e.g., via an ordered `task_attributions` list or ordered keys in `step_results`). | Derived directly from `HandoffPayload.workflow.tasks` sequence. |
| `task_id` | Present in `results` and `step_results` keys. | Transferred via `WorkflowResult.step_results` keys or structured records. | Transferred via `HandoffPayload` task attribution records. |
| `agent_id` | **Discarded.** In `Task.agent_id`, not in `WorkflowResult`. | `orchestrator.py` copies `task.agent_id` into `WorkflowResult.step_results[task_id]["agent_id"]`. | Extracted from `HandoffPayload.workflow.tasks` during Join Gate handoff construction. |
| Task status | Present in `step_results[task_id]["status"]`. | Transferred via `WorkflowResult.step_results`. | Transferred via `HandoffPayload.step_results` or attribution records. |
| `findings` | Present in `WorkflowResult.results` and `step_results`. | Transferred via `WorkflowResult.results` / `step_results`. | Transferred via `HandoffPayload` task findings. |
| `artifacts` | **Discarded.** Exists in `Result.artifacts`, ignored in `orchestrator.py:332–337`. | `orchestrator.py:335` updated to store `result.artifacts` into `WorkflowResult.step_results[task_id]["artifacts"]`. | Join Gate collects `result.artifacts` and packages them into `HandoffPayload.artifacts`. |
| `is_essential` | **Discarded.** In `Task.is_essential`, not in `WorkflowResult`. | `orchestrator.py` copies `task.is_essential` into `WorkflowResult.step_results[task_id]["is_essential"]`. | Extracted from `HandoffPayload.workflow.tasks` by the Join Gate. |
| Consolidated errors | Present on `WorkflowResult.errors`. | Transferred directly via `WorkflowResult.errors`. | Transferred via `HandoffPayload.workflow_result.errors`. |
| `provenance` | Present on `WorkflowResult.provenance`. | Transferred directly via `WorkflowResult.provenance`. | Transferred via `HandoffPayload.workflow_result.provenance`. |

---

## 5. Failure / Eligibility Pathway Analysis

Tracing the six canonical workflow outcomes through current runtime and both options:

### 5.1 Case 1: All Tasks Succeed
- **Current Runtime:** `orchestrator.py:379` returns `WorkflowResult(status=SUCCESS, completed_tasks=[all], failed_task=None, not_executed_tasks=[])`.
- **Join Gate Evaluation:** All tasks reached terminal `SUCCESS`; provenance valid; no essential failures. Gate evaluates `synthesis_eligible = True`.
- **Synthesis Action:** Processes all task findings in declared order; produces `SynthesisResult(status=SUCCESS)`.
- **Option A Boundary:** `WorkflowResult(status=SUCCESS, synthesis_eligible=True, ...)` passed to synthesis.
- **Option B Boundary:** `HandoffPayload(workflow=workflow, workflow_result=result, synthesis_eligible=True, ...)` passed to synthesis.

### 5.2 Case 2: Non-Essential Task Fails
- **Current Runtime:** `orchestrator.py:348–355` logs failure in `step_results[tid]`, calls `_block_dependents(tid)`, and allows independent tasks to finish. When remaining tasks succeed, lines 379–382 return `WorkflowResult(status=SUCCESS)`, but `step_results[tid]["status"] == "FAILED"`.
- **Join Gate Evaluation:** Inspects failed tasks; verifies every failed task has `task.is_essential == False`. Reconciles overall status to permit partial synthesis. Gate evaluates `synthesis_eligible = True`.
- **Synthesis Action:** Under `SYNTHESIS_CONTRACT.md` Section 4.2 and Section 11, produces `SynthesisResult(status=PARTIAL)` containing findings from successful tasks and explicit failure records for incomplete tasks.
- **Option A Boundary:** `WorkflowResult(status=SUCCESS, synthesis_eligible=True, step_results={... contains is_essential=False ...})`. Synthesis verifies non-essentiality directly from `WorkflowResult`.
- **Option B Boundary:** `HandoffPayload` provides both `WorkflowResult` and `Workflow.tasks` (where `is_essential` resides). Join Gate records `synthesis_eligible=True`; synthesis reads essentiality from `HandoffPayload`.

### 5.3 Case 3: Essential Task Fails
- **Current Runtime:** `orchestrator.py:342–347` detects `task.is_essential == True`. Calls `_create_terminal_failure(terminal_status=FAILED, failed_task=tid)`. Blocks all pending tasks as `NOT_EXECUTED`. Returns `WorkflowResult(status=FAILED)`.
- **Join Gate Evaluation:** Essential failure detected. Gate evaluates `synthesis_eligible = False`.
- **Synthesis Action:** Under `SYNTHESIS_CONTRACT.md` Section 4.1 and Section 11, fails closed: produces `SynthesisResult(status=FAILED, synthesis_eligible=False, aggregated_findings=[])`.
- **Option A Boundary:** `WorkflowResult(status=FAILED, synthesis_eligible=False, failed_task=tid)`.
- **Option B Boundary:** `HandoffPayload(workflow_result=..., synthesis_eligible=False)`.

### 5.4 Case 4: Worker Timeout
- **Essential Timeout:** `orchestrator.py:280–300` detects timeout on essential task. Invokes `_create_terminal_failure(terminal_status=FAILED)`. Step status is `TaskStatus.TIMEOUT`. Join Gate evaluates `synthesis_eligible = False`. Synthesis fails closed with `FAILED`.
- **Non-Essential Timeout:** `orchestrator.py:301–303` marks step status as `TaskStatus.TIMEOUT`, calls `_block_dependents()`, and continues execution. Join Gate evaluates `synthesis_eligible = True`. Synthesis outputs `SynthesisResult(status=PARTIAL)` recording timeout in task attributions.
- **Option A Boundary:** Timeout status and essentiality are packaged in `WorkflowResult.step_results`.
- **Option B Boundary:** Timeout status is in `WorkflowResult.step_results`; essentiality is in `HandoffPayload.workflow.tasks`.

### 5.5 Case 5: Authorization or Validation Rejection
- **Validation Rejection:** Pre-execution check fails (`orchestrator.py:177`). Returns `WorkflowResult(status=REJECTED, completed_tasks=[], not_executed_tasks=[all])`.
- **Agent/Tool Rejection:** Runtime tool rejection detected via `_is_rejection(result)` (`orchestrator.py:344`). Returns `WorkflowResult(status=REJECTED)`.
- **Join Gate Evaluation:** Rejection detected. Gate evaluates `synthesis_eligible = False`.
- **Synthesis Action:** Per `SYNTHESIS_CONTRACT.md` Section 4.2: *"If `WorkflowResult.status == REJECTED`, synthesis MUST NOT execute; the output status MUST be `FAILED`."*
- **Option A Boundary:** `WorkflowResult(status=REJECTED, synthesis_eligible=False)`.
- **Option B Boundary:** `HandoffPayload(workflow_result=..., synthesis_eligible=False)`.

### 5.6 Case 6: Dependent Task Marked `NOT_EXECUTED`
- **Current Runtime:** When an upstream dependency fails or times out, `_block_dependents()` (`orchestrator.py:476–487`) marks all direct and transitive dependents in `step_results` as `WorkflowResultStatus.NOT_EXECUTED.value` with an explanatory error.
- **Join Gate Evaluation:** Verifies all blocked dependents reached terminal `NOT_EXECUTED` status.
- **Synthesis Action:** Per `SYNTHESIS_CONTRACT.md` Section 6, unexecuted tasks are recorded in `task_attributions` with status `NOT_EXECUTED`, empty findings, and error messages preserved.
- **Option A Boundary:** `WorkflowResult.step_results` conveys unexecuted statuses directly.
- **Option B Boundary:** `HandoffPayload` conveys unexecuted statuses directly.

---

## 6. Option A — Concrete Architectural Consequences

### 6.1 Architectural Separation & Coupling
- **Coupling:** High coupling between orchestration result tracking and synthesis requirements. `WorkflowResult`, originally designed in Phase 04 as a general execution summary, is modified to hold synthesis-specific fields (`synthesis_eligible`, `artifacts`, `agent_id`).
- **Encapsulation:** Single-object encapsulation. A single object traverses from orchestration completion through the Join Gate to Result Synthesis.
- **Join Gate Boundary:** The Join Gate operates either as a method inside `DeterministicOrchestrator` or as an in-place transformer of `WorkflowResult`. The handoff boundary remains physically typed as `WorkflowResult`.

### 6.2 Data Flow & Model Impact
- **Model Modifications:** `src/biorch/orchestration/result.py` must be modified. Requires adding `synthesis_eligible: bool = Field(...)` and formalizing `step_results` to guarantee presence of `agent_id`, `is_essential`, and `artifacts`.
- **Runtime Modifications:** `src/biorch/orchestration/orchestrator.py` must retain `result.artifacts` at lines 332–337 and populate `agent_id` and `is_essential` from `task` into `step_results` across all three construction points (lines 177, 379, 453).

### 6.3 Contract Alignment
- **`SYNTHESIS_CONTRACT.md`:** Highly aligned with the core mandate of Section 3 (*"consume exclusively the `WorkflowResult` object"*). Requires only a surgical text update to Section 3's field list to add `synthesis_eligible`.
- **`ORCHESTRATOR_CONTRACT.md`:** Section 12 should be updated to formally reflect `synthesis_eligible` in the orchestrator result definition.

---

## 7. Option B — Concrete Architectural Consequences

### 7.1 Architectural Separation & Coupling
- **Coupling:** Low coupling between orchestration and synthesis. `WorkflowResult` remains a generic execution summary for Phase 04 and Phase 08.4D. Synthesis-specific requirements are isolated to the Join Gate and Synthesis phases.
- **Encapsulation:** Multi-object / composite encapsulation. The handoff object is a composite container (`HandoffPayload` / `JoinGateOutput`) that packages execution results alongside workflow definition metadata.
- **Join Gate Boundary:** The Join Gate is established as an explicit, distinct architectural boundary component that takes `Workflow` and `WorkflowResult`, performs reconciliation and eligibility evaluation, and emits `HandoffPayload`.

### 7.2 Data Flow & Model Impact
- **Model Modifications:** `src/biorch/orchestration/result.py` is **NOT** modified. A new model (e.g. `JoinGatePayload`) is introduced in a new or existing module (e.g., `src/biorch/orchestration/join_gate.py`).
- **Runtime Modifications:** `src/biorch/orchestration/orchestrator.py` must still be modified to avoid discarding `Result.artifacts`, or must provide access to raw `Result` objects so the Join Gate can collect artifacts.

### 7.3 Contract Alignment
- **`SYNTHESIS_CONTRACT.md`:** Substantial contractual modification required. Section 3 and Section 14.1 explicitly prohibit consuming anything other than `WorkflowResult`. These sections must be rewritten to declare `HandoffPayload` as the authoritative input object.
- **`ORCHESTRATOR_CONTRACT.md`:** Section 25.4 must be updated to state that the Join Gate emits `HandoffPayload` rather than terminating with `WorkflowResult`.

---

## 8. Backward-Compatibility Analysis

### 8.1 Callers and Constructors of `WorkflowResult`
- **Constructors:** `WorkflowResult` is constructed strictly within `src/biorch/orchestration/orchestrator.py` at lines 177, 379, and 453. No external caller or agent constructs `WorkflowResult`.
- **Consumers:**
  - `tests/test_orchestrator.py` (asserts `result.status`, `result.completed_tasks`, `result.errors`)
  - `tests/test_parallel_dispatch.py` (asserts `result.provenance['execution_order']`)
  - `tests/test_08_4D_execution.py` (asserts `result.status`, `result.step_results[tid]["status"]`)
  - `tests/test_reconciliation.py` (tests `_reconcile_terminal_outcomes`)

### 8.2 Structural Compatibility Evaluation
- **Option A Compatibility:**
  - If new fields on `WorkflowResult` have default values (e.g., `synthesis_eligible: bool = False`), existing test fixtures and callers constructing or receiving `WorkflowResult` continue to pass without modification.
  - If `step_results` remains a `Dict[str, Any]` and new keys (`agent_id`, `artifacts`, `is_essential`) are added additively, existing assertions like `result.step_results["t1"]["status"] == "SUCCESS"` remain 100% valid.
  - If `step_results` is converted to a strict typed model without dictionary-like access, existing test lookups will break.
- **Option B Compatibility:**
  - Zero risk of regression for existing `WorkflowResult` callers. `WorkflowResult` remains untouched in both schema and runtime behavior.
  - Existing tests in `tests/test_orchestrator.py` and `tests/test_08_4D_execution.py` require zero fixture changes.

---

## 9. Data Integrity / Information Loss Analysis

Independent source-code verification confirms the five data loss points identified in earlier investigations:

```text
[Task Definition: agent_id, is_essential, inputs, metadata]
       │
       ▼ (used during dispatch & control flow in orchestrator.py)
[Worker Execution: produces Result(findings, artifacts, errors)]
       │
       ▼ (completion loop in orchestrator.py:332–337)
 ❌ LOSS POINT 1: Result.artifacts is ignored; never assigned to step_results.
 ❌ LOSS POINT 2: Result.metadata is ignored; never assigned to step_results.
 ❌ LOSS POINT 3: Task.agent_id is not copied into step_results.
 ❌ LOSS POINT 4: Task.is_essential is not copied into step_results.
 ❌ LOSS POINT 5: Task.objective, inputs, dependencies are not copied into WorkflowResult.
       │
       ▼ (WorkflowResult constructed)
[WorkflowResult: contains only task_id, status strings, findings, errors, provenance]
```

### 9.1 Verification of Specific Data Loss Points
1. **`Task.agent_id`:** Defined in `src/biorch/core/task.py:20`. Validated in `orchestrator.py:88`. Resolved in `orchestrator.py:281`. Discarded during completion aggregation (`orchestrator.py:332–337`). **Verified: Lost before `WorkflowResult` construction.**
2. **`Task.is_essential`:** Defined in `src/biorch/core/task.py:27`. Read in `orchestrator.py:293, 314, 342` for control flow. Discarded during result construction. **Verified: Lost before `WorkflowResult` construction.**
3. **`Result.artifacts`:** Defined in `src/biorch/core/result.py:18`. Populated by specialist tools. Completely omitted in `orchestrator.py:332–337`. **Verified: Lost during task completion handling.**
4. **`Result.metadata`:** Defined in `src/biorch/core/result.py:20`. Completely omitted in `orchestrator.py:332–337`. **Verified: Lost during task completion handling.**
5. **Task Definition Context (`objective`, `inputs`, `dependencies`):** Defined in `src/biorch/core/task.py`. Validated in `validate_workflow()`. Omitted from `WorkflowResult`. **Verified: Lost at `WorkflowResult` construction.**

---

## 10. Future Phase Boundary Implications

### 10.1 Phase 08.4H (Provenance Validation & Audit)
- **Contractual Mandate:** `SYNTHESIS_CONTRACT.md` Section 13 states: *"The resulting object MUST be passed intact to Phase 08.4H (Provenance Validation & Audit)."*
- **Option A Implication:** Phase 08.4H receives `SynthesisResult` whose provenance forwards the single `WorkflowResult.provenance` chain. The audit trail flows through one continuous model.
- **Option B Implication:** Phase 08.4H audits provenance across two distinct orchestration artifacts: `WorkflowResult.provenance` and `HandoffPayload.provenance`.

### 10.2 Phase 09 (Review Loops) & Phase 11 (BI Comparison)
- **Phase 09:** Will introduce maker/checker loops across agents. Keeping generic execution results separate from review/synthesis inputs (Option B pattern) or maintaining enriched self-contained result envelopes (Option A pattern) will establish the precedent for how multi-agent evaluation data is packaged.
- **Phase 11:** Performs semantic cross-platform reconciliation between Tableau and Power BI. Relies strictly on `SynthesisResult` outputs; neither option alters the terminal schema of `SynthesisResult`.

---

## 11. Contract Change Matrix

| Contract & Section | Current State | Option A Consequence | Option B Consequence | Repository Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `SYNTHESIS_CONTRACT.md` Section 3 (Input Boundary) | Mandates consuming exclusively `WorkflowResult`; lists fields omitting `synthesis_eligible`. | **REQUIRED CHANGE:** Add `synthesis_eligible` to the enumerated field list of `WorkflowResult`. | **REQUIRED CHANGE:** Rewrite section to mandate consumption of `HandoffPayload` instead of `WorkflowResult`. | `contracts/synthesis/SYNTHESIS_CONTRACT.md:45–58` |
| `SYNTHESIS_CONTRACT.md` Section 4.1 (Eligibility Verification) | Requires checking `synthesis_eligible` on 08.4F output. | Fully aligned. Field is read from `WorkflowResult.synthesis_eligible`. | Fully aligned. Field is read from `HandoffPayload.synthesis_eligible`. | `contracts/synthesis/SYNTHESIS_CONTRACT.md:63–67` |
| `SYNTHESIS_CONTRACT.md` Section 7.2 (Attribution) | Requires `agent_id` on all task records. | Fully aligned if `WorkflowResult` preserves `agent_id`. | Fully aligned if `HandoffPayload` preserves `agent_id`. | `contracts/synthesis/SYNTHESIS_CONTRACT.md:99–104` |
| `SYNTHESIS_CONTRACT.md` Section 14.1 (Conformance) | Conformance requires consuming exclusively `WorkflowResult` from 08.4F. | **NO CHANGE:** Conformance criterion remains accurate. | **REQUIRED CHANGE:** Conformance criterion must be updated to reference `HandoffPayload`. | `contracts/synthesis/SYNTHESIS_CONTRACT.md:194` |
| `ORCHESTRATOR_CONTRACT.md` Section 12 (Result Definition) | Defines `WorkflowResult` fields without `synthesis_eligible` or `artifacts`. | **POSSIBLY REQUIRED:** Clarify Section 12 to include `synthesis_eligible` in parallel workflows. | **NO CHANGE:** `WorkflowResult` remains as defined. | `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md:195–210` |
| `ORCHESTRATOR_CONTRACT.md` Section 25.4 (Join Gate) | Mandates Join Gate determine synthesis eligibility (item 7). | Aligned. Join Gate sets flag on `WorkflowResult`. | Aligned. Join Gate sets flag on `HandoffPayload`. | `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md:383–395` |

---

## 12. Runtime Change-Surface Matrix

| Component / File | Current State | Option A Consequence | Option B Consequence | Repository Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `src/biorch/orchestration/result.py` | Defines `WorkflowResult` with 10 fields; lacks `synthesis_eligible`. | **REQUIRED CHANGE:** Add `synthesis_eligible: bool = False`; enrich `step_results` structure. | **NO CHANGE:** File remains untouched. | `src/biorch/orchestration/result.py:11–37` |
| `src/biorch/orchestration/orchestrator.py` | Discards `artifacts` (lines 332–337); discards `agent_id` and `is_essential`. | **REQUIRED CHANGE:** Retain `artifacts`, `agent_id`, `is_essential` in `step_results`; compute `synthesis_eligible`. | **POSSIBLY REQUIRED:** Must retain or expose `Result.artifacts` so Join Gate can collect them. | `src/biorch/orchestration/orchestrator.py:330–355` |
| `src/biorch/orchestration/join_gate.py` | Does not exist (Phase 08.4F PENDING). | **POSSIBLY REQUIRED:** Implemented as an internal method in `orchestrator.py` or helper class. | **REQUIRED CHANGE:** Implemented as a distinct class emitting `HandoffPayload`. | `governance/gemini/PHASE_INDEX.md:20` |
| `src/biorch/core/task.py` | Contains `agent_id`, `is_essential`. | **NO CHANGE.** | **NO CHANGE.** | `src/biorch/core/task.py:14–29` |
| `src/biorch/core/result.py` | Contains `artifacts`, `findings`. | **NO CHANGE.** | **NO CHANGE.** | `src/biorch/core/result.py:11–22` |
| `src/biorch/core/workflow.py` | Contains `tasks: List[Task]`. | **NO CHANGE.** | **NO CHANGE.** | `src/biorch/core/workflow.py:12–19` |
| `schemas/synthesis_result.schema.json` | Specifies 08.4G output. | **NO CHANGE.** Targets this schema. | **NO CHANGE.** Targets this schema. | `schemas/synthesis_result.schema.json` |
| `schemas/synthesis_input.schema.json` | Does not exist. | **NOT REQUIRED.** | **POSSIBLY REQUIRED:** To validate composite payload. | Schema directory |

---

## 13. Test Impact Matrix

| Test Suite | Current Scope | Option A Consequence | Option B Consequence | Repository Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `tests/test_orchestrator.py` | Validates sequential execution and validation failures. | **NO IMPACT** if new fields have defaults; fixture updates if fields are mandatory without defaults. | **NO IMPACT.** `WorkflowResult` is unchanged. | `tests/test_orchestrator.py` |
| `tests/test_08_4D_execution.py` | Validates parallel timeouts, essential failure, and dependent blocking. | **NO IMPACT** if `step_results` dictionary structure remains backward-compatible. | **NO IMPACT.** `WorkflowResult` is unchanged. | `tests/test_08_4D_execution.py` |
| `tests/test_reconciliation.py` | Validates `_reconcile_terminal_outcomes`. | **NO IMPACT** unless reconciliation verifies enriched metadata. | **NO IMPACT.** | `tests/test_reconciliation.py` |
| `tests/test_result.py` | Validates `Result` model. | **REQUIRED CHANGE:** Add tests for enriched `WorkflowResult` serialization. | **NO IMPACT.** | `tests/test_result.py` |
| Future Phase 08.4F Tests | Join Gate tests (not yet created). | Tests verify `WorkflowResult` enrichment and eligibility flag calculation. | Tests verify `HandoffPayload` construction and eligibility flag calculation. | `governance/gemini/PHASE_INDEX.md:20` |
| Future Phase 08.4G Tests | Synthesis tests (not yet created). | Tests pass enriched `WorkflowResult` into `synthesize()`. | Tests pass `HandoffPayload` into `synthesize()`. | `governance/gemini/PHASE_INDEX.md:21` |

---

## 14. Unresolved Questions

The following questions cannot be resolved through code inspection and require human architectural decision:

1. **Architectural Scope of `WorkflowResult`:** Should `WorkflowResult` be the unified post-reconciliation container for all downstream consumers including synthesis (Option A), or should `WorkflowResult` remain strictly an execution-state summary while Phase 08.4F introduces an explicit composite handoff payload (Option B)?
2. **Artifact Preservation Strategy:** Where should `Result.artifacts` be stored when specialist workers complete? Should they be added to `WorkflowResult.step_results[task_id]["artifacts"]` (Option A), or should `DeterministicOrchestrator` maintain a separate artifact collection handed to the Join Gate (Option B)?
3. **Contract Rectification Timing:** Should `SYNTHESIS_CONTRACT.md` be updated before Phase 08.4F implementation begins, or should contract amendments be committed concurrently with Phase 08.4F closure?
4. **Join Gate Modularity:** Should Phase 08.4F Join Gate logic be implemented directly within `DeterministicOrchestrator` (e.g. `DeterministicOrchestrator.evaluate_join_gate()`) or as an independent module (`DeterministicJoinGate`) in `src/biorch/orchestration/`?

---

## 15. Human Architectural Decision Point

Architectural selection remains pending human approval.
This investigation does not select Option A or Option B.
