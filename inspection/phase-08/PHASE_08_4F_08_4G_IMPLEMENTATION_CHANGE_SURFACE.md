# Phase 08.4F → 08.4G — Implementation Dependency & Change-Surface Investigation

## 1. Executive Summary

This strictly read-only investigation maps the exact implementation dependencies, runtime data flows, data loss points, and change surfaces for connecting **Phase 08.4F (Join Gate)** to **Phase 08.4G (Result Synthesis)**.

### Current Governance Baseline
- **Phase 08.4E (Join/Reconciliation):** CLOSED.
- **Phase 08.4F (Join Gate):** PENDING.
- **Phase 08.4G (Result Synthesis):** PENDING.
- **Architectural Status:** Two architectural options have been proposed to resolve the handoff boundary:
  - **Option A:** Enrich `WorkflowResult` so that it directly contains all metadata, eligibility flags, and attribution data required by `SYNTHESIS_CONTRACT.md`.
  - **Option B:** Introduce a separate or composite handoff payload model (`HandoffPayload` / `JoinGateOutput`) that packages execution results alongside workflow definition metadata, retaining `WorkflowResult` in its current form.
- **Investigation Mandate:** This investigation does **NOT** select, favor, or implement either option. It establishes factual evidence, classifies the change surfaces, and identifies unresolved questions to support human architectural decision-making.

---

## 2. Current Runtime Handoff & Data Flow Analysis

### 2.1 Current Runtime Pipeline
The working-tree runtime execution flow in `src/biorch/` currently proceeds as follows:

```text
Workflow (tasks: List[Task])
       ↓
DeterministicOrchestrator.execute()
       ↓
ThreadPoolExecutor worker dispatch: execute_task(task: Task)
       ↓
DeterministicAgentExecutor.execute(task: Task)
       ↓
Result (task_id, status, findings, artifacts, errors, metadata)
       ↓
DeterministicOrchestrator completion loop / _create_terminal_failure()
       ↓
_reconcile_terminal_outcomes(workflow, step_results)
       ↓
WorkflowResult (workflow_id, version, status, completed_tasks, failed_task, not_executed_tasks, results, step_results, errors, provenance)
       ↓
[08.4F Join Gate — PENDING]
       ↓
[08.4G Result Synthesis — PENDING]
```

### 2.2 Trace of Specific Fields Across Runtime Components

| Field | Source Location | Processing in `DeterministicOrchestrator` | Retention in `WorkflowResult` | Data Status at 08.4F Boundary |
| :--- | :--- | :--- | :--- | :--- |
| `Task.agent_id` | `src/biorch/core/task.py` (`Task.agent_id: str`) | Inspected in `validate_workflow()` (line 88) and `execute_task()` (line 281) for agent resolution via `AgentResolver.resolve(task.agent_id)`. | **DISCARDED.** Not included in `WorkflowResult.results` or `WorkflowResult.step_results`. | **LOST.** 08.4G cannot perform attribution mapping without accessing original `Task`. |
| `Task.is_essential` | `src/biorch/core/task.py` (`Task.is_essential: bool`) | Evaluated during timeout (line 293), exception (line 314), and failure (line 342) to trigger `_create_terminal_failure()` vs `_block_dependents()`. | **DISCARDED.** Neither `_create_terminal_failure()` nor line 379 stores `is_essential`. | **LOST.** 08.4G cannot evaluate whether a `FAILED` workflow qualifies for `PARTIAL` synthesis per Section 4.2. |
| `Task.status` | `src/biorch/core/task.py` (`Task.status: TaskStatus`) | Evaluated in `validate_workflow()` (line 123). Updated state is mirrored in `step_results[tid]["status"]`. | **RETAINED** as string value in `step_results[tid]["status"]`. | **AVAILABLE** via `step_results` dictionary lookup. |
| `Task.objective`, `inputs`, `dependencies`, `metadata` | `src/biorch/core/task.py` (`Task`) | Evaluated during pre-execution validation and dependency satisfaction checks (`dependencies_met`). | **DISCARDED.** Not copied into `WorkflowResult`. | **LOST** at handoff boundary. |
| `Result.findings` | `src/biorch/core/result.py` (`Result.findings: List[Dict]`) | Assigned to `results[tid] = result.findings` (line 332) and `step_results[tid]["findings"] = result.findings` (line 335). | **RETAINED** in `WorkflowResult.results` and `WorkflowResult.step_results`. | **AVAILABLE** for aggregation. |
| `Result.artifacts` | `src/biorch/core/result.py` (`Result.artifacts: List[str]`) | **IGNORED.** Lines 332–337 completely omit `result.artifacts`. | **DISCARDED.** `WorkflowResult` contains no artifact references. | **LOST.** 08.4G cannot populate `artifacts` in `task_attributions`. |
| `Result.errors` | `src/biorch/core/result.py` (`Result.errors: List[str]`) | Stored in `step_results[tid]["errors"]` (line 353) and aggregated into `WorkflowResult.errors`. | **RETAINED** in `step_results` and `WorkflowResult.errors`. | **AVAILABLE** for error consolidation. |
| `Result.metadata` | `src/biorch/core/result.py` (`Result.metadata: Optional[Dict]`) | **IGNORED.** Not referenced during result aggregation. | **DISCARDED.** Not retained in `WorkflowResult`. | **LOST** at handoff boundary. |
| `synthesis_eligible` | Not present in runtime | Neither computed nor assigned anywhere in `orchestrator.py`. | **MISSING.** `WorkflowResult` has no `synthesis_eligible` attribute. | **ABSENT.** 08.4G cannot verify gate eligibility flag per Section 4.1. |

