# Runtime Tableau + Power BI Orchestration Wiring Design Review

**Phase:** Phase 08 / Runtime Integration  
**Document:** `governance/gemini/phase-08-parallel-orchestration/RUNTIME_TABLEAU_PBI_WIRING_DESIGN_REVIEW.md`  
**Status:** Read-Only Design Review / Investigation Report  
**Date:** October 3, 2026  

---

## 1. Executive Summary

This investigation evaluates whether the existing, fully working Tableau and Power BI standalone integration pipelines can be wired into the existing BIOrch orchestration runtime as two independent, parallel deterministic tasks executed via `DeterministicOrchestrator`, synthesized via `synthesize_result`, and validated via `ProvenanceValidator`, **without modifying core orchestration architecture, contracts, or schemas**.

Based on an exhaustive code inspection of the BIOrch repository (`src/biorch/`), all necessary runtime primitives already exist:
- **Execution Engine:** `DeterministicOrchestrator`, `AgentResolver`, `DeterministicAgentExecutor`, and `ToolGateway`.
- **Parallel Execution:** ThreadPoolExecutor-based parallel dispatch with dependency tracking (`Task.dependencies`).
- **Synthesis & Provenance:** `DeterministicJoinGate`, `synthesize_result`, and `ProvenanceValidator`.
- **Integration Pipelines:** Standalone Tableau CLI pipeline (`biorch.integrations.tableau.cli`) and Power BI TMDL adapter (`biorch.integrations.powerbi.adapter`).

No modifications to core orchestration contracts, schemas (`schemas/`), or governance records are required to support this wiring.

---

## 2. Current Contract Findings

Inspection of core files (`core/task.py`, `core/workflow.py`, `core/result.py`, `core/agent.py`, `core/gateway.py`, `agents/deterministic_agent.py`, `orchestration/agent_resolver.py`, `orchestration/orchestrator.py`, `orchestration/join_gate.py`, `orchestration/synthesis.py`, `orchestration/provenance_validator.py`) confirms:
1. **Tasks** accept arbitrary `inputs` dictionaries (`tool_id`, `operation`, `tool_inputs`, `resource`).
2. **Agents** (`Agent`) define `allowed_tools` and `supported_operations`.
3. **ToolGateway** enforces authorization against registered `ToolDefinition` schemas, permitted operations, and allowed resource roots.
4. **DeterministicAgentExecutor** bridges tasks to tools via the gateway, mapping successful tool execution results into structured `Result` objects (`SUCCESS`/`FAILURE`, `findings`, `artifacts`, `errors`, `metadata`).
5. **DeterministicOrchestrator** natively supports parallel execution of independent tasks (`dependencies = []`), timeout enforcement, terminal state reconciliation, and join evaluation.
6. **Synthesis** and **ProvenanceValidator** consume `HandoffPayload` and `WorkflowResult` without assumptions about the underlying domain engine.

---

## 3. Tableau Tool/Agent Wiring Design

### ToolDefinition Shape
```python
ToolDefinition(
    tool_id="tableau_extractor",
    name="Tableau Metadata Extractor",
    purpose="Extract canonical entities and relationships from Tableau .twb workbooks",
    version="1.0",
    input_schema={"input_path": "str", "output_directory": "str"},
    output_schema={"status": "str", "artifacts": "list"},
    allowed_resources=["examples/artifacts/tableau/", "/tmp/"],
    permitted_operations=["EXTRACT"],
    security_classification="INTERNAL"
)
```

### Agent Configuration
```python
Agent(
    agent_id="tableau_agent",
    name="Tableau Specialist",
    role="Extracts and canonicalizes Tableau workbook metadata",
    allowed_tools=["tableau_extractor"],
    supported_operations=["EXTRACT"]
)
```

---

## 4. Power BI Tool/Agent Wiring Design

### ToolDefinition Shape
```python
ToolDefinition(
    tool_id="powerbi_adapter",
    name="Power BI TMDL Model Adapter",
    purpose="Deserialize and canonicalize Power BI semantic models from TMDL folders",
    version="1.0",
    input_schema={"model_folder": "str"},
    output_schema={"tables_count": "int", "relationships_count": "int", "columns_count": "int"},
    allowed_resources=["examples/artifacts/powerbi/"],
    permitted_operations=["ANALYZE"],
    security_classification="INTERNAL"
)
```

### Agent Configuration
```python
Agent(
    agent_id="powerbi_agent",
    name="Power BI Specialist",
    role="Deserializes and canonicalizes Power BI TMDL semantic models",
    allowed_tools=["powerbi_adapter"],
    supported_operations=["ANALYZE"]
)
```

---

## 5. Result Mapping Design

### Tableau Result
- **Status:** `ResultStatus.SUCCESS` (or `FAILURE` on exception).
- **Findings:** Summary statistics of extracted entities (`datasources`, `tables`, `columns`, `fields`, `worksheets`).
- **Artifacts:** Absolute or relative file paths to generated output files (`metadata.json`, `tables.csv`, etc.).
- **Errors:** List of exception messages if extraction fails.

### Power BI Result
- **Status:** `ResultStatus.SUCCESS` (or `FAILURE` on exception).
- **Findings:** Model summary (`database_name`, `tables_count`, `relationships_count`, `columns_count`).
- **Artifacts:** List of model entity identifiers or model folder paths.
- **Errors:** List of exception messages if loading/canonicalization fails.

