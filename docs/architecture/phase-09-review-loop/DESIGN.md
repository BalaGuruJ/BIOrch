# Phase 09 — Deterministic Review Loop: Architecture & Design Specification

**Phase:** Phase 09 — Review Loop (Evaluator / Reviewer Loops)  
**Status:** DESIGN SPECIFICATION (CANONICAL / RECONCILED WITH REPOSITORY)  
**Source of Truth:** BIOrch Repository Architecture (Phases 01–08.4H)

---

## 1. Executive Summary & Objectives

Phase 09 introduces the **Deterministic Review Loop** (Maker/Checker evaluation and bounded retry/correction loops) to the BIOrch orchestration and agent architecture. Building upon the robust parallel execution, reconciliation, synthesis, and provenance verification established in Phase 08 (Phases 08.4A–08.4H), Phase 09 ensures that agent outputs are systematically evaluated against deterministic rules, schemas, and expectations before final synthesis.

Crucially, Phase 09 adheres strictly to the core BIOrch architectural invariants:
- **No LLM-Based Evaluation or Planning:** All evaluation rules, review checks, and retry decisions are strictly deterministic and rule-based.
- **Backward Compatibility:** Phase 07 Power BI parsing and Phase 08 parallel dispatch/reconciliation/provenance contracts remain entirely unaltered and fully backward compatible.
- **Fail-Closed Semantics:** Any unrecovered review rejection, retry exhaustion, or hard execution failure results in deterministic failure status (`SUCCESS = False`, `REJECTED` or `FAILED`).

---

## 2. Reviewer/Evaluator Contract

### 2.1 Exact Responsibility
The Reviewer/Evaluator (the "Checker") inspects the `TaskResult` (produced by the worker "Maker" agent) against a set of registered, deterministic evaluation rules. It determines whether the output satisfies structural, schema, and semantic expectations.

### 2.2 Input Contract
- **`Task`**: The original task definition containing execution instructions, expected artifacts, or schema constraints.
- **`TaskResult`**: The output produced by the worker agent, containing `status` (`SUCCESS`/`FAILURE`/`PARTIAL`), output artifacts, execution logs, and metadata.
- **`ReviewConfig` / Rules**: A deterministic rule set or validator list (e.g., schema validation, required keys presence, data invariant checks).

### 2.3 Output Contract (`ReviewResult`)
- **`approved`** (`bool`): True if all deterministic rules passed; False otherwise.
- **`rule_results`** (`List[RuleResult]`): Detailed pass/fail outcome for each evaluated rule.
- **`correction_feedback`** (`Optional[str]`): Structured feedback string describing why rules failed, formatted for injection into subsequent retry attempts.
- **`reviewer_id`** (`str`): Unique identifier of the evaluator component/rule set.

### 2.4 Deterministic Rule Representation
Rules are expressed as pure Python callables or serializable rule objects that inspect `TaskResult` without side effects or probabilistic reasoning.
```python
@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    message: str

@dataclass
class ReviewResult:
    approved: bool
    rule_results: List[RuleResult]
    correction_feedback: Optional[str]
    reviewer_id: str
```

### 2.5 PASS / REJECT Semantics
- **PASS (`approved=True`)**: All evaluation rules succeed. The task proceeds to synthesis/reconciliation normally.
- **REJECT (`approved=False`)**: One or more rules fail. If retries remain, the task enters a correction loop. If retries are exhausted, the task results in rejection status.

### 2.6 Hard Failure vs. Review Rejection Distinction
- **Hard Failure**: Occurs during task execution (e.g., Tool Gateway denial, security violation, unhandled exception, syntax error in worker execution). Hard failures are **not** subject to review retries and immediately set `status = ResultStatus.FAILURE`.
- **Review Rejection**: Occurs when execution completes successfully (`status = ResultStatus.SUCCESS`), but the output fails post-execution quality/schema evaluation rules. Review rejections **are** eligible for bounded retries with correction feedback.

---

## 3. Integration Point

### 3.1 Exact Orchestrator Location
Review and correction loops are integrated into the task execution lifecycle immediately after worker task execution (or parallel worker execution) and before final join/reconciliation/synthesis, within the orchestrator execution loop (`src/biorch/orchestration/orchestrator.py`).