### 2.3 `WorkflowResult` Construction Points
In `src/biorch/orchestration/orchestrator.py`, `WorkflowResult` is constructed at exactly three locations:
1. **Validation Failure (lines 177–198):** Returns `WorkflowResult` with `status=WorkflowResultStatus.REJECTED`, empty `completed_tasks`, all tasks in `not_executed_tasks`, and validation errors.
2. **Execution Completion (lines 379–399):** Returns `WorkflowResult` with `status=WorkflowResultStatus.SUCCESS`, `completed_tasks`, `results`, `step_results` reconciled via `_reconcile_terminal_outcomes()`, and execution provenance.
3. **Terminal Failure in `_create_terminal_failure()` (lines 453–474):** Returns `WorkflowResult` with `status=terminal_status` (`FAILED` or `REJECTED`), `completed_tasks`, `failed_task`, `not_executed_tasks`, populated `step_results`, and failure provenance.

---

## 3. Information Required by Phase 08.4G (Result Synthesis)

Based on authoritative contracts (`contracts/synthesis/SYNTHESIS_CONTRACT.md` and `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`) and canonical schemas (`schemas/synthesis_result.schema.json`):

1. **Workflow Identifiers:** `workflow_id` (string) and `workflow_version` (string) (Section 3, Section 12).
2. **Reconciled Terminal Status:** `status` (`SUCCESS`, `FAILED`, `REJECTED`, `NOT_EXECUTED`) (Section 3).
3. **Synthesis Eligibility Flag:** `synthesis_eligible` (boolean), determined by 08.4F Join Gate to enforce fail-closed gatekeeping (Section 4.1, Section 12, `synthesis_result.schema.json`).
4. **Declared Task Ordering:** The sequence of tasks as originally defined in `Workflow.tasks` (Section 5).
5. **Per-Task Attribution & Outcomes (`task_attributions`):**
   - `task_id` (string) (Section 7.1, Section 12)
   - `agent_id` (string) (Section 7.2, Section 12)
   - `status` (`SUCCESS`, `FAILED`, `TIMEOUT`, `NOT_EXECUTED`) (Section 6, Section 12)
   - `findings` (array of objects) (Section 6, Section 12)
   - `artifacts` (array of strings) (Section 8.2, Section 12)
   - `errors` (array of strings) (Section 6, Section 12)
