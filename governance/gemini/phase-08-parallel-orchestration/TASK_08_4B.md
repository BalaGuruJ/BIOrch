# Phase 08.4B: Worker Invocation Boundary

## Objective
Establish the deterministic worker invocation boundary required for Phase 08 parallel orchestration.

## Status
- Status: IN_PROGRESS
- Authoritative Source: contracts/orchestrator/ORCHESTRATOR_CONTRACT.md (BIORCH-ORCH-001)

## Investigation
- Inspect `DeterministicOrchestrator` implementation.
- Analyze agent invocation boundary.
- Review `DeterministicAgent` interface.
- Audit `ToolGateway` boundary.
- Validate workflow/task execution path.
- Review result/provenance structures.
- Evaluate Gemini CLI subprocess/runtime integration.
- Examine tests for agent invocation and orchestration.

## Constraints
- MUST NOT implement parallel dispatch.
- MUST NOT bypass `DeterministicAgent` or `ToolGateway`.
- MUST NOT modify source code during investigation.
- MUST NOT modify BIORCH-ORCH-001 or Phase 07 artifacts.
- MUST NOT create new orchestrator contract.

## Deliverables
- Task-to-worker association definition.
- Worker lifecycle state representation.
- Deterministic worker invocation contracts (in/out).
- Structured worker result representation.
- Identification of necessary minimal additive runtime/result structures.

## Reporting Requirements
For every proposed file modification:
- exact path;
- existing responsibility;
- proposed change;
- reason;
- contract requirement satisfied;
- compatibility impact;
- tests required.
