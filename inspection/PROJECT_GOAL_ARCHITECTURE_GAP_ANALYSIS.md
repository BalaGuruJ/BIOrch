# BIOrch Project Goal & Architecture Gap Analysis

## Executive Summary
This report documents the architectural gap analysis of the current BIOrch repository against its intended long-term goals.

## A. Current Capability Summary
BIOrch has implemented the foundational components (Phases 00-04).
- **Orchestration:** Deterministic, sequential orchestrator capable of executing predefined workflows.
- **Agents:** Deterministic Agent executor, using `ToolGateway` for secure tool access.
- **Contracts/Schemas:** Formalized contracts (Task, Agent, Result, Workflow, Tool) via Pydantic models.
- **Security:** Tool Gateway acts as the central security boundary enforcing tool allowlisting.
- **Testing:** Unit test coverage exists for agent, orchestrator, gateway, and task components.

## B. Project-Goal Definition
The intended BIOrch architecture is a multi-agent orchestration platform for Business Intelligence, characterized by:
1. Framework-neutral adapter-based integration.
2. Deterministic orchestration of complex, sequential/parallel BI workflows.
3. Strict security boundaries via `ToolGateway`.
4. Extensible agent architecture (Tableau/Power BI agents).
5. Human-in-the-loop for sensitive operations.

## C. Architecture Gaps
1. **Parallel Execution (Phase 08):** Currently only sequential orchestration is implemented.
2. **Review Loops (Phase 09):** No mechanism for maker/checker workflows.
3. **LLM Planning (Phase 10):** No autonomous task decomposition capability.
4. **BI Integration (Phases 06/07):** TabUI and PBIParser adapters are currently placeholders.
5. **Phase Alignment Discrepancy:** `governance/gemini/PHASE_INDEX.md` marks phases 03 and 04 as "CLOSED", whereas `docs/PROJECT_STATE.md` lists Phase 02 as the last completed phase.

## D. Agent Architecture Assessment
The current architecture (Core `Agent` model + `DeterministicAgentExecutor`) robustly supports future extension.
- Adding new agents (e.g., `TableauAgent`) requires implementing new `Agent` definitions, registering allowed tools in the `ToolGateway`, and instantiating a new executor.
- No structural changes are necessary to accommodate specialized agents.

## E. Skills/Commands/Agents Distinction
- **Application/Runtime Agents:** The `src/biorch/agents` classes (e.g., `DeterministicAgentExecutor`) that handle runtime execution of tasks.
- **Development-time Gemini Skills:** The files in `.agents/skills/` (e.g., `biorch-task`) that help manage the development/governance lifecycle in the Gemini CLI.
- **Gemini CLI Commands:** The files in `.gemini/commands/` (e.g., `biorch-task.toml`) that map CLI commands to actionable development tasks.
- **BIOrch Runtime Orchestration:** The `src/biorch/orchestration/orchestrator.py` that coordinates the runtime agents.

*Confusion exists:* The terminology "Agent" is used in both development-time (Gemini CLI) and runtime (BIOrch) contexts.

## F. Security/Boundary Gaps
- The `ToolGateway` relies on tool allowlisting; verification of the actual enforcement mechanism is required against the Phase 02 closure evidence.

## G. Testing Gaps
- **Integration Tests:** Coverage of the full path: `Orchestrator -> Agent -> Gateway -> Tool`.
- **Fault Injection:** Testing orchestrator behavior under simulated failure conditions (Gateway timeouts, Tool exceptions).

## H. Cleanup Findings
- (None detected; current structure is highly disciplined).

## I. Future Development Dependencies
1. Parallel Execution (`Phase 08`) depends on `Phase 04` (Sequential Orchestration) being stable.
2. LLM Planning (`Phase 10`) depends on `Phase 05` (Multi-Agent Architecture).

## J. Recommended Next Phase
**Phase 05 (Multiple Agents):** Reconcile `PROJECT_STATE.md` with `PHASE_INDEX.md` and introduce specialized agent definitions for BI tasks to prepare for upcoming integration phases.

## K. Files Inspected
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `governance/gemini/PHASE_INDEX.md`
- `governance/gemini/phase-03-deterministic-agent/PHASE_CLOSURE.md`
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`
- `src/biorch/core/agent.py`
- `src/biorch/agents/deterministic_agent.py`

## L. Confirmation
No repository files were modified or deleted during this analysis, except for the gap analysis report itself.