6. **Task Essentiality Classification (`is_essential`):** Required by Section 4.2 to verify whether all failed tasks in a `FAILED` workflow are non-essential, permitting a `PARTIAL` synthesis status instead of unconditional failure.
7. **Consolidated Errors:** `errors` (array of strings) (Section 8.3, Section 12).
8. **Execution & Reconciliation Provenance:** `provenance` (object) (Section 8.4, Section 13).

---

## 4. Option A — Change Surface (Enriched `WorkflowResult`)

### 4.1 Description of Option A
Under Option A, `WorkflowResult` is enriched to carry all metadata and flags required by `SYNTHESIS_CONTRACT.md`. The 08.4F Join Gate operates directly on or within `WorkflowResult`, outputting an updated `WorkflowResult` that serves as the self-contained handoff object to Phase 08.4G.

### 4.2 Change Surface Table for Option A

| File Path | Role in Repository | Classification | Detailed Technical Reason |
| :--- | :--- | :--- | :--- |
| `src/biorch/orchestration/result.py` | Runtime Model | **REQUIRED** | Must add `synthesis_eligible: bool` to `WorkflowResult`. Must enrich `step_results` schema or define a structured `StepResult` / `TaskAttribution` model to carry `agent_id: str`, `artifacts: List[str]`, and `is_essential: bool`. |
| `src/biorch/orchestration/orchestrator.py` | Orchestration Engine | **REQUIRED** | Must implement `synthesis_eligible` calculation per `ORCHESTRATOR_CONTRACT.md` Section 25.4 item 7; must retain `result.artifacts` during worker completion (lines 332–337); must propagate `task.agent_id` and `task.is_essential` into `step_results` across all three construction points (validation failure, execution success, terminal failure). |
| `contracts/synthesis/SYNTHESIS_CONTRACT.md` | Authoritative Contract | **REQUIRED** | Section 3 ("Authoritative Input Boundary") field list must be updated to explicitly include `synthesis_eligible`, aligning Section 3 with Section 4.1. |
| `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` | Authoritative Contract | **POSSIBLY REQUIRED** | Section 12 ("Orchestrator Result") should formally list `synthesis_eligible` alongside existing fields (`workflow_id`, `status`, etc.) to match Section 25.4 item 7. |
| `schemas/task.schema.json` | JSON Schema | **POSSIBLY REQUIRED** | Currently lacks `is_parallel_eligible` and `is_essential` which exist on `src/biorch/core/task.py`. Updating schema ensures formal alignment across contracts. |
| `schemas/workflow_result.schema.json` | JSON Schema | **POSSIBLY REQUIRED** | Currently, no JSON schema exists for `WorkflowResult`. Introducing one would formalize the enriched handoff structure. |
| `tests/test_result.py` | Unit Tests | **POSSIBLY REQUIRED** | Must add unit tests for `WorkflowResult` serialization/deserialization with enriched fields. |
| `tests/test_orchestrator.py` | Unit Tests | **POSSIBLY REQUIRED** | Must verify that `DeterministicOrchestrator` populates `synthesis_eligible`, `agent_id`, and `artifacts` in `WorkflowResult`. Existing tests passing default fixtures will remain valid if default field values are provided. |
| `tests/test_08_4D_execution.py` | Unit Tests | **POSSIBLY REQUIRED** | Existing tests check `result.step_results[tid]["status"]`. Will require updates if `step_results` dictionary structure changes. |
| `tests/test_reconciliation.py` | Unit Tests | **POSSIBLY REQUIRED** | May require updates if `_reconcile_terminal_outcomes()` validates enriched step result fields. |
| `src/biorch/core/task.py` | Core Model | **NOT REQUIRED** | `Task` already contains `agent_id`, `is_essential`, `is_parallel_eligible`, `status`. No model changes needed. |
| `src/biorch/core/result.py` | Core Model | **NOT REQUIRED** | `Result` already contains `findings`, `artifacts`, `errors`, `metadata`. No model changes needed. |
| `src/biorch/core/workflow.py` | Core Model | **NOT REQUIRED** | `Workflow` already contains `workflow_id`, `version`, `tasks`. No model changes needed. |
| `schemas/synthesis_result.schema.json` | JSON Schema | **NOT REQUIRED** | Already specifies `synthesis_eligible`, `task_attributions`, `aggregated_findings`. Option A directly targets this schema. |

