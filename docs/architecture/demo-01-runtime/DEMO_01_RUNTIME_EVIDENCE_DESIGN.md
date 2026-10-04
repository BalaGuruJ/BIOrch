# BIOrch Demo #1 — Runtime Evidence & Run Log Design

## 1. Executive Summary
This design document defines the runtime evidence and run artifact collection mechanism for **BIOrch Demo #1**. To provide a self-contained, verifiable proof of what BIOrch orchestrated, executed, and synthesized during a demonstration run, every execution of `runtime_demo.py` will automatically produce a structured evidence bundle under:

`artifacts/demo-01/runs/<run_id>/`

This mechanism bridges the gap between ephemeral in-memory runtime execution results (`HandoffPayload`, `WorkflowResult`, `ToolResult`) and permanent, inspectable audit artifacts required for stakeholder demonstration.

---

## 2. Investigation Findings: Current vs. Missing Evidence

### Currently Available (In-Memory)
- **Workflow DAG & Tasks:** Structured in `Workflow` and `Task` objects, showing task identifiers, objectives, agent assignments, and dependencies (`dependencies=[]`).
- **Parallel Eligibility:** Tasks with empty dependencies (`dependencies=[]`) are dispatched concurrently via `DeterministicOrchestrator` using a `ThreadPoolExecutor`.
- **Tool Execution & Results:** `ToolResult` objects containing status (`SUCCESS`/`FAILED`), data summaries, and tool provenance timestamps/artifacts.
- **Workflow Results:** `WorkflowResult` tracking completed tasks, step results, duration, and status.
- **Synthesis:** `synthesize_result()` aggregating task attributions, findings, and status.
- **Provenance:** `ProvenanceValidator` computing SHA-256 audit checksums and verifying attribution integrity.

### Missing (To Be Implemented)
- **Persistent Evidence Bundle Directory:** A dedicated folder `artifacts/demo-01/runs/<run_id>/` containing machine-readable JSON files and a human-readable markdown summary.
- **Run Identifier (`run_id`):** Unique run tracking (e.g., `run_20261004_120000_<uuid>`).
- **Run Timing:** Explicit start and end UTC timestamps for the overall demonstration run.
- **Thread/Executor Evidence:** Explicit capture of worker thread / executor identities during parallel task dispatch.
- **Normalized Per-Integration Results:** Dedicated JSON files for Tableau and Power BI extraction outputs.

---

## 3. Proposed Run-Output Directory Structure

```
artifacts/
└── demo-01/
    └── runs/
        └── run_20261004_123456_a1b2c3d4/
            ├── run_manifest.json
            ├── workflow.json
            ├── execution.json
            ├── tableau_result.json
            ├── powerbi_result.json
            ├── provenance.json
            ├── synthesis.json
            └── run_summary.md
```

---

## 4. Evidence Schema & File Mapping

1. **`run_manifest.json`**:
   - `run_id`: Unique run identifier string.
   - `demo_scenario`: Description of Demo #1.
   - `start_timestamp`: ISO-8601 start time.
   - `end_timestamp`: ISO-8601 end time.
   - `overall_status`: `SUCCESS`, `PARTIAL`, or `FAILED`.
   - `environment`: Python version, OS, platform status.

2. **`workflow.json`**:
   - `workflow_id`: Workflow identifier.
   - `version`: Workflow version.
   - `tasks`: List of tasks with `task_id`, `objective`, `agent_id`, `dependencies`, `inputs`, `status`.
   - `parallel_eligible_tasks`: Count and IDs of tasks eligible for parallel execution.

3. **`execution.json`**:
   - Step results from `workflow_result.step_results`.
   - `task_execution_metrics`: Per-task execution records containing `task_id`, `agent_id`, `start_timestamp`, `end_timestamp`, `duration_seconds`, `thread_id`, `thread_name`, `status`, and `errors`.
   - `concurrency_proof`: Empirical concurrency verification data proving actual execution overlap and distinct thread utilization (`parallel_execution_verified`, `overlap_detected`, `distinct_threads_used`, `pairwise_comparisons`).

4. **`tableau_result.json`**:
   - Raw data and tool result provenance from `tableau_extractor`.
   - Extracted entity counts (datasources, tables, columns, worksheets).
   - Artifact paths.

5. **`powerbi_result.json`**:
   - Raw data and tool result provenance from `powerbi_adapter`.
   - Extracted entity counts (tables, columns, relationships).
   - Fail-closed execution status (handling missing .NET runtime gracefully without fake mocks).

6. **`provenance.json`**:
   - Planner provenance (`workflow.current_state["planner"]`).
   - Task rationales (`task.metadata["planner_rationale"]`).
   - Audit checksum computed by `ProvenanceValidator`.

7. **`synthesis.json`**:
   - Output of `synthesize_result(handoff)` containing consolidated findings and task attributions.

8. **`run_summary.md`**:
   - Concise human-readable narrative answering the 10 required demonstration questions:
     1. Intent requested
     2. Plan generated
     3. Tasks created
     4. Tasks run
     5. Concurrency execution proof (Tableau & Power BI parallel execution)
     6. Integration statuses
     7. Provenance captured
     8. Final synthesis result
     9. Run success/failure status
     10. Failure diagnostics (if any)

---

## 5. Architectural Safeguards
- **No Protected Architecture Modifications:** `DeterministicOrchestrator`, `ToolGateway`, `AgentResolver`, and `ProvenanceValidator` core classes remain unaltered.
- **No Mocking Power BI:** The evidence mechanism records actual execution outcomes; if Power BI prerequisites are missing, it accurately records failure/incomplete status rather than inventing fake data.
- **File System Isolation:** Evidence is written strictly under `artifacts/demo-01/runs/` (or temporary directories during unit tests).
