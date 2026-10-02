# BIOrch Deterministic Result Synthesis Contract

**Contract ID:** BIORCH-SYNTH-001  
**Contract Name:** Deterministic Result Synthesis Contract  
**Phase:** Phase 08.4G — Result Synthesis  
**Status:** DRAFT  
**Depends On:**  
- BIORCH-ORCH-001 — Deterministic Orchestrator Contract (Sections 12, 13, 21.7, 25.4)  
- BIORCH-AGENT-001 — Deterministic Agent Contract  

---

## 1. Purpose

This contract defines the authoritative architectural boundary and behavioral requirements for Phase 08.4G (Result Synthesis) of the BIOrch parallel orchestration architecture.

Phase 08.4G is responsible for deterministically transforming the validated, declared-order task outputs delivered by the Phase 08.4F Join Gate into a unified, attributed, machine-readable synthesis artifact.

Result synthesis is a deterministic aggregation and structured reporting component. It MUST NOT perform autonomous planning, probabilistic inference, or semantic reinterpretation of specialist outputs.

---

## 2. Architectural Position

The canonical pipeline for parallel workflow termination and result handling is:

    Parallel Worker Execution (Phase 08.4D)
                     ↓
    Terminal Outcome Reconciliation (Phase 08.4E)
                     ↓
    Deterministic Join Gate (Phase 08.4F)
                     ↓
    Result Synthesis (Phase 08.4G)
                     ↓
    Provenance Validation & Audit (Phase 08.4H)

Phase 08.4G operates strictly downstream of the Phase 08.4F Join Gate and strictly upstream of the Phase 08.4H Provenance Validation layer.

Phase 08.4G MUST NOT bypass the Phase 08.4F Join Gate, nor may it consume raw worker outputs directly from Phase 08.4D or Phase 08.4E.

---

## 3. Authoritative Input Boundary

Phase 08.4G MUST consume exclusively the `HandoffPayload` object produced and handed off by the Phase 08.4F Join Gate.

The incoming `HandoffPayload` carries:
- `workflow`: The original workflow definition.
- `workflow_result`: The generic `WorkflowResult` object (containing execution status, results, etc.).
- `synthesis_eligible`: The eligibility flag determined by the Join Gate.
- `artifacts`: Collected worker artifacts.

Phase 08.4G MUST NOT accept raw worker outputs, and it MUST NOT attempt to re-reconcile worker states already finalized by Phase 08.4E and Phase 08.4F.

---

## 4. Synthesis Eligibility Rules

Before proceeding with synthesis transformations, Phase 08.4G MUST evaluate synthesis eligibility based on the 08.4F Join Gate output:

1. **Eligibility Flag Verification:** The 08.4F Join Gate determines whether synthesis is permitted (`synthesis_eligible`). If `synthesis_eligible == False`, synthesis MUST fail closed or produce a designated terminal failure result with no synthesized findings.
2. **Terminal Status Compatibility:**
   - If `WorkflowResult.status == REJECTED`, synthesis MUST NOT execute; the output status MUST be `FAILED`.
   - If `WorkflowResult.status == FAILED`, synthesis is permitted ONLY IF all failed tasks are classified as non-essential under `BIORCH-ORCH-001` Section 9.2, yielding a `PARTIAL` synthesis status. If any essential task failed, synthesis MUST produce a `FAILED` status with no synthesized findings.
   - If `WorkflowResult.status == SUCCESS`, synthesis proceeds to produce a `SUCCESS` status.

---

## 5. Deterministic Ordering Requirements

Synthesis MUST process and output all task findings strictly in declared workflow order:

1. The order of task records in synthesis output MUST match the original task sequence declared in the `Workflow` definition.
2. Synthesis output MUST NOT depend on the execution completion order of concurrent workers.
3. Multiple executions of the same workflow with identical task results MUST produce identical, byte-for-byte deterministic synthesis output.
4. No task finding may be reordered based on arrival time, task duration, or worker thread identifier.

---

## 6. Treatment of Worker Terminal States

Phase 08.4G MUST handle each worker terminal state deterministically, ensuring failed, timed out, and unexecuted tasks remain explicitly visible in the synthesized output:

- **SUCCESS:** The task findings and artifacts are incorporated into the synthesized output with source task attribution preserved.
- **FAILED:** The task is recorded with status `FAILED`; its recorded errors are aggregated; its findings list remains empty.
- **TIMEOUT:** The task is recorded with status `TIMEOUT`; timeout details are preserved in the error list; its findings list remains empty.
- **NOT_EXECUTED:** The task is recorded with status `NOT_EXECUTED`; recorded as an unexecuted dependency; its findings list remains empty.

Under no circumstances may a failed, timed out, or unexecuted task be silently omitted or converted into a successful result.

---

## 7. Preservation of Attribution

Phase 08.4G MUST maintain complete end-to-end attribution:

1. Every finding in the synthesized output MUST explicitly retain the `task_id` of the task that generated it.
2. Every task record MUST retain the `agent_id` of the specialist agent to which the task was assigned, where grounded by the runtime task definition.
3. Synthesis MUST NOT collapse findings into an untyped or unassigned global pool.
4. Lineage and source attribution present in task findings MUST remain unmodified.

