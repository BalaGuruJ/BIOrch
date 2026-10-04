# Phase 10 — LLM-Based Adaptive Planning: Architecture & Design Specification

**Phase:** Phase 10 — LLM-Based Planning (Adaptive Task Planning)  
**Status:** DESIGN SPECIFICATION (CANONICAL / RECONCILED WITH REPOSITORY)  
**Source of Truth:** BIOrch Repository Architecture (Phases 01–09)

---

## 1. Executive Summary & Objectives

Phase 10 introduces **LLM-Based Adaptive Planning** to BIOrch. Building upon the secure tool gateways (Phase 02), deterministic agents (Phase 03), orchestrators (Phase 04/08), multi-agent resolution (Phase 05), parallel dispatch (Phase 08.4C-H), and maker-checker review loops (Phase 09), Phase 10 enables the system to accept high-level natural language user intents and dynamically synthesize structured, executable `Workflow` graphs.

Crucially, Phase 10 adheres strictly to the core BIOrch architectural invariants:
- **Separation of Planning and Execution:** The LLM Planner is strictly responsible for generating candidate workflow plans from user intents. It never executes code, accesses tools directly, or bypasses security.
- **Strict Plan Validation:** Every LLM-generated plan must pass rigorous structural, schema, and security validation before execution is permitted.
- **Authoritative Tool Gateway & Agent Allowlists:** The Tool Gateway and `AgentResolver` remain fully authoritative. Any generated plan proposing unauthorized tools or invalid agent routing is rejected during validation.
- **Deterministic Execution:** Once validated, the plan is wrapped in a canonical `Workflow` and executed deterministically by the existing `DeterministicOrchestrator` and Phase 09 `Reviewer` inspection loops.
- **Additive Contract Architecture:** Phase 10 introduces an additive contract (`LLM_PLANNER_CONTRACT.md`) without modifying existing core contracts or schemas.

---

## 2. Exact Responsibility and Boundary of the LLM Planner

### 2.1 Core Responsibility
The LLM Planner is responsible for translating unstructured user intents (natural language goals) into structured, canonical `Workflow` representations (ordered lists of `Task` objects with dependencies, agent assignments, and operations).

### 2.2 Architectural Boundaries
- **In Scope:**
  - Parsing natural language user prompts or business objectives.
  - Interacting with an LLM provider abstraction to propose workflow steps.
  - Serializing/deserializing structured JSON/YAML plan representations.
  - Attaching planning provenance and source intent metadata to generated workflows.
- **Out of Scope (Strictly Forbidden):**
  - Direct execution of tasks or tool calls.
  - Bypassing the Tool Gateway or agent allowlists.
  - Making policy, review, or retry determinations during execution.
  - Modifying existing orchestrator, review, or gateway runtimes.

---

## 3. Intent → Plan → Canonical Workflow Flow

The lifecycle of an adaptive request proceeds through distinct, non-overlapping phases:

```
[User Intent (Natural Language)]
             ↓
    [LLM Planner Component]
             ↓
    [Raw Candidate Plan (JSON/Dict)]
             ↓
    [Plan Validator / Deterministic Validator] (Schema & Security Check)
             ↓  (Valid)
    [Canonical Workflow Instance]
             ↓
    [DeterministicOrchestrator] (Sequential / Parallel Execution + Phase 09 Review Loop)
             ↓
    [Synthesis & Provenance]
```

1. **Intent Formulation:** User provides a natural language goal (e.g., *"Inspect the Tableau workbook relationships and extract Power BI semantic lineage"*).
2. **Plan Generation:** The LLM Planner queries an LLM provider with available agent capabilities and tool schemas to generate a structured candidate task graph.
3. **Plan Validation:** The candidate plan is converted into a `Workflow` instance and validated via `DeterministicOrchestrator.validate_workflow()`.
4. **Execution:** The validated canonical workflow is executed by `DeterministicOrchestrator`.

---

## 4. Planning and Plan Validation as Separate Stages

Planning and validation are strictly decoupled:
- **Stage 1 (Planning):** Probabilistic / LLM-based generation of candidate workflow steps and dependencies. Because LLM output can be noisy or misaligned, this stage is entirely unprivileged.
- **Stage 2 (Validation):** Deterministic, rule-based inspection (`DeterministicOrchestrator.validate_workflow()`) ensuring every step conforms to strict schema definitions, valid agent IDs, supported operations, and authorized tool allowlists.
- **Rule:** No generated plan may bypass Stage 2 validation.

---

## 5. Exact Interface Between Planner and Existing Workflow/Task Contracts

The LLM Planner outputs a Python dictionary or JSON structure that maps directly into BIOrch's canonical core models (`Workflow`, `Task`):
- **`Workflow`**: Contains `workflow_id`, `version`, and `tasks` (`List[Task]`).
- **`Task`**: Contains `task_id`, `agent_id`, `inputs` (including `operation` and `tool_id`), `dependencies`, and `metadata` (capturing planning rationale and prompt origin).

---

## 6. How Generated Workflows are Validated Before Execution

