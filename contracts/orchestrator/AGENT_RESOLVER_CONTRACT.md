# BIOrch Static AgentResolver Contract

**Contract ID:** BIORCH-RESOLVER-001

**Contract Name:** Static AgentResolver Contract

**Phase:** Phase 05 — Multiple Agents (Routing Abstraction)

**Status:** DRAFT

**Depends On:**
- BIORCH-AGENT-001 — Deterministic Agent Contract
- BIORCH-ORCH-001 — Deterministic Orchestrator Contract

---

## 1. Purpose

This contract defines the architectural boundary and behavioral requirements
for the `Static AgentResolver` introduced in Phase 05 to support multi-agent
routing.

The `AgentResolver` is responsible for mapping a known `agent_id` to a
pre-initialized `DeterministicAgentExecutor` instance.

The `AgentResolver` MUST support deterministic, read-only routing for the
Orchestrator.

---

## 2. Architectural Principle

The `AgentResolver` is a static coordination component.

It MUST provide a read-only mapping of `agent_id` to its corresponding agent executor.

The mapping MUST be initialized at application startup and MUST NOT be mutated
at runtime.

The orchestrator MUST use the `AgentResolver` to resolve agent executors
prior to task delegation.

---

## 3. Scope and Routing Logic

The `AgentResolver` MUST implement the following lookup logic:

1. Input: `agent_id` (string).
2. Lookup: Resolve `agent_id` against the pre-initialized static map.
3. Success: Return the associated `DeterministicAgentExecutor` instance.
4. Failure: Raise a deterministic `AgentNotFoundError` if the `agent_id` is unknown.

The orchestrator MUST catch `AgentNotFoundError` and treat it as a terminal
workflow failure (REJECTED or FAILED status).

---

## 4. Determinism

Routing MUST be deterministic.

The same `agent_id` MUST resolve to the same executor instance.

The mapping MUST NOT change after initialization.

The resolver MUST NOT implement:
- dynamic agent discovery;
- LLM-based agent selection;
- capability scoring;
- dynamic registration.

---

## 5. Security Boundary

The `AgentResolver` is NOT a security authorization component.

The `ToolGateway` remains the authoritative boundary for tool access control.

The `AgentResolver` only maps to executors that are already configured with
their own authorized `ToolGateway` allowlists (as defined in `BIORCH-AGENT-001`).

---

## 6. Executor Ownership

The `AgentResolver` does NOT own the `AgentExecutor` lifecycle beyond lookup.

The `AgentExecutor` configuration (e.g., ToolGateway allowlist) is immutable once
initialized.

The resolver MUST NOT reconfigure or modify an executor after it has been retrieved.

---

## 7. Backward Compatibility

The `AgentResolver` MUST support existing Phase 04 orchestration.

The system MUST function identically to Phase 04 if the resolver is
initialized with exactly one agent executor corresponding to the Phase 04 agent.

---

## 8. Failure and Error Semantics

The `AgentResolver` MUST fail closed.

When a lookup fails, it MUST raise a distinct, deterministic exception.

The orchestrator MUST ensure that this failure results in a valid `WorkflowResult`
status, distinguishing between validation-time (REJECTED) and execution-time
(FAILED) lookups.

---

## 9. Implementation Obligations

Implementation MUST provide:

1. `AgentResolver` class with `resolve(agent_id: str) -> DeterministicAgentExecutor` method.
2. Initialization logic that populates the resolver with static agent definitions.
3. Orchestrator integration that injects the resolver and performs the lookup.

---

## 10. Required Tests

Tests MUST demonstrate:

1. Successful lookup of a valid `agent_id`.
2. `AgentNotFoundError` for an invalid `agent_id`.
3. Orchestrator correctly handles lookup failures during workflow validation.
4. Orchestrator correctly handles lookup failures during execution.
5. Deterministic consistency of the resolver mapping.

---

## 11. Explicit Non-Goals (Future Phases)

The following MUST NOT be implemented or supported:

- AgentRegistry (Dynamic/Mutable);
- Capability-based discovery;
- Capability matching/scoring;
- LLM-based routing;
- Dynamic runtime registration;
- Parallel orchestration;
- Orchestrator-level authorization.

These features belong to later phases.

---

## 12. Relationship to Other Contracts

This contract extends the orchestration capability by abstracting the
executor lookup without modifying existing contracts.

The following remain the source of truth for their respective boundaries:
- `BIORCH-TG-001` (ToolGateway)
- `BIORCH-AGENT-001` (Agent)
- `BIORCH-ORCH-001` (Orchestrator)

This resolver is an implementation of the existing orchestrator's
delegation requirement.
