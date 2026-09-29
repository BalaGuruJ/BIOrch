# TASK: Phase 05 — Multiple-Agent Routing

**Task ID:** TASK-05
**Phase:** Phase 05 — Multiple Agents
**Status:** DRAFT
**Contract:** contracts/orchestrator/AGENT_RESOLVER_CONTRACT.md

---

## 1. Objective
Implement a deterministic, read-only `AgentResolver` to support routing to multiple `DeterministicAgentExecutor` instances, refactoring the `Orchestrator` to utilize this resolver while maintaining strict Phase 04 backward compatibility.

## 2. Scope
### Implementation (Read-Only/Static)
1.  Define `AgentNotFoundError` exception.
2.  Implement `AgentResolver` class in `src/biorch/orchestration/agent_resolver.py`.
    -   Method: `resolve(agent_id: str) -> DeterministicAgentExecutor`
    -   Static, immutable agent mapping (initialized at startup).
3.  Refactor `src/biorch/orchestration/orchestrator.py` to:
    -   Accept `AgentResolver` via dependency injection.
    -   Use `AgentResolver` for `DeterministicAgentExecutor` lookup during task delegation.
    -   Maintain Phase 04 behavior (support single-agent lookup if resolver is initialized with one executor).
    -   Handle `AgentNotFoundError` as terminal workflow failure.

### Testing
-   Unit tests in `tests/test_resolver.py`:
    -   Successful lookup of valid `agent_id`.
    -   `AgentNotFoundError` for invalid `agent_id`.
    -   Deterministic consistency of mapping.
-   Refine/extend integration tests in `tests/test_orchestrator.py`:
    -   Verify orchestrator functionality with `AgentResolver` injection.
    -   Verify workflow failure semantics upon resolver failure.

## 3. Explicit Non-Goals
-   `AgentRegistry` (Dynamic/Mutable)
-   Capability-based discovery / matching / scoring
-   LLM-based routing
-   Dynamic planning
-   Parallel orchestration
-   Changes to existing contracts (`Agent`, `Task`, `Workflow`, `Result`, `ToolGateway`)
-   Authorization boundary changes (remain in `ToolGateway`)
-   Domain-specific Tableau/Power BI agent changes

## 4. Implementation Plan (Files Affected)
*   **New File:** `src/biorch/orchestration/agent_resolver.py`
*   **Modified File:** `src/biorch/orchestration/orchestrator.py`
*   **New File:** `tests/test_resolver.py`
*   **Modified File:** `tests/test_orchestrator.py`

## 5. Acceptance Criteria
1.  `AgentResolver` successfully maps known `agent_id` to executor.
2.  `AgentResolver` raises `AgentNotFoundError` for unknown `agent_id`.
3.  `Orchestrator` uses `AgentResolver` for delegation.
4.  Phase 04 workflows work identically with the new `AgentResolver` configuration.
5.  Tests demonstrate all lookup scenarios (Success/Failure) and orchestrator integration.

---

## 6. Unresolved Questions
None. The design is strictly bounded by the approved `AGENT_RESOLVER_CONTRACT.md`.
