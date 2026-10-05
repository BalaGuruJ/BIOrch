# BIOrch Demo #1 — Run Summary

## Run Identifier
- **Run ID:** `run_20261004_183647_b843c99a`
- **Start Time:** `2026-10-04T18:36:47.741259+00:00`
- **End Time:** `2026-10-04T18:36:48.896358+00:00`
- **Overall Status:** **FAILED**

---

## Demonstration Questions & Evidence

1. **What intent was requested?**
   - *Answer:* Analyze the supplied Tableau workbook (`superstore_base.twb`) and Power BI model (`AdventureWorks Sales.SemanticModel`) for sales-related metadata in parallel.

2. **What plan was generated?**
   - *Answer:* Plan ID `plan_demo_01_runtime` compiled by `PlanCompiler` with strict 1:1 objective mapping and injected planner provenance.

3. **What tasks were created?**
   - *Answer:* Two canonical tasks: `tableau_task` (assignee: `tableau_agent`) and `pbi_task` (assignee: `powerbi_agent`).

4. **Which tasks ran?**
   - *Answer:* [].

5. **Were Tableau and Power BI actually executed concurrently?**
   - *Answer:* Yes, verified empirically via runtime execution metrics (overlap detected on distinct worker threads).
     - **tableau_task:** start=`2026-10-04T18:36:47.752289+00:00`, end=`2026-10-04T18:36:48.893351+00:00`, duration=`1.1411s`, thread=`132831134082752`
     - **pbi_task:** start=`2026-10-04T18:36:47.751890+00:00`, end=`2026-10-04T18:36:48.536550+00:00`, duration=`0.7847s`, thread=`132831142475456`
     - **Overlap Detected:** `True` | **Distinct Threads:** `True`

6. **What were their statuses?**
   - *Answer:* Tableau status: **NOT_EXECUTED** | Power BI status: **FAILED**.

7. **What provenance was captured?**
   - *Answer:* Planner provenance in `workflow.current_state["planner"]`, task rationales in `task.metadata`, and tool result timestamps/artifacts. Audit Checksum Validation: **VALID**.

8. **What was the final synthesized result?**
   - *Answer:* Synthesis status: **FAILED** (consolidated across 2 task attributions).

9. **Did the run succeed or fail?**
   - *Answer:* Run status: **FAILED**.

10. **If it failed, exactly where and why?**
    - *Answer:* Check execution.json and powerbi_result.json for detailed failure diagnostics (e.g. Power BI .NET/TOM environment prerequisites).

---
*Evidence bundle generated at: `/home/balaguruj8/BIOrch/artifacts/demo-01/runs/run_20261004_183647_b843c99a`*