Before any generated workflow is handed to `DeterministicOrchestrator.run()` or `run_with_synthesis()`, it must pass:
1. **Schema Validation:** Ensures required fields (`workflow_id`, `version`, `tasks`) and task attributes (`task_id`, `agent_id`, `inputs`) are present and correctly typed.
2. **Dependency Graph Integrity:** Ensures step dependencies refer to preceding steps and contain no circular references.
3. **Agent and Tool Allowance Check:** Validates that every task's `agent_id` exists in the `AgentResolver` and that its requested `tool_id` and `operation` are strictly permitted by that agent's security allowlist.

---

## 7. Authoritative Tool Gateway and Agent Allowlists

The introduction of LLM planning in no way relaxes security constraints:
- The **Tool Gateway** (`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`) remains the sole enforcement point for tool execution permissions.
- The **`AgentResolver`** (`contracts/orchestrator/AGENT_RESOLVER_CONTRACT.md`) remains the static registry of agent executors and their immutable allowlists.
- If an LLM-generated plan suggests an unallowlisted tool or unrecognised agent, validation fails immediately, preventing execution.

---

## 8. DeterministicOrchestrator as the Execution Boundary

- Once validated, the generated `Workflow` is passed to `DeterministicOrchestrator`.
- The orchestrator executes the workflow exactly as it would a statically defined workflow (supporting sequential execution, parallel dispatch via `JoinGate`, and provenance validation).
- The orchestrator remains completely agnostic to whether the workflow originated from a static definition or the LLM Planner.

---

## 9. Phase 09 Reviewer Remains Downstream of Execution

- Task-level execution and review loops (`Reviewer`, Maker-Checker evaluation, bounded retries with correction feedback) operate identically on LLM-generated workflows.
- Review policies and evaluation rules inspect worker outputs post-execution, ensuring quality control regardless of how the task graph was created.

---

## 10. Failure and Rejection Semantics

- **Planning Failure:** If the LLM fails to return valid JSON or encounters a provider error, the planner raises a deterministic exception (`PlanGenerationError`).
- **Validation Rejection:** If a generated plan fails structural, schema, or security validation, validation errors are returned, and execution is halted (`WorkflowResultStatus.REJECTED`).
- **Fail-Closed Principle:** The system never attempts to "auto-fix" insecure or malformed plans through guessing; validation failure results in immediate rejection.

---

## 11. Deterministic Handling of Planner Outputs

To maintain consistency and testability:
- The Planner component supports an optional deterministic mock/fixture mode for testing and evaluation without live LLM calls.
- Prompt templates and structuring instructions sent to the LLM are versioned and standardized.

---

## 12. Provenance and Audit Requirements for Generated Plans

Every LLM-generated workflow and its tasks must retain planning provenance in their workflow state (`workflow.current_state`) and task metadata:
- `workflow.current_state["planner"]`: Captures planner ID, model identifier, generation timestamp, and original user prompt.
- `task.metadata["planner_rationale"]`: Captures the reasoning or description provided by the planner for why the task was generated.
- These metadata fields flow transparently through `ProvenanceValidator` without disrupting SHA-256 cryptographic checksum checks.

---

## 13. LLM-Provider Abstraction and Contract Impact

- **Provider Abstraction:** An internal `LLMProvider` interface (supporting mock providers, API clients, or pluggable connectors) isolates model communication from orchestration logic.
- **Contract Impact:** Phase 10 requires **B) an additive contract**:
  - New Contract: `contracts/orchestrator/LLM_PLANNER_CONTRACT.md`.
  - Existing contracts (`ORCHESTRATOR_CONTRACT.md`, `AGENT_RESOLVER_CONTRACT.md`, `TOOL_GATEWAY_CONTRACT.md`, `SYNTHESIS_CONTRACT.md`, etc.) remain **completely unmodified**.

---

## 14. Backward Compatibility with Phases 01–09

- All existing static workflows, unit tests, parallel orchestrations (Phase 08), and review loops (Phase 09) continue to execute without change.
- The LLM Planner is an optional, additive entry point upstream of the orchestrator; existing direct workflow execution is fully preserved.

---

## 15. Exact Implementation Components / Files (Post-Approval)

After design approval and contract creation:
1. **Contract:** `contracts/orchestrator/LLM_PLANNER_CONTRACT.md`
2. **Source Module:** `src/biorch/orchestration/planner.py` (LLM Planner implementation & provider abstraction)
3. **Tests:** `tests/test_llm_planner.py` (Unit tests covering intent translation, plan validation, security interception, and provenance)

---

## 16. Required Tests and Acceptance Criteria

- **Test 1:** Successful translation of natural language intent into a validated, canonical `Workflow`.
- **Test 2:** Rejection of LLM plans proposing unauthorized tools or invalid agent IDs during validation.
- **Test 3:** Seamless execution of validated generated workflows through `DeterministicOrchestrator` and Phase 09 `Reviewer`.
- **Test 4:** Preservation of planning provenance in `workflow.current_state` and task metadata.
- **Test 5:** Full backward compatibility with existing static workflow tests.
