# Phase 08.4C: Parallel Dispatch

## Objective
Implement minimum runtime mechanism to dispatch explicitly independent, parallel-eligible tasks concurrently through the existing `DeterministicAgentExecutor` boundary.

## Status
- Status: NEXT
- Authoritative Source: contracts/orchestrator/ORCHESTRATOR_CONTRACT.md (BIORCH-ORCH-001)

## Dependencies
- Phase 08.4A (Schema Foundation): `TaskStatus.TIMEOUT`, `TaskStatus.NOT_EXECUTED`, `Task.is_parallel_eligible`, `Task.is_essential`. (Note: src/biorch/core/task.py is consumed unchanged).
- Phase 08.4B (Worker Invocation Boundary): `DeterministicAgentExecutor.execute(...)` boundary.

## Scope
- Explicit identification of parallel-eligible tasks.
- Dependency-aware dispatch (tasks only dispatched if dependencies satisfied).
- Concurrent execution of explicitly independent, parallel-eligible tasks.
- Preservation of existing `DeterministicAgentExecutor` boundary.
- Establish minimum runtime association: `task_id` → worker execution/result.

## Explicit Non-Goals (Scope Exclusions)
- Timeout enforcement (08.4D).
- Advanced failure handling (08.4D).
- Join/reconciliation logic (08.4E).
- Final result validation (08.4E).
- Worker completeness determination (08.4E).
- Synthesis eligibility determination (08.4F).
- Deterministic synthesis (08.4F).
- Completion-order-independent synthesis (08.4F).

## Architectural Acceptance Criteria
- Tasks marked `is_parallel_eligible` execute concurrently when dependencies are met.
- Workflow dependency graph is strictly honored.
- Existing sequential workflow path remains unaffected.
- Orchestrator delegates through `DeterministicAgentExecutor`.
- Orchestrator fails closed on dispatch errors.

## Implementation Requirements
For every proposed file modification:
- exact path;
- existing responsibility;
- proposed change;
- reason;
- contract requirement satisfied;
- compatibility impact;
- tests required.

## Next Governance Action
- Investigation (using `biorch-investigation`)
