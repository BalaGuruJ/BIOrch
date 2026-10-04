# BIOrch Demo #1 — Parallel Execution Forensic Investigation Report

## 1. Investigation Objective
Perform a read-only forensic investigation to determine why BIOrch Demo #1 (`tableau_task` and `pbi_task`) executed sequentially (`overlap_detected=false`, `distinct_threads_used=false`) rather than concurrently during the runtime execution of `src/biorch/runtime_demo.py`, despite documentation and architectural intent stating that independent tasks with `dependencies=[]` run in parallel.

---

## 2. Trace of the Execution Path

1. **Natural-language / Planner Path:**
   - Simulated planner metadata in `runtime_demo.py` specifies intent to analyze Tableau and Power BI models in parallel.
2. **Workflow Construction (`src/biorch/runtime_demo.py`):**
   - `tableau_task` and `pbi_task` were instantiated directly using `Task(...)` without explicitly providing `is_parallel_eligible=True`.
3. **Task Definition Default (`src/biorch/core/task.py`):**
   - The `Task` Pydantic model defines `is_parallel_eligible: bool = Field(default=False, ...)`.
   - Consequently, both tasks defaulted to `is_parallel_eligible = False`.
4. **DeterministicOrchestrator Execution (`src/biorch/orchestration/orchestrator.py`):**
   - The orchestrator maintains a `ThreadPoolExecutor` and iterates over ready tasks.
   - For each ready task submitted to the executor, the dispatch loop checks:
     ```python
     if not task.is_parallel_eligible:
         wait([futures[task.task_id]["future"]], timeout=timeout_val)
         break
     ```
   - Because `is_parallel_eligible` was `False`, the orchestrator immediately awaited the future of `pbi_task` and broke out of the dispatch loop, forcing sequential execution before evaluating `tableau_task`.

---

## 3. Investigation Findings (Ten Questions Answered)

1. **Did both tasks reach the ThreadPoolExecutor concurrently?**
   - No. `pbi_task` was submitted, executed, and completed before `tableau_task` was submitted.
2. **Did DeterministicOrchestrator submit both futures before waiting for either result?**
   - No. The `if not task.is_parallel_eligible:` guard caused an immediate synchronous wait and loop break after submitting the first task.
3. **Did any dependency, ordering rule, executor configuration, task classification, or wrapper cause serialization?**
   - Yes, **task classification** (`is_parallel_eligible=False` due to omitting `is_parallel_eligible=True` during manual instantiation in `runtime_demo.py`) triggered the orchestrator's non-parallel serialization branch.
4. **Can AgentResolver / DeterministicAgentExecutor serialize execution?**
   - No. They are passive routing and execution wrappers.
5. **Does TimedAgentExecutor change execution semantics?**
   - No. It is purely an observational wrapper measuring timing, duration, thread ID, and status.
6. **Does RuntimeDemoGateway or integration paths introduce global locks/singletons?**
   - No. Both integration paths are thread-safe and stateless with respect to orchestration execution.
7. **Is single-thread execution caused by executor worker count?**
   - No. `ThreadPoolExecutor()` defaults to multiple workers. The cause is purely task eligibility configuration.
8. **Does the real runtime execution path differ from the unit-test parallel execution path?**
   - Yes. `PlanCompiler` automatically sets `is_parallel_eligible=True`, whereas `runtime_demo.py` constructed tasks manually without setting `is_parallel_eligible=True`.
9. **Do unit tests prove real concurrent execution or simulate it?**
   - Unit tests in `test_parallel_dispatch.py` test orchestrator logic with mock delays, but `runtime_demo.py` demo execution script instantiated tasks without setting `is_parallel_eligible=True`.
10. **Evidence Bundle Reconstruction (`artifacts/demo-01/runs/run_20261004_181854_2fdfd3be`):**
    - `pbi_task`: start `18:18:54.666`, end `18:18:57.559`, duration `2.893s`, thread `137282488936128` (`ThreadPoolExecutor-0_0`)
    - `tableau_task`: start `18:18:57.560`, end `18:18:58.713`, duration `1.1527s`, thread `137282488936128` (`ThreadPoolExecutor-0_0`)
    - Concurrency proof: `overlap_detected=false`, `distinct_threads_used=false`, `parallel_execution_verified=false`.

---

## 4. Classification
**C. SERIALIZATION IN ORCHESTRATION LOGIC** (triggered by task configuration `is_parallel_eligible=False` in `runtime_demo.py`).

---

## 5. Summary & Concluding Answers

1. **Root cause:** `runtime_demo.py` constructed `tableau_task` and `pbi_task` without specifying `is_parallel_eligible=True`, causing `DeterministicOrchestrator` to enforce sequential execution via its `is_parallel_eligible=False` serialization guard.
2. **Evidence:** Execution timestamps in `execution.json` show strict sequential execution (`pbi_task` ends at 18:18:57.559; `tableau_task` starts at 18:18:57.560 on the exact same thread ID).
3. **Classification:** **C** (Serialization in orchestration logic / task configuration).
4. **Whether this is an actual defect:** Yes, it is a configuration/instantiation defect in `runtime_demo.py` where the demo script failed to set `is_parallel_eligible=True` on independent demo tasks, preventing the demonstrated parallel execution.
5. **Smallest correction point:** Setting `is_parallel_eligible=True` on both `tableau_task` and `pbi_task` in `src/biorch/runtime_demo.py`. (Note: Per strict instructions, no code changes or fixes are implemented during this investigation phase).
6. **Whether Demo #1 can be considered complete:** Demo #1 completed a successful functional extraction and synthesis run (overall status SUCCESS), but did not achieve true parallel concurrent execution due to the task configuration omission.
7. **Exact next SINGLE human action:** Review this forensic investigation report and authorize an implementation task to set `is_parallel_eligible=True` in `src/biorch/runtime_demo.py`.