---

## 5. Option B — Change Surface (Composite / Separate Handoff Payload)

### 5.1 Description of Option B
Under Option B, `WorkflowResult` remains untouched as the execution result of `DeterministicOrchestrator`. A new composite model (e.g. `JoinGatePayload`, `HandoffPayload`, or `SynthesisInput`) is defined at the Phase 08.4F Join Gate boundary. This model packages `WorkflowResult` together with the original `Workflow` definition (or extracted `Task` metadata) and worker artifacts, supplying Phase 08.4G with a composite input object.

### 5.2 Change Surface Table for Option B

| File Path | Role in Repository | Classification | Detailed Technical Reason |
| :--- | :--- | :--- | :--- |
| `src/biorch/orchestration/join_gate.py` (or `handoff.py`) | New Runtime Module | **REQUIRED** | New module defining the composite handoff model (e.g. `HandoffPayload` with `workflow: Workflow`, `workflow_result: WorkflowResult`, `synthesis_eligible: bool`, `task_artifacts: Dict[str, List[str]]`) and Join Gate evaluation logic. |
| `contracts/synthesis/SYNTHESIS_CONTRACT.md` | Authoritative Contract | **REQUIRED** | Section 3 and Section 14.1 must be rewritten. Currently, Section 3 states: *"Phase 08.4G MUST consume exclusively the `WorkflowResult` object produced and handed off by the Phase 08.4F Join Gate."* This must be changed to mandate consumption of the new composite handoff payload. |
| `src/biorch/orchestration/orchestrator.py` | Orchestration Engine | **POSSIBLY REQUIRED** | Even if `WorkflowResult` is unchanged, `orchestrator.py` currently discards `Result.artifacts` in lines 332–337. To pass artifacts to the Join Gate, `orchestrator.py` must either retain them or expose raw `Result` objects to the Join Gate component. |
| `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` | Authoritative Contract | **POSSIBLY REQUIRED** | Section 25.4 ("Join Gate / Reconciliation") must clarify that the Join Gate produces the composite handoff payload rather than terminating with `WorkflowResult`. |
| `schemas/synthesis_input.schema.json` | JSON Schema | **POSSIBLY REQUIRED** | New JSON schema required to validate the composite handoff payload structure across the 08.4F → 08.4G boundary. |
| `src/biorch/orchestration/result.py` | Runtime Model | **NOT REQUIRED** | `WorkflowResult` remains unchanged in its Phase 04 / Phase 08.4D form. |
| `src/biorch/core/task.py` | Core Model | **NOT REQUIRED** | `Task` model remains unchanged. |
| `src/biorch/core/workflow.py` | Core Model | **NOT REQUIRED** | `Workflow` model remains unchanged. |
| `src/biorch/core/result.py` | Core Model | **NOT REQUIRED** | `Result` model remains unchanged. |
| `tests/test_orchestrator.py` | Unit Tests | **NOT REQUIRED** | Existing tests for `DeterministicOrchestrator` assert on `WorkflowResult` and remain 100% untouched. |
| `tests/test_08_4D_execution.py` | Unit Tests | **NOT REQUIRED** | Existing tests remain completely unaffected. |
| `tests/test_reconciliation.py` | Unit Tests | **NOT REQUIRED** | Existing outcome reconciliation tests remain unaffected. |
| `schemas/synthesis_result.schema.json` | JSON Schema | **NOT REQUIRED** | 08.4G output schema remains unchanged. |

---

## 6. Common / Option-Independent Dependencies

The following repository files are materially required for understanding, designing, and validating the 08.4F → 08.4G boundary regardless of which option is approved:

