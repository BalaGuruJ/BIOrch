# PART 05D: AgentResolver Contract Investigation

## A. Scope
Read-only investigation of contract requirements for implementing the Static AgentResolver design in Phase 05 multi-agent orchestration.

## B. Existing Contract Evidence
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` (Phase 04 boundary)
- `contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md` (Agent abstraction)

## C. Current Routing Assumptions
- Orchestrator is hardcoded to a single `DeterministicAgentExecutor`.
- `Task` contracts contain `agent_id`, but it is currently validated against a single source.

## D. AgentResolver Responsibility
- **Responsible for**: Deterministic lookup/mapping of `agent_id` to an initialized `DeterministicAgentExecutor` instance.
- **NOT Responsible for**: LLM planning, dynamic capability discovery, orchestration logic, agent execution, security enforcement.

## E. Proposed Resolver Interface
```python
class AgentResolver:
    def resolve(self, agent_id: str) -> DeterministicAgentExecutor:
        # Returns the pre-initialized executor or raises 
        # DeterministicRoutingError if agent_id is unknown.
```

## F. Unknown-Agent Behavior
- `AgentResolver` MUST raise a deterministic exception (e.g., `AgentNotFoundError`) when an unknown `agent_id` is requested. 
- The Orchestrator MUST catch this and trigger a FAILED or REJECTED workflow result.

## G. Determinism Requirements
- Mapping MUST be immutable at runtime.
- Lookup MUST be consistent for the same input.

## H. Security Boundary
- `ToolGateway` remains the authoritative security boundary.
- `AgentResolver` only maps to executors that are already configured with their own `ToolGateway` allowlists.

## I. Contract Change Matrix
| Contract | Change? | Reason |
| :--- | :--- | :--- |
| Agent | NO | Sufficient for identification |
| Task | NO | Sufficient for routing (`agent_id`) |
| Workflow | NO | Sufficient structure |
| Result | NO | Sufficient semantics |
| Tool | NO | Existing boundary |
| ToolGateway | NO | Existing boundary |
| Orchestrator | YES | Constructor and lookup logic update |

## J. Backward Compatibility
The Phase 04 orchestrator can be supported by initializing an `AgentResolver` with a single entry (the existing agent).

## K. Required Tests
- Valid lookup.
- Unknown agent lookup (Error handling).
- Orchestrator integration (injecting the resolver).

## L. Open Questions
- None.

## M. Final Design Gate
- Proceed with `AgentResolver` abstraction.
- Agent contract changes: **DO NOT CHANGE**.
- Orchestrator contract changes: **DO NOT CHANGE** (semantics preserved).

## N. Read-Only Boundary Confirmation
Confirmed: No implementation files changed.
