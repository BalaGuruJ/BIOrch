# Phase 08.4B: Worker Invocation Boundary Investigation Response

## Objective
Establish the deterministic worker invocation boundary required for Phase 08 parallel orchestration.

## A. Investigation Scope
- **Files Inspected**:
    - `src/biorch/orchestration/orchestrator.py`
    - `src/biorch/agents/deterministic_agent.py`
    - `src/biorch/core/task.py`
    - `src/biorch/core/result.py`
    - `src/biorch/orchestration/result.py`
    - `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`
- **Components Inspected**: `DeterministicOrchestrator`, `AgentResolver`, `DeterministicAgentExecutor`, `ToolGateway`.
- **Contracts Inspected**: BIORCH-ORCH-001 (Deterministic Orchestrator Contract).

## B. Current Execution Boundary
The existing execution path is:
`Workflow` → `DeterministicOrchestrator` → `AgentResolver` → `DeterministicAgentExecutor` → `ToolGateway` → `Authorized Tool`.

- **Workflow**: Defines the task sequence and dependencies.
- **DeterministicOrchestrator**: Coordinates execution and validates the workflow.
- **AgentResolver**: Resolves `Task.agent_id` to a `DeterministicAgentExecutor`.
- **DeterministicAgentExecutor**: Invokes the `ToolGateway`.
- **ToolGateway**: Executes the authorized tool.
- **Authorized Tool**: Performs the specific BIOrch task.

## C. Worker Definition for Phase 08
A "worker" in the current architecture is defined by a `DeterministicAgentExecutor` instance, which is responsible for executing a `Task` delegated by the orchestrator. No new `Worker` abstraction is required.

## D. Task-to-Worker Association
Tasks are associated with workers via the `Task.agent_id` field. The `DeterministicOrchestrator` uses the `AgentResolver` to map this `agent_id` to a specific `DeterministicAgentExecutor` instance. `Task.dependencies` ensures the order of invocation.

## E. Worker Invocation Input Contract
The input contract for worker invocation is defined by the `Task` object, specifically the `inputs` field (`Dict[str, Any]`), which contains `operation`, `tool_id`, `version`, and `tool_inputs`.

## F. Worker Invocation Output Contract
The output contract for worker invocation is the `Result` object (defined in `src/biorch/core/result.py`), containing `status` (`SUCCESS`/`FAILURE`/`PARTIAL`), `findings` (list of dictionaries), `artifacts`, `errors`, and `metadata`.

## G. Worker Lifecycle
Phase 08.4B uses the existing `TaskStatus` model for the worker lifecycle:
- **PENDING**: Task initialized but not yet started.
- **IN_PROGRESS**: `DeterministicAgentExecutor.execute()` has been called.
- **COMPLETED**: `ResultStatus.SUCCESS` returned.
- **FAILED**: `ResultStatus.FAILURE` returned.
- **CANCELLED**: Task execution aborted by orchestrator.
- **TIMEOUT**: (Reserved for Phase 08.4C/Future).
- **NOT_EXECUTED**: Task dependency failed or workflow terminated early.

## H. Failure Boundary
Failure propagation:
1. **Agent Rejection**: `DeterministicAgentExecutor` returns `Result(status=ResultStatus.FAILURE, errors=...)`.
2. **Tool Gateway Rejection**: `ToolGateway` returns error status, caught by `DeterministicAgentExecutor` and returned as `Result(status=ResultStatus.FAILURE, ...)`.
3. **Execution Failure**: Caught by `DeterministicAgentExecutor` and returned as `Result(status=ResultStatus.FAILURE, ...)`.
The `DeterministicOrchestrator` handles these failures by terminating the workflow (fail-fast) or recording the failure as specified by the workflow policy.

## I. Provenance
Provenance is retained using the `WorkflowResult.provenance` field, which aggregates metadata from individual task executions (as returned in `Result.metadata` and `ToolResult.provenance`).

## J. Minimal Additive Change Assessment
Phase 08.4B requires no production source-code modification. It establishes and documents the existing worker invocation boundary for consumption by Phase 08.4C.

## K. Phase 08.4C Handoff
Phase 08.4C (Parallel Dispatch) will consume the established boundary by invoking `DeterministicAgentExecutor.execute` in parallel, managing the join/reconciliation gate, and handling worker-level failures/timeouts.

## L. Contract Compliance (BIORCH-ORCH-001)
- **5 (Execution Strategy)**: Sequential order enforced.
- **6 (Agent Boundary)**: Orchestrator delegates to `DeterministicAgentExecutor`.
- **9 (Step Failure)**: Fail-fast behavior is preserved.
- **12 (Orchestrator Result)**: `WorkflowResult` structure is compliant.
- **14 (Failure/Security)**: Orchestrator fails closed on all error types.
- **15 (State)**: Execution state is tracked in `WorkflowResult` and `Task`.
- **25.1, 25.2, 25.3**: The boundary supports independent worker invocation with isolated input/output/failure states.

## M. Explicit Non-Changes
Confirmed:
- No parallel dispatch.
- No ThreadPoolExecutor.
- No concurrent execution.
- No runtime timeout enforcement.
- No new Worker class.
- No new orchestrator contract.
- No Tool Gateway changes.
- No Deterministic Agent changes.
- No Phase 07 changes.

## N. Proposed Files
None.
