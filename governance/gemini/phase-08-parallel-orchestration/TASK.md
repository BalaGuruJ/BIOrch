# Phase 08 — Parallel Orchestration

## Objective
Deterministic parallel orchestration using the existing BIOrch orchestrator boundary and Gemini CLI as the subprocess execution substrate.

## Authoritative Contract
BIORCH-ORCH-001 is the single authoritative orchestrator contract. It governs both:
- deterministic sequential execution;
- deterministic parallel execution.
Do NOT create a new parallel orchestrator contract.

## Runtime Boundary
Verified Gemini CLI capabilities to be used as execution substrate:
- headless execution;
- text output;
- JSON output;
- Python subprocess invocation;
- concurrent subprocess execution;
- timeout enforcement.
Gemini CLI is an execution substrate, NOT the authoritative orchestrator.

## Required Implementation Capabilities
The Phase 08 implementation covers only:
- deterministic workflow definition;
- explicit parallel dispatch;
- independent specialist worker execution;
- worker process isolation;
- mandatory worker timeout;
- worker lifecycle/status tracking;
- worker failure handling;
- deterministic result collection;
- deterministic validation;
- deterministic join/reconciliation;
- deterministic synthesis ordering;
- structured orchestrator result;
- provenance preservation;
- fail-closed behavior.

## Explicit Non-Goals
The following are out of scope:
- LLM planning;
- autonomous task decomposition;
- adaptive routing;
- dynamic workflow generation;
- agent-to-agent autonomous collaboration;
- review/evaluator loops;
- CrewAI;
- LangChain;
- LangGraph;
- AutoGen;
- MCP implementation;
- Gemini MCP integration;
- BI parser changes;
- Phase 07 Power BI contract changes;
- Tableau/Power BI metadata extraction implementation.

## Phase 07 Protection
Phase 08 consumes Phase 07 outputs/contracts and does not modify or reimplement Phase 07 PBIParser/canonicalization logic.

## Implementation Sequencing (Ordered Gates)
Phase 08.4A — Implementation Contract/Schema Definition
Phase 08.4B — Worker Invocation Boundary
Phase 08.4C — Parallel Dispatch
Phase 08.4D — Timeout and Failure Handling
Phase 08.4E — Join/Reconciliation
Phase 08.4F — Deterministic Synthesis
Phase 08.4G — Integration Tests
Phase 08.4H — Final Governance/Contract Validation

## Acceptance Criteria
Derived from BIORCH-ORCH-001:
- sequential behavior remains intact;
- independent workers can execute concurrently;
- dependent tasks are not dispatched concurrently;
- every worker has a bounded timeout;
- worker failures are represented deterministically;
- timeout is represented deterministically;
- join/reconciliation occurs before synthesis;
- synthesis ordering does not depend on completion order;
- failed required work prevents SUCCESS;
- provenance is retained;
- Tool Gateway/Agent boundaries remain intact;
- no LLM planning is introduced;
- Phase 07 remains untouched;
- tests demonstrate all required behavior.
