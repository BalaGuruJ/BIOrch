# Phase 10 — LLM-Based Adaptive Planning: Implementation Task

## 1. Objective
Implement Phase 10 (LLM-Based Adaptive Planning) within BIOrch, enabling the system to accept natural language user intents, generate structured `CandidatePlan` representations via an abstract `LLMProvider` interface, deterministically compile them into canonical `Workflow` and `Task` instances via `PlanCompiler`, validate them against strict schema and security boundaries, and execute them using the existing `DeterministicOrchestrator` and Phase 09 `Reviewer` loops.

## 2. Implementation Scope
- **CandidatePlan Model:** Define the intermediate data structure (`CandidatePlan`, `CandidateTask`) capturing plan metadata, intent, and tasks with explicit objectives, agent IDs, operations, inputs, dependencies, and rationale.
- **LLMProvider Abstraction:** Implement an abstract provider interface (`LLMProvider`) along with a concrete deterministic mock provider (`MockLLMProvider`) and optionally an API-backed provider to generate candidate plans.
- **PlanCompiler:** Implement a pure, deterministic compiler translating `CandidatePlan` -> canonical `Workflow` / `Task` models with 1:1 objective mapping, fail-closed handling for missing/empty objectives, and provenance injection (`workflow.current_state["planner"]`, `task.metadata["planner_rationale"]`).
- **Planner Service / Integration:** Provide a high-level coordination entrypoint (`LLMPlannerService`) that coordinates intent parsing, plan generation, compilation, validation via `DeterministicOrchestrator.validate_workflow()`, and execution.
- **Testing & Validation:** Add comprehensive unit and integration tests (`tests/test_llm_planner.py`) covering successful planning, validation rejection, mock provider determinism, and provenance preservation.

## 3. Exact Files / Modules Expected to be Added
- `src/biorch/planner/__init__.py`
- `src/biorch/planner/models.py`
- `src/biorch/planner/provider.py`
- `src/biorch/planner/compiler.py`
- `src/biorch/planner/service.py`
- `tests/test_llm_planner.py`

## 4. Existing Files Protected from Modification
All existing Phase 01–09 source code (`src/biorch/core/`, `src/biorch/gateway/`, `src/biorch/agent/`, `src/biorch/orchestrator/`, `src/biorch/review/`, etc.), schemas (`schemas/`), existing contracts (`contracts/`), and existing unit tests (`tests/test_*.py` excluding `tests/test_llm_planner.py`) are strictly protected from modification. Phase 10 is purely additive.

## 5. CandidatePlan Requirements
- Must contain `plan_id`, `intent`, `target_model`, and `tasks`.
- Each candidate task must contain `task_id`, `objective` (non-empty string), `agent_id`, `operation`, `inputs`, `dependencies`, and `rationale`.
- Must support serialization/deserialization to/from JSON/dict formats.

## 6. PlanCompiler Requirements
- Pure, deterministic mapping from `CandidatePlan` to canonical `Workflow` and `Task` instances.
- 1:1 mapping of `CandidateTask.objective` → `Task.objective`.
- Fail closed immediately if `objective` is missing, empty, or unassigned.
- Separate `rationale` into `task.metadata["planner_rationale"]`.
- Inject planning metadata (`workflow.current_state["planner"]`) without modifying execution behavior.
- No implicit task creation, auto-correction, or prompt guessing.

## 7. LLMProvider Abstraction Boundary
- Abstract base class `LLMProvider` with method `generate_plan(intent: str, context: dict) -> CandidatePlan`.
- Support pluggable implementations (e.g. `MockLLMProvider` for deterministic testing).
- Isolates LLM client communication from compilation and execution logic.

## 8. Planner / Execution Security Boundary
- The LLM Planner has **no direct tool execution access**.
- Planner never talks to `ToolGateway` or executes agent tasks directly.
- `AgentResolver` and `ToolGateway` remain fully authoritative.
- Generated plans are subject to strict deterministic validation before any execution is permitted.

## 9. Validation and Fail-Closed Behavior
- Compiled workflows must pass `DeterministicOrchestrator.validate_workflow()`.
- Validations include schema compliance, dependency acyclicity, agent existence in `AgentResolver`, and tool allowlist verification.
- Any planning failure or validation failure fails closed immediately (`WorkflowResultStatus.REJECTED` or raised exception).

## 10. Provenance Requirements
- Workflow-level state (`workflow.current_state["planner"]`) captures planner ID, model identifier, timestamp, and source intent.
- Task-level metadata captures planner rationale.
- Provenance must remain intact and pass cryptographic checksum verification (`ProvenanceValidator`).

## 11. Deterministic Mock-Provider & Testing Requirements
- `MockLLMProvider` must generate fully reproducible candidate plans for given intents.
- Test suite (`tests/test_llm_planner.py`) must verify successful planning, compilation, validation, execution, rejection of unauthorized tool usage, and provenance audit integrity.

## 12. Backward-Compatibility Requirements
- Phase 01–09 deterministic execution workflows, static orchestrators, multi-agent routers, parallel dispatch, and review loops must continue to function identically without regression.

## 13. Explicit Acceptance Criteria
1. All new modules under `src/biorch/planner/` implemented cleanly and type-safely.
2. `PlanCompiler` strictly enforces 1:1 non-empty objective mapping and fails closed on violations.
3. `DeterministicOrchestrator` successfully validates and executes LLM-generated workflows.
4. Comprehensive test suite (`tests/test_llm_planner.py`) passes successfully with `pytest`.
5. Existing test suite (`tests/test_*.py`) passes without regressions.
6. Zero modifications made to protected core files or existing contracts/schemas.

## 14. Prohibited Actions / Out-of-Scope Work
- Direct tool execution from planner code.
- Auto-correcting malformed candidate plans or guessing missing agent IDs.
- Modifying core orchestrator, agent, or gateway source code.
- Modifying existing contracts or schemas.
