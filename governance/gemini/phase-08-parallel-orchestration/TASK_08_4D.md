# TASK_08_4D.md

## Objective
Implement the minimum runtime mechanism for worker-level task execution boundary, including mandatory worker timeout enforcement (Section 25.3), worker/task failure classification (Section 9), and per-task status recording (Section 13) following the parallel-dispatch mechanism (08.4C).

## Authoritative Contract Sections
- Section 9 (Step Failure Behavior)
- Section 13 (Workflow Result Status)
- Section 25.1 (Parallel Dispatch)
- Section 25.2 (Worker Isolation)
- Section 25.3 (Timeout Boundary)

## Dependencies
- 08.4A (Schema Foundation)
- 08.4B (Worker Invocation Boundary)
- 08.4C (Parallel Dispatch)

## Exact 08.4D Scope
- Own the implementation of the minimum mandatory timeout enforcement mechanism for parallel worker invocations within the Orchestrator dispatch loop.
- Implement failure classification (Essential vs Non-Essential tasks) per Section 9.
- Implement per-task status recording mechanism using `TaskStatus.TIMEOUT` and existing `WorkflowResult.step_results` mapping to capture terminal states (`TIMEOUT`, `FAILED`, `SUCCESS`).
- Implement best-effort worker cancellation logic upon timeout detection using `ThreadPoolExecutor.Future.cancel()`.
- Update the execution loop in `DeterministicOrchestrator` to handle timeout results and failure classification without redesigning parallel dispatch or modifying core schemas.

## Explicit Non-Goals
- DO NOT implement join/reconciliation logic (reserved for 08.4E).
- DO NOT implement final workflow synthesis (reserved for 08.4F).
- DO NOT invent new Worker abstractions (`worker_runtime.py`).
- DO NOT implement retries.
- DO NOT modify `src/biorch/core/result.py` or `src/biorch/core/task.py`.

## Architectural Acceptance Criteria
- Timeout boundary implemented within `DeterministicOrchestrator` dispatch loop.
- Timeout results explicitly recorded using `TaskStatus.TIMEOUT` within the orchestration result mapping.
- Essential task failure immediately terminates workflow.
- Non-essential task failure/timeout does not terminate the workflow:
    - Independent tasks may continue.
    - Direct and transitive dependents of the failed/timed-out task MUST NOT execute.
    - Dependent tasks MUST be recorded as `NOT_EXECUTED`.
- 08.4D responsibility limited to execution-state classification.
- 08.4D does not perform final join/reconciliation/synthesis (reserved for 08.4E).
- No new Worker abstraction introduced; existing executor/futures capability used.
- Cancellation of already-running workers is best-effort.

## Actual Implementation Boundary
- `src/biorch/orchestration/orchestrator.py`: Modify execution loop and task dispatch to handle timeouts, task cancellation, and failure classification based on task metadata.

## Required Tests
- Verify `TaskStatus.TIMEOUT` recording within the orchestration state.
- Verify timeout triggers task cancellation (best-effort).
- Verify essential failure terminates workflow immediately.
- Verify non-essential failure allows workflow continuation.

## Sequential Compatibility Requirements
- Preserve sequential workflow execution logic established in Phase 04.

## Parallel-Dispatch Compatibility Requirements
- Must use existing `ThreadPoolExecutor` and `future` implementation from 08.4C.

## 08.4E Handoff Requirements
- Per-task terminal outcomes (SUCCESS/FAILED/TIMEOUT) must be clearly exposed to the 08.4E Join Gate for reconciliation via orchestration-level state tracking.

## Next Governance Action
- Review and approval of implementation plan for 08.4D.
