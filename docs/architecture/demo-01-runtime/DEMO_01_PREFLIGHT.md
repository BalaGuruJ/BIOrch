# BIOrch Demo #1 — Runtime Capability Preflight Report

## 1. Demo Objective
Demonstrate an end-to-end execution flow where a natural-language BI analysis request is translated into a canonical workflow, dispatched in parallel to Tableau and Power BI extraction/analysis agents, and compiled into verified structured results with complete provenance tracking.

**Target Scenario:**
"Analyze the supplied Tableau workbook and Power BI model for their sales-related metadata. Run the Tableau and Power BI analysis in parallel and return structured results with provenance."

---

## 2. Current Runtime Architecture
BIOrch features a fully implemented, deterministic multi-agent orchestration runtime consisting of:
- **`ToolGateway` / `RuntimeDemoGateway`:** Enforces security classifications, tool registration, permitted operations, and resource allowlists.
- **`AgentResolver`:** Resolves agent identifiers to deterministic executor wrappers (`DeterministicAgentExecutor`).
- **`DeterministicOrchestrator`:** Manages workflow execution order, concurrency (`ThreadPoolExecutor`), timeouts, dependency DAG resolution, and step failure classification.
- **`DeterministicJoinGate`:** Validates join conditions and workflow completion status.
- **`synthesize_result`:** Aggregates task attributions, findings, and provenance into a unified result payload.
- **`ProvenanceValidator`:** Computes and verifies audit checksums and provenance consistency.

---

## 3. Natural Language → Planner Path
- **Path Status:** Implemented.
- **Execution Flow:** 
  1. `LLMPlannerService` receives natural language intent and context.
  2. `MockLLMProvider` (or LLM provider) generates a `CandidatePlan` containing `CandidateTask` definitions with structured operations and rationales.
  3. `PlanCompiler` translates the `CandidatePlan` into a canonical `Workflow` object containing `Task` instances with strict 1:1 non-empty objective mapping and injected planner provenance in `workflow.current_state["planner"]` and `task.metadata["planner_rationale"]`.

---

## 4. Tableau Execution Path
- **Path Status:** Fully Executable.
- **Input Artifact:** `examples/artifacts/tableau/superstore_base.twb`
- **Execution Flow:**
  - Invokes `tableau_extractor` tool via `RuntimeDemoGateway`.
  - Executes `run_pipeline` from `src/biorch/integrations/tableau/cli.py`.
  - Parses workbook XML, extracts datasources, tables, columns, and worksheets, and outputs canonical metadata JSON.

---

## 5. Power BI Execution Path
- **Path Status:** Implemented (Requires .NET Runtime & TOM Assemblies).
- **Input Artifact:** `examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel`
- **Execution Flow:**
  - Invokes `powerbi_adapter` tool via `RuntimeDemoGateway`.
  - Utilizes `PowerBIAdapter` (`src/biorch/integrations/powerbi/adapter.py`) to load the semantic model via pythonnet and Microsoft Analysis Services Tabular Object Model (TOM) assemblies.
  - Serializes/canonicalizes model entities into canonical data structures.
- **Dependencies:** Requires `.NET` runtime (`DOTNET_ROOT`) and TOM DLL path (`BIORCH_TOM_DLL_PATH` pointing to `.deps/microsoft.analysisservices/19.117.0/lib/net6.0/Microsoft.AnalysisServices.Tabular.dll`).

---

## 6. Parallel Execution Path
- **Path Status:** Fully Implemented & Tested.
- **Execution Flow:**
  - `DeterministicOrchestrator.execute()` uses `ThreadPoolExecutor` to dispatch independent tasks (`dependencies=[]`, `is_parallel_eligible=True`) concurrently.
  - Both `tableau_task` and `pbi_task` run simultaneously in separate threads, collecting results and artifacts deterministically.

---

## 7. Provenance Path
- **Path Status:** Fully Implemented.
- **Mechanisms:**
  - Planner provenance: `workflow.current_state["planner"]` (contains plan ID, intent, compiler version, timestamp).
  - Task rationale: `task.metadata["planner_rationale"]`.
  - Execution provenance: Tool result provenance dictionaries including timestamps and file artifacts.
  - Audit validation: `ProvenanceValidator` computes and verifies SHA-256 audit checksums.

---

## 8. Reviewer Integration
- **Path Status:** Implemented.
- **Mechanism:** Optional `Reviewer` and review policies (`src/biorch/review.py`) can inspect step outputs, evaluate rule results, and inject correction feedback for iterative refinement loops.

---

## 9. Available Sample Inputs
- **Tableau:** `/home/balaguruj8/BIOrch/examples/artifacts/tableau/superstore_base.twb`
- **Power BI:** `/home/balaguruj8/BIOrch/examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel`

---

## 10. Environment Preconditions

| Requirement | Classification | Description |
| :--- | :--- | :--- |
| **Python 3.12+ & `.venv`** | REQUIRED | Virtual environment located at `.venv`. |
| **Editable Package Install** | REQUIRED | `pip install -e .` to make `biorch` importable. |
| **Tableau Sample (`superstore_base.twb`)** | REQUIRED | Present in repository artifacts. |
| **.NET 8+ Runtime (`DOTNET_ROOT`)** | CONDITIONAL (Power BI) | Required by pythonnet / TOM interop. |
| **TOM DLL (`BIORCH_TOM_DLL_PATH`)** | CONDITIONAL (Power BI) | Located at `.deps/microsoft.analysisservices/19.117.0/lib/net6.0/Microsoft.AnalysisServices.Tabular.dll`. |
| **Live External LLM API Keys** | NOT REQUIRED | Mock LLM provider and deterministic execution paths function fully offline. |

---

## 11. Exact Commands Available Today

1. **Run the End-to-End Runtime Demo:**
   ```bash
   python src/biorch/runtime_demo.py
   ```
   *(With Power BI environment variables set)*:
   ```bash
   export DOTNET_ROOT=/usr/share/dotnet
   export BIORCH_TOM_DLL_PATH=$(pwd)/.deps/microsoft.analysisservices/19.117.0/lib/net6.0/Microsoft.AnalysisServices.Tabular.dll
   python src/biorch/runtime_demo.py
   ```

2. **Run Demo & Integration Tests:**
   ```bash
   .venv/bin/pytest tests/test_runtime_demo.py
   ```

---

## 12. Missing Pieces / Blockers
- No missing code features or architectural gaps.
- Blocker is strictly environmental: standard host environment requires .NET SDK/runtime installation (`dotnet-sdk`) and editable package registration (`pip install -e .`) to execute Power BI TOM interop tests.

---

## 13. Recommended Preflight Result

**B. READY WITH ENVIRONMENT SETUP**

---

## 14. Evidence Index
- `src/biorch/runtime_demo.py` (End-to-end orchestration demo script)
- `tests/test_runtime_demo.py` (Pytest test suite verifying demo gateway, parallel execution, and CLI entrypoint)
- `src/biorch/orchestration/orchestrator.py` (Deterministic orchestrator with thread pool parallel execution)
- `src/biorch/planner/compiler.py` (Canonical plan compiler)
- `src/biorch/integrations/tableau/cli.py` (Tableau pipeline execution)
- `src/biorch/integrations/powerbi/adapter.py` (Power BI semantic model adapter)