---

## 8. Permitted Synthesis Transformations

Phase 08.4G is permitted to perform ONLY the following structural transformations:

1. **Deterministic Aggregation:** Collating task-level findings into `aggregated_findings` strictly preserving declared task sequence and task attribution.
2. **Attribution Mapping:** Generating `task_attributions` mapping each declared task to its terminal status, findings, artifacts, and errors.
3. **Error Consolidation:** Aggregating workflow-level and step-level errors into a consolidated error list.
4. **Metadata & Provenance Forwarding:** Forwarding incoming execution provenance with the addition of deterministic synthesis completion metadata.

---

## 9. Prohibited Operations / Negative Invariants

Phase 08.4G MUST NOT:

1. **No Autonomous Planning:** Employ LLMs, probabilistic models, or dynamic planners to generate, remove, or modify findings.
2. **No Semantic Reinterpretation:** Modify, summarize, reword, or interpret the structured contents of specialist findings.
3. **No Deduplication:** Silently merge, collapse, or discard findings across tasks, even if findings appear identical.
4. **No Prioritization or Ranking:** Reorder or score findings based on subjective importance, confidence, or severity heuristics.
5. **No Entity Invention:** Introduce arbitrary identifiers or entities not grounded in repository contracts (e.g. `finding_id`, `result_id`, `FinalEvidenceResult`).
6. **No Platform-Specific Assumptions:** Introduce Tableau-specific or Power BI-specific synthesis semantics.
7. **No Tool or Direct Execution Access:** Directly invoke tools, subagents, or shell commands.

---

## 10. Framework and Platform Neutrality

Phase 08.4G MUST remain strictly framework-neutral and platform-neutral:

- It MUST NOT depend on Gemini CLI, CrewAI, LangGraph, AutoGen, or any external framework.
- It MUST NOT assume specific BI platform paradigms (Tableau vs Power BI); outputs from both domains MUST be processed uniformly as structured task findings.

---

## 11. Failure and Partial-Result Behavior

The terminal `status` of the synthesized output MUST be one of:

- **`SUCCESS`:** All declared tasks completed with status `SUCCESS` and were synthesized.
- **`PARTIAL`:** All essential tasks completed successfully, but one or more non-essential tasks resulted in `FAILED`, `TIMEOUT`, or `NOT_EXECUTED`. The synthesized output contains findings from successful tasks and explicit failure records for incomplete tasks.
- **`FAILED`:** Workflow was rejected, an essential task failed or timed out, or synthesis eligibility was not satisfied. No synthesized findings are returned.

---

## 12. Output Contract

Phase 08.4G produces a `SynthesisResult` conforming to `schemas/synthesis_result.schema.json`:

```text
SynthesisResult
├── workflow_id (string)
├── workflow_version (string)
├── status ("SUCCESS" | "FAILED" | "PARTIAL")
├── synthesis_eligible (boolean)
├── task_attributions (array)
│    └── [task_id, agent_id, status, findings, artifacts, errors]
├── aggregated_findings (array)
│    └── [task_id, data]
├── errors (array of string)
└── provenance (object)
```

The output structure is strictly defined by `schemas/synthesis_result.schema.json`.

---

## 13. Provenance Preservation and Handoff

Phase 08.4G MUST preserve all provenance data received from the 08.4F Join Gate without loss or mutation.

Synthesis-specific metadata added to `provenance` MUST include:
- `synthesis_contract`: "BIORCH-SYNTH-001"
- `synthesis_version`: "1.0"
- `synthesis_status`: Terminal status (`SUCCESS`, `FAILED`, `PARTIAL`)
- `synthesis_task_count`: Total number of tasks synthesized

The resulting object MUST be passed intact to Phase 08.4H (Provenance Validation & Audit).

---

## 14. Conformance and Acceptance Criteria

An implementation complies with this contract only when:

1. It consumes exclusively `HandoffPayload` from Phase 08.4F.
2. It enforces fail-closed behavior when `synthesis_eligible` is false.
3. It guarantees deterministic declared workflow ordering regardless of worker completion order.
4. It preserves task attribution for all findings.
5. It preserves visibility of failed, timed-out, and unexecuted tasks.
6. It performs NO deduplication, prioritization, or semantic reinterpretation.
7. It does not introduce ungrounded identifiers (`finding_id`, `result_id`, `FinalEvidenceResult`).
8. It serializes output strictly valid against `schemas/synthesis_result.schema.json`.
9. It preserves provenance for Phase 08.4H verification.

---

## 15. Unresolved Architectural Decisions

The following items cannot be grounded in the current repository state and are explicitly deferred:

1. **Domain-Specific Cross-Platform Reconciliation (Phase 11):** Semantic matching (e.g. comparing Tableau calculated fields against Power BI DAX measures) is deferred to Phase 11 and MUST NOT be conflated with Phase 08.4G generic result synthesis.
2. **Provenance Audit Cryptography (Phase 08.4H):** Hashing or cryptographic signing of execution records is deferred to Phase 08.4H.