Specifically, for each task executed by a worker:
1. Worker executes `Task`.
2. Produces initial `Result`.
3. **Review Loop Hook**: If a review policy is attached and task status is `ResultStatus.SUCCESS`, evaluate `Result` via the Reviewer.
4. If **Approved**: Return `Result` with review provenance attached in `metadata`.
5. If **Rejected** (and retries remain): Inject `correction_feedback` into **`task.inputs["correction_feedback"]`** and re-dispatch to the worker.
6. If **Rejected** (at retry limit): Mark step result as rejected/failed per fail-closed semantics.

*(Note: Task-level `ResultStatus` in `src/biorch/core/result.py` strictly defines `SUCCESS`, `FAILURE`, and `PARTIAL`. Review rejections are represented via workflow/step-level tracking and metadata.)*

### 3.2 Preservation of Existing Behavior
- Placing review loops at the individual task execution boundary ensures that sequential workflows (Phase 04) and parallel dispatch workflows (Phase 08.4C/08.4D) operate identically when no review policy is defined.
- Existing reconciliation (`JoinGate`), synthesis (`WorkflowResult`), and provenance validation (`ProvenanceValidator`) consume the final step results and provenance payload without modification to their public interfaces.

---

## 4. Retry Model

### 4.1 Max Retry Semantics
- Configured via `max_retries` (default: `0` for backward compatibility; configurable per workflow/task).

### 4.2 Attempt Numbering
- Attempt 1: Initial execution.
- Attempt 2..N: Retry attempts subsequent to review rejections (`attempt_number` tracked in metadata).

### 4.3 Retry Termination
Retries terminate immediately upon:
1. Reviewer approval (`approved=True`).
2. Retry limit exhaustion (`attempt_number > max_retries`).
3. Hard execution or security failure.

### 4.4 Behavior Matrix
| Outcome | Condition | Result Status / Step Status | Action |
| --- | --- | --- | --- |
| **a. Review Approval** | `approved=True` | `SUCCESS` | Proceed to synthesis |
| **b. Rejection + Retries Remaining** | `approved=False` & `attempt <= max_retries` | `RETRYING` (internal) | Inject feedback into `task.inputs` & re-execute |
| **c. Rejection at Retry Limit** | `approved=False` & `attempt > max_retries` | `REJECTED` / `FAILED` | Halt and fail closed |
| **d. Hard Execution / Security Failure** | Exception / Gateway denial | `FAILURE` | Halt immediately (no retries) |

---

## 5. Correction Feedback

### 5.1 Feedback Propagation
When a review rejection occurs, `correction_feedback` must be injected into **`task.inputs["correction_feedback"]`**, ensuring that the worker agent (`DeterministicAgentExecutor`), which strictly reads `task.inputs` and ignores `task.metadata`, receives the correction instructions on the subsequent retry attempt.

### 5.2 Schema & Contract Compatibility
Existing `Task` and `Result` models support extensible dictionaries (`inputs` and `metadata`), allowing correction feedback and review audit history to be transmitted without breaking public schema contracts (`schemas/task.schema.json`, `schemas/result.schema.json`).

---

## 6. Audit & Provenance

### 6.1 Information Retained per Attempt
For every review attempt, review information is retained for EVERY review attempt without allowing later attempts to overwrite earlier attempts using an explicit attempt history structure:

`Result.metadata["review"]["attempt_history"]`

where each attempt entry contains:
- `attempt_number`
- `reviewer_id`
- `rule_results`
- `correction_feedback`, when rejected

This ensures review information is strictly deterministic and fully auditable across multi-attempt correction loops without introducing unauthorized timestamps.

### 6.2 ProvenanceValidator Integration
`ProvenanceValidator` (`src/biorch/orchestration/provenance_validator.py`) **requires zero modifications**. Review audit trails and attempt histories stored in `Result.metadata` pass through existing provenance completeness and SHA-256 cryptographic checksum validation transparently.

---

## 7. Result Semantics & Workflow Status

### 7.1 Mapping to Workflow Status
- **`SUCCESS`**: Task executed successfully and passed review.
- **`FAILED`**: Task encountered a hard execution error, tool gateway denial, or security violation.
- **`REJECTED`**: Task executed but failed review evaluation and exhausted all retry attempts.
- **`NOT_EXECUTED`**: Task skipped due to upstream failures or join gate rejection.