| File Path | Role | Nature of Dependency |
| :--- | :--- | :--- |
| `contracts/synthesis/SYNTHESIS_CONTRACT.md` | Authoritative Contract | Defines 08.4G synthesis requirements, eligibility gatekeeping rules, declared ordering, and attribution invariants. |
| `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` | Authoritative Contract | Defines parallel orchestration, failure classification (Section 9.2), and Join Gate responsibilities (Section 25.4 item 7). |
| `src/biorch/orchestration/orchestrator.py` | Runtime Engine | Central orchestration execution loop where worker results are collected, reconciled, and packaged. |
| `src/biorch/orchestration/result.py` | Runtime Model | Authoritative definition of `WorkflowResult` and `WorkflowResultStatus`. |
| `src/biorch/core/task.py` | Core Model | Source of truth for `agent_id`, `is_essential`, `is_parallel_eligible`, and `status`. |
| `src/biorch/core/result.py` | Core Model | Source of truth for worker execution outputs (`Result`), specifically `findings` and `artifacts`. |
| `src/biorch/core/workflow.py` | Core Model | Source of truth for declared task sequence (`Workflow.tasks`). |
| `schemas/synthesis_result.schema.json` | Canonical Schema | Target output specification for Phase 08.4G. |
| `schemas/result.schema.json` | Canonical Schema | Contractual schema for specialist worker outputs. |
| `schemas/workflow.schema.json` | Canonical Schema | Contractual schema for workflow definitions. |
| `schemas/task.schema.json` | Canonical Schema | Contractual schema for task definitions. |
| `governance/gemini/PHASE_INDEX.md` | Governance Registry | Authoritative lifecycle tracking for Phases 08.4E (CLOSED), 08.4F (PENDING), and 08.4G (PENDING). |

---

## 7. Testing Requirements & Surface Analysis

### 7.1 Existing Tests Potentially Affected
- **`tests/test_orchestrator.py`:**
  - *Option A Impact:* Low to Moderate. If `WorkflowResult` adds new fields with sensible defaults (e.g. `synthesis_eligible: bool = False`), existing tests constructing or receiving `WorkflowResult` continue to pass. If required fields without defaults are added, fixtures will fail.
  - *Option B Impact:* None. `WorkflowResult` is unmodified.
- **`tests/test_08_4D_execution.py`:**
  - *Option A Impact:* Low. Currently asserts `result.step_results[tid]["status"]`. If `step_results` dictionary structure is enriched additively, assertions remain valid.
  - *Option B Impact:* None.
- **`tests/test_reconciliation.py`:**
  - *Option A Impact:* Low. Asserts `_reconcile_terminal_outcomes(workflow, step_results)` behavior.
  - *Option B Impact:* None.

### 7.2 New Tests Required
- **Under Option A:**
  1. `test_workflow_result_enrichment`: Validates serialization/deserialization of `WorkflowResult` with `synthesis_eligible`, `agent_id`, and `artifacts`.
  2. `test_join_gate_eligibility_flag`: Verifies that `synthesis_eligible` evaluates to `True` on full success or non-essential failures, and `False` on essential failure, timeout, or rejection.
  3. `test_artifact_preservation`: Verifies that `Result.artifacts` is preserved through orchestration into `WorkflowResult`.
- **Under Option B:**
  1. `test_handoff_payload_construction`: Validates creation and serialization of the new composite handoff payload.
  2. `test_join_gate_payload_generation`: Verifies that Phase 08.4F Join Gate correctly extracts `Task` metadata and worker artifacts into the composite payload.
  3. `test_synthesis_consumption_of_payload`: Verifies that Phase 08.4G consumes the composite payload without accessing raw orchestrator state.

### 7.3 Contract & Schema Validation Tests
- Verification of `schemas/synthesis_result.schema.json` against synthesized outputs (identical under both options).
- If Option B is chosen, schema validation test for `schemas/synthesis_input.schema.json`.

### 7.4 Integration Tests
- End-to-end integration test executing a parallel workflow (08.4D) → terminal reconciliation (08.4E) → join gate (08.4F) → synthesis (08.4G).

---

## 8. Runtime Boundary Analysis