---

## 6. Parallel Execution Design

Both tasks are defined with `dependencies=[]`:
- Task 1: `tableau_task` (agent: `tableau_agent`, inputs referencing `tableau_extractor`)
- Task 2: `powerbi_task` (agent: `powerbi_agent`, inputs referencing `powerbi_adapter`)

Because both have empty dependency lists, `DeterministicOrchestrator.execute()` identifies both as ready simultaneously, sorts them deterministically by `task_id`, and dispatches them concurrently using `ThreadPoolExecutor`.

---

## 7. Join / Synthesis Compatibility
- **JoinGate (`DeterministicJoinGate`):** Evaluates `WorkflowResult` status and aggregates collected artifacts. Fully compatible.
- **Synthesis (`synthesize_result`):** Iterates over workflow tasks in declared order, builds task attributions, aggregates findings, and builds provenance metadata matching `schemas/synthesis_result.schema.json`. Fully compatible.

---

## 8. Provenance Compatibility
- **ProvenanceValidator:** Validates required keys (`workflow_id`, `workflow_version`, `synthesis_contract`, `synthesis_version`, `synthesis_status`, `synthesis_task_count`), checks task attributions length, and computes/verifies SHA-256 cryptographic audit checksums per `SYNTHESIS_CONTRACT.md` Section 15.2. Fully compatible.

---

## 9. Security / Gateway Analysis
- **ToolGateway:** Enforces tool ID existence, version match, permitted operations (`EXTRACT`, `ANALYZE`), and allowed resource roots (`examples/artifacts/`, `/tmp/`). Both Tableau and Power BI inputs reside within authorized paths, satisfying fail-closed security checks.

---

## 10. Exact File-Level Impact
If implementation is authorized in a future phase:
1. **Existing files reused unchanged:** `Workflow`, `Task`, `Result`, `WorkflowResult`, `Agent`, `ToolDefinition`, `ToolGateway`, `DeterministicAgentExecutor`, `AgentResolver`, `DeterministicOrchestrator`, `DeterministicJoinGate`, `synthesis.py`, `ProvenanceValidator`.
2. **New files (optional integration wiring):** A small integration helper module or extension script defining tool handler functions wrapping `run_pipeline` and `PowerBIAdapter`. No core engine code modification required.
3. **Contracts / Schemas:** Zero changes.
4. **Tests:** New integration test file (`tests/test_bi_orchestration_integration.py`).

---

## 11. External Driver vs. Repository Implementation Options
- **External / Temporary Driver Script:** Can instantiate `ToolGateway`, register custom tools wrapping the Tableau CLI runner and Power BI adapter, set up `AgentResolver`, run `DeterministicOrchestrator`, and validate output via `ProvenanceValidator` without touching core repository source code.
- **Repository Integration:** Can be added as a first-class integration module when authorized.

---

## 12. Risks & Limitations
- **Runtime Prerequisites:** Power BI execution requires `.NET` CoreCLR and TOM assembly path (`BIORCH_TOM_DLL_PATH`).
- **Filesystem Side Effects:** Tableau extraction writes CSV files to a directory; tool wrappers must manage temporary staging directories securely.

---

## 13. Final Verdict

### **A. READY FOR IMPLEMENTATION**
Existing contracts fully support the design, and parallel orchestration of Tableau and Power BI pipelines is achievable without modifying core orchestration architecture, contracts, or schemas.

---

### Reference Data
- **Exact files inspected:**
  - `src/biorch/core/task.py`
  - `src/biorch/core/workflow.py`
  - `src/biorch/core/result.py`
  - `src/biorch/core/agent.py`
  - `src/biorch/core/gateway.py`
  - `src/biorch/agents/deterministic_agent.py`
  - `src/biorch/orchestration/agent_resolver.py`
  - `src/biorch/orchestration/orchestrator.py`
  - `src/biorch/orchestration/join_gate.py`
  - `src/biorch/orchestration/synthesis.py`
  - `src/biorch/orchestration/provenance_validator.py`
  - `src/biorch/integrations/tableau/cli.py`
  - `src/biorch/integrations/powerbi/adapter.py`
  - `src/biorch/integrations/powerbi/canonicalizer.py`
  - `src/biorch/integrations/powerbi/validator.py`
  - `src/biorch/integrations/pbi/runtime.py`
- **Exact tests inspected:**
  - `tests/test_orchestrator.py`
  - `tests/test_08_4D_execution.py`
  - `tests/test_08_4H_provenance.py`
  - `tests/test_parallel_dispatch.py`
  - `tests/test_powerbi_integration.py`
  - `tests/test_tableau_serialization.py`
- **Exact commands used:**
  - `PYTHONPATH=src .venv/bin/python3 -m pytest`
  - `PYTHONPATH=src .venv/bin/python3 -m src.biorch.integrations.tableau.cli ...`
- **Exact conclusion:** Existing contracts and orchestration engine fully support parallel execution, synthesis, and provenance validation of Tableau and Power BI pipelines.
- **Whether implementation should proceed:** Awaiting explicit authorization per BIOrch governance rules.