### 7.2 Fail-Closed Semantics
Any workflow containing a `REJECTED` or `FAILED` task evaluates `WorkflowResult.success = False`.

---

## 8. Parallel Execution & Thread Safety

### 8.1 Independent Review Loops
For parallel-ready tasks (Phase 08), each worker execution thread runs its review and retry loop independently on its assigned task slice.

### 8.2 Thread Safety
- Reviewer evaluation functions are pure, stateless, and thread-safe.
- Attempt counters and review histories are stored locally within task/result object instances or orchestrator-local tracking dictionaries rather than global mutable state.

---

## 9. Contract Impact & Backward Compatibility

### 9.1 Contract Modification Analysis
- `schemas/task.schema.json`: No modification required. Review configuration is carried through the existing extensible Task inputs/metadata structures.
- `schemas/result.schema.json`: No modification required. Review audit information is carried through the existing Result metadata structure.
- Python Code Contracts: Additive extensions (`Reviewer`, `ReviewResult`, `RuleResult`, review execution wrapper) without altering existing public methods.

### 9.2 Backward Compatibility
Workflows and tests without configured review policies execute identically to Phase 08.

---

## 10. Testing Design

The minimum required test suite for Phase 09 includes:
1. **Reviewer Approval Test**: Verify task passes when rules succeed.
2. **Single Rejection & Retry Success Test**: Verify rejection on attempt 1, feedback propagation (`task.inputs`), and success on attempt 2.
3. **Multiple Retries Test**: Verify multi-attempt correction loops.
4. **Retry Exhaustion Test**: Verify task results in rejection status when `max_retries` is exceeded.
5. **Hard Execution Failure Test**: Verify hard errors bypass retries and yield `FAILURE`.
6. **Security Failure Test**: Verify tool gateway / security rejections immediately fail closed.
7. **Correction Feedback Propagation Test**: Verify feedback is correctly passed via `task.inputs` to subsequent worker attempts.
8. **Provenance Preservation Test**: Verify attempt history and rule results are fully captured in result metadata without breaking `ProvenanceValidator`.
9. **Parallel Task Independent Review Test**: Verify parallel workers execute independent review loops correctly.
10. **Phase 08 Regression Test**: Verify existing parallel orchestration and test suites pass without regression.

---

## 11. Exact Implementation File Plan

### 11.1 Files to be Created (during implementation phase)
- `src/biorch/review.py`: Reviewer, evaluation rules, and review loop orchestrator.
- `tests/test_review_loop.py`: Comprehensive test suite covering all 10 testing requirements.

### 11.2 Files to be Modified (during implementation phase)
- `src/biorch/orchestration/orchestrator.py`: Integrate review hook, attempt tracking, and retry handling.

### 11.3 Files Explicitly Protected from Modification
- `src/biorch/orchestration/provenance_validator.py` (Verified: no changes required).
- `src/biorch/pbiparser.py` (Phase 07 parsing logic is strictly protected).
- Existing Phase 08 parallel dispatch/reconciliation modules.
- `contracts/**` and `schemas/**` (Contracts remain immutable).
- Governance status files (`TASK.md`, `RESPONSE.md`, `REVIEW.md`, `PHASE_INDEX.md`).

---

## 12. Environment Note

The test environment prior to Phase 09 previously produced: `17 failed, 102 passed, 2 skipped` because `DOTNET_ROOT` was not configured. This is treated strictly as an environment configuration issue (unrelated to BIOrch code defects). Environment configuration is not modified as part of Phase 09.

---

## 13. Acceptance Checklist for Implementation

- [ ] Reviewer contract defined (`Reviewer`, `ReviewResult`, `RuleResult`).
- [ ] Orchestrator integrated with review loop and retry management.
- [ ] Retry semantics (max retries, attempt numbering, termination) implemented.
- [ ] Correction feedback propagation via `task.inputs` tested.
- [ ] Audit and provenance retention verified (without modifying `ProvenanceValidator`).
- [ ] Result semantics (`SUCCESS`, `FAILURE`, `REJECTED`) correctly mapped with fail-closed behavior.
- [ ] Parallel execution thread-safety verified.
- [ ] 10-point test suite implemented and passing.
- [ ] Phase 08 regression verification successful.
