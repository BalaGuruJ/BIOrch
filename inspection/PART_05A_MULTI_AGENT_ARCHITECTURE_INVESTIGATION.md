# PART 05A: Multiple-Agent Architecture Investigation

## A. Investigation Scope
This investigation is a READ-ONLY analysis of the current BIOrch repository (Phases 00-04) to determine the architectural requirements and path forward for Phase 05 (Multiple Agents), while preserving deterministic and security boundaries established in Phases 03 and 04.

## B. Current Architecture
- **Agents**: Defined via a Pydantic `Agent` model in `src/biorch/core/agent.py`. Currently, `DeterministicAgentExecutor` acts as the single-agent runtime.
- **Orchestration**: A deterministic, sequential orchestrator defined in `src/biorch/orchestration/orchestrator.py` (Phase 04).
- **Security**: `ToolGateway` (Phase 02) defines the strict tool allowlisting boundary.

## C. Current Single-Agent Assumptions
- Runtime assumes exactly one active agent instance during orchestration.
- `DeterministicAgentExecutor` is hardcoded to a specific agent definition.
- Orchestrator lacks a dynamic lookup or registry mechanism to select agents.

## D. Multi-Agent Requirements
- **Agent Registry**: A mechanism to register and look up specialized agents by `agent_id` or `role`.
- **Agent Factory/Resolver**: Logic to instantiate or retrieve an agent executor based on registry lookup.
- **Agent Roles**: Specialized agent definitions (e.g., `TableauAgent`, `PowerBIAgent`).
- **Authorization**: The `ToolGateway` must remain authoritative; agent-to-tool allowlisting must be maintained on a per-agent basis in the registry/executor.

## E. Contract Impact
- **Agent Contract**: Likely unchanged. The `Agent` Pydantic model is sufficient.
- **Registry Contract**: **EXTENSION_REQUIRED**. A new `AgentRegistry` contract is needed for registration/lookup.
- **Orchestrator Contract**: **EXTENSION_REQUIRED**. Orchestrator needs to reference the Registry rather than a hardcoded agent.

## F. Orchestrator Impact
The Orchestrator must be decoupled from specific agent instances. It should query an `AgentRegistry` during workflow validation to resolve agents.

## G. Security Impact
- Routing Boundary: Risk of unauthorized agent lookup.
- Routing Boundary: Registry must ensure `ToolGateway` security is *not* bypassed (the Registry should only return *permitted* tools, which the ToolGateway still enforces).

## H. Determinism Impact
Determinism is preserved if the Registry is immutable at runtime, and lookup logic is deterministic (e.g., `agent_id` mapped to an agent definition).

## I. Testing Impact
- New tests for `AgentRegistry` lookup/rejection.
- New tests for multi-agent routing.

## J. Tableau/Power BI Compatibility
The registry-based approach supports adding new BI agents (Tableau/Power BI) without changing orchestrator logic.

## K. Skills/Commands/Runtime Agent Distinction
- **Runtime Agent**: `src/biorch/agents` (e.g., `DeterministicAgentExecutor`).
- **Gemini Skill**: `.agents/skills/` (for CLI dev workflow).
- **Gemini CLI Command**: `.gemini/commands/` (CLI automation).

## L. Proposed Target Architecture
1. **Registry**: `AgentRegistry` containing agent definitions.
2. **Resolver**: `AgentResolver` lookup logic.
3. **Execution**: `DeterministicAgentExecutor` for a given agent configuration.

## M. Phase 05 Implementation Breakdown
- 05A: Architecture Investigation (this report)
- 05B: Agent Registry Contract Design
- 05C: Agent Registry Implementation
- 05D: Orchestrator Multi-Agent Routing
- 05E: Security + Determinism Validation
- 05F: Integration + Closure

## N. Gap Analysis Cross-Check
Matches current repository state and architectural gaps.

## O. Risks / Open Questions
- Dynamic registration vs. static? (Prefer static/pre-defined for determinism).
- Registry mutation risks at runtime? (Must be read-only).

## P. Recommendation
Accept the registry-based design to support multi-agent architecture while preserving Phase 04 determinism.

## Q. Read-Only Boundary Confirmation
Confirmed: No source code, tests, contracts, or governance modified.