### 8.1 Option A Connection Boundary
In Option A, the boundary is unified:
```text
DeterministicOrchestrator.execute()
    └── 08.4E Outcome Reconciliation
    └── 08.4F Join Gate Evaluation (sets synthesis_eligible, preserves artifacts/agent_id)
            ↓ returns
WorkflowResult (enriched)
            ↓ handed to
DeterministicResultSynthesizer.synthesize(workflow_result: WorkflowResult) -> SynthesisResult
```
- **Connection Point:** `DeterministicResultSynthesizer` accepts a single `WorkflowResult` instance.
- **Contract Compatibility:** Complies verbatim with `SYNTHESIS_CONTRACT.md` Section 3 ("consumes exclusively the `WorkflowResult` object").

### 8.2 Option B Connection Boundary
In Option B, the boundary is bifurcated:
```text
DeterministicOrchestrator.execute()
    └── 08.4E Outcome Reconciliation
            ↓ returns
(Workflow, WorkflowResult, RawResults)
            ↓ passed to
JoinGate.evaluate(workflow, workflow_result, raw_results)
            ↓ returns
HandoffPayload (composite)
            ↓ handed to
DeterministicResultSynthesizer.synthesize(payload: HandoffPayload) -> SynthesisResult
```
- **Connection Point:** `JoinGate` acts as an explicit intermediary stage, consuming `WorkflowResult` and `Workflow`, and producing `HandoffPayload`. `DeterministicResultSynthesizer` accepts `HandoffPayload`.
- **Contract Compatibility:** Requires amending `SYNTHESIS_CONTRACT.md` Section 3 and Section 14.1 to redefine the input object.

---

## 9. Compatibility and Migration Considerations

### 9.1 Option A (Enriched `WorkflowResult`)
- **Backward Compatibility:** High if new fields (`synthesis_eligible`, `agent_id`, `artifacts`, `is_essential`) have default values or are added additively to `step_results`. Existing sequential workflows (Phase 04) that produce `WorkflowResult` continue to function without breaking existing callers or tests.
- **Contract Alignment:** Maintains the existing contract assertion in `SYNTHESIS_CONTRACT.md` Section 3 that `WorkflowResult` is the sole handoff object. Requires only surgical clarification to Section 3's field list.
- **Coupling Impact:** Slightly increases the complexity of `WorkflowResult` by embedding synthesis-oriented metadata into the general orchestrator result.

### 9.2 Option B (Separate / Composite Handoff Payload)
- **Backward Compatibility:** Absolute for `WorkflowResult` and Phase 04 orchestration, as neither `WorkflowResult` nor its callers are altered.
- **Contract Alignment:** Requires formal amendment of `SYNTHESIS_CONTRACT.md` Section 3, Section 4, and Section 14.1, because the contract currently forbids consuming anything other than `WorkflowResult`.
- **Coupling Impact:** Decouples orchestrator results from synthesis inputs, but introduces a new intermediate lifecycle model and schema that must be maintained across Phases 08.4F, 08.4G, and 08.4H.

---

## 10. Unresolved Architectural Questions

The following questions cannot be resolved through code inspection and require human architectural decision:

1. **Handoff Object Authority:** Should `WorkflowResult` remain the sole, authoritative output of parallel orchestration carrying all post-join metadata (Option A), or should orchestration result tracking be strictly segregated from synthesis input packaging via an explicit intermediary model (Option B)?
2. **Artifact Lifecycle:** Given that `Result.artifacts` is currently discarded in `orchestrator.py`, should artifact aggregation belong inside `WorkflowResult` (e.g. within `step_results[task_id]["artifacts"]`), or should artifacts be routed directly to the Join Gate outside of `WorkflowResult`?
3. **Contract Rectification Order:** Does governance require Phase 08.4F (Join Gate) to be implemented and closed before `SYNTHESIS_CONTRACT.md` is updated, or should the contract amendment occur concurrently with the architectural decision?
4. **Scope of Join Gate Component:** Should Phase 08.4F be implemented as an internal method within `DeterministicOrchestrator` (e.g. `_evaluate_join_gate()`), or as an independent class (`DeterministicJoinGate`) in `src/biorch/orchestration/`?

---

## 11. Human Approval Point

Architectural selection remains pending human approval.
This investigation does not select Option A or Option B.
