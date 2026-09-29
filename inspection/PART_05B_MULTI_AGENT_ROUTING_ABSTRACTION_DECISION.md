# PART 05B: Multi-Agent Routing Abstraction Decision

## A. Investigation Scope
Read-only analysis to determine the minimal architectural abstraction for Phase 05 multi-agent routing, resolving disagreements from Phase 05A.

## B. Existing Architecture
- **Orchestrator**: Phase 04 deterministic orchestrator (sequential, hardcoded agent executor).
- **Agent**: `DeterministicAgentExecutor` (Phase 03).
- **Security**: `ToolGateway` (Phase 02).

## C. Design A — Registry
- **Mechanism**: Dynamic mapping via a central `AgentRegistry`.
- **Pros**: Dynamic discovery.
- **Cons**: High complexity, service-locator anti-pattern risks.

## D. Design B — Static Configuration
- **Mechanism**: Pre-defined `AgentRegistry` mapping (e.g., config file) loaded at start-up.
- **Pros**: Simple, highly deterministic, no dynamic registry mutation.
- **Cons**: Less flexible than dynamic lookup.

## E. Design C — Capability Discovery
- **Mechanism**: Task defines required capabilities; Orchestrator selects agent via capability matching.
- **Pros**: Highly flexible, future-proofs LLM/Parallel phases.
- **Cons**: Significantly more complex to implement deterministically.

## F. Security Analysis
- **Registry**: Registry itself becomes a security target.
- **Static Config**: Read-only file, easily auditable.
- **Capability Discovery**: Requires capability-to-agent mapping validation.

## G. Determinism Analysis
- **Registry**: High risk if mutable.
- **Static Config**: Inherently deterministic.
- **Capability Discovery**: Determinism depends on matching rules.

## H. Contract Impact
- **Agent Contract**: Likely needs capability field extension.
- **Task Contract**: May need to reflect capability requirements.

## I. Future Compatibility
- **Static Config**: Sufficient for current Phase 05 requirements.
- **Capability Discovery**: Best for Phases 08 (Parallel) and 10 (LLM Planning).

## J. Decision Matrix
| Requirement | Registry | Static Config | Capability Discovery |
| :--- | :--- | :--- | :--- |
| Deterministic Routing | Medium | High | Medium |
| Implementation Complexity | High | Low | High |
| Phase 04 Compatibility | Good | Excellent | Medium |

## K. Minimum Required Abstraction
A **Static Agent Definition Map** (Design B) linked to an **Agent Contract extension** (Capability field) to allow for future capability discovery (Design C) without implementing complex matching logic yet.

## L. Required Now vs Future
- **Required Now**: Static mapping of `AgentID` to `Executor`, Capability field in `Agent` contract.
- **Future**: Dynamic Capability Discovery logic.

## M. Surgical Implementation Sequence
- 05B.1: Extend `Agent` schema to include `capabilities`.
- 05B.2: Implement `AgentRegistry` as a static, read-only wrapper around a configuration dictionary.
- 05B.3: Refactor Orchestrator to use `AgentRegistry` for lookup.

## N. Open Questions
- Should capabilities be validated against tool allowlists? (No, gateway handles this).

## O. Final Decision
Adopt **Static Configuration (Design B)** with **Capability Schema Extension**. This fulfills Phase 05 requirements with minimal risk to existing Phase 04 determinism.

## P. Read-Only Boundary Confirmation
Confirmed: No source code, tests, contracts, or governance modified.
