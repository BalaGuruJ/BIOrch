# PART 05C: Agent Contract & Routing Design Gate

## A. Scope
Read-only investigation to determine if the Agent contract requires modification for Phase 05 multi-agent support, and to select the minimal routing design.

## B. Evidence
- Current Orchestrator implementation `src/biorch/orchestration/orchestrator.py` validates `task.agent_id` against a single `available_agent_id`.
- The current Agent contract (`src/biorch/core/agent.py`) already contains `agent_id`, `role`, `capabilities`, `allowed_tools`, and `supported_operations`.
- The existing infrastructure (Orchestrator and Agent models) is structurally prepared for multiple agents.

## C. Phase 05 Requirements
- Route tasks to multiple, distinct agents based on `task.agent_id`.
- Maintain determinism and security boundaries.
- No dynamic planning or LLM-based agent selection in Phase 05.

## D. Agent Contract Analysis
**Result: DO NOT CHANGE.**
The existing Agent contract `src/biorch/core/agent.py` already includes all required fields:
- `agent_id`: Identification for routing.
- `allowed_tools`: Security boundary for ToolGateway enforcement.
- `supported_operations`: Agent capability boundary.
No modification is required to route tasks to multiple agents.

## E. Capability Analysis
**Result: NOT REQUIRED NOW.**
- The `capabilities` field already exists in the `Agent` Pydantic model.
- No Phase 05 component is designed to consume this field for routing logic, as routing remains deterministic based on `agent_id`.
- Implementing capability-based discovery logic is a future requirement (Phase 10/LLM Planning).

## F. Registry vs Resolver
- **Registry**: Implies a central, possibly mutable service.
- **Resolver**: Implies a read-only, deterministic lookup mechanism.
**Recommendation**: **Design B (Static Agent Resolver)**.
The orchestrator needs a read-only `AgentResolver` to map `agent_id` to a `DeterministicAgentExecutor` instance. This preserves the static, deterministic Phase 04 design.

## G. Phase 04 Compatibility
The `AgentResolver` approach is fully backward compatible with the Phase 04 orchestrator's structure.

## H. Future Compatibility
This design prepares for:
- Phase 06/07 (Tableau/PBI Agents) by simply adding new agent instances to the Resolver.
- Phase 10 (LLM Planning) by allowing future replacement of the static Resolver with a capability-based dynamic resolver.

## I. Contract Change Gate
- Agent contract: **DO NOT CHANGE**. Existing fields sufficient.
- Task contract: **DO NOT CHANGE**. Existing `agent_id` sufficient.
- Workflow contract: **DO NOT CHANGE**. Existing structure sufficient.
- Result contract: **DO NOT CHANGE**.
- Orchestrator contract: **DO NOT CHANGE**.

## J. Minimum Implementation Surface
- New: `src/biorch/orchestration/agent_resolver.py`.
- Modified: `src/biorch/orchestration/orchestrator.py` (Inject Resolver instead of Executor).

## K. Final Decision
**Final Verdict: Design B (Static Agent Resolver).**
Phase 05 does not require contract changes. The orchestrator must be updated to use an `AgentResolver` instead of a hardcoded `AgentExecutor`.

## L. Open Questions
- None.

## M. Read-Only Boundary Confirmation
Confirmed: No implementation files changed.
