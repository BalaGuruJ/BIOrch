# Phase 08.4F → 08.4G — Architectural Decision-Support Addendum

## 1. Baseline Artifact Used
- **Primary Reference:** `inspection/phase-08/PHASE_08_4F_08_4G_ARCHITECTURAL_DECISION_SUPPORT.md`
- **Supporting References:**
  - `inspection/phase-08/PHASE_08_4F_08_4G_IMPLEMENTATION_CHANGE_SURFACE.md`
  - `inspection/phase-08/PHASE_08_4F_TO_08_4G_ELIGIBILITY_OWNERSHIP_RESOLUTION.md`
  - `contracts/synthesis/SYNTHESIS_CONTRACT.md`
  - `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`
  - `governance/gemini/PHASE_INDEX.md`

The primary baseline artifact is verified as accurate, grounded, and consistent with the live working tree at commit `9b55af1`. Its findings are adopted directly without duplication.

---

## 2. What Is Already Established

1. **Governance State:** Phase 08.4E is `CLOSED`. Phase 08.4F (Join Gate) is `PENDING`. Phase 08.4G (Result Synthesis) is `PENDING` (`PHASE_INDEX.md`).
2. **Current Runtime Loss Points:** Five distinct data loss points occur in `src/biorch/orchestration/orchestrator.py` before `WorkflowResult` construction: `Task.agent_id`, `Task.is_essential`, `Result.artifacts`, `Result.metadata`, and task definition metadata.
3. **Synthesis Eligibility Ownership:** Section 4.1 of `SYNTHESIS_CONTRACT.md` and Section 25.4 item 7 of `ORCHESTRATOR_CONTRACT.md` establish that the Phase 08.4F Join Gate owns the determination of `synthesis_eligible`.
4. **Current Handoff Object:** `src/biorch/orchestration/result.py` defines `WorkflowResult`, which currently lacks `synthesis_eligible`, `agent_id`, `is_essential`, and `artifacts`.
5. **Contract Inconsistency:** `SYNTHESIS_CONTRACT.md` Section 3 enumerates incoming `WorkflowResult` fields without `synthesis_eligible`, yet Section 4.1 mandates that Phase 08.4G verify `synthesis_eligible` based on the 08.4F Join Gate output.
6. **Backward Compatibility:** Existing Phase 04 / Phase 08.4D orchestration callers and test suites can remain backward-compatible under both options (under Option A via default field values; under Option B by leaving `WorkflowResult` untouched).

---

## 3. What Remains Unresolved

A single, concrete architectural fork remains unresolved:

> **The Boundary Packaging Decision:**  
> Should the Phase 08.4F Join Gate enrich and emit `WorkflowResult` as the sole handoff object to Phase 08.4G (**Option A**), or should it emit a separate composite handoff payload (`HandoffPayload` / `JoinGateOutput`) that packages execution results alongside the workflow definition, leaving `WorkflowResult` in its current generic form (**Option B**)?

### Specific Human Assumptions Requiring Confirmation:
1. **Orchestrator Scope:** Does the project intend `WorkflowResult` to remain a lean, generic execution summary for all workflow types, or should it expand into a unified post-reconciliation container for synthesis?
2. **Contract Revision Appetite:** Is there preference for a minimal contract update (Option A: surgical addition of `synthesis_eligible` to Section 3's list) versus a structural contract revision (Option B: rewriting Section 3 and Section 14.1 to redefine the input contract)?
3. **Artifact Routing:** Should specialist worker artifacts (`Result.artifacts`) be stored directly within `WorkflowResult.step_results`, or routed to the Join Gate separately?
4. **Join Gate Architecture:** Should Phase 08.4F be implemented as an internal method within `DeterministicOrchestrator` or as a standalone component (`DeterministicJoinGate`)?

---

## 4. Minimal Decision Surface for Human Approval

To resolve the architectural fork, human review requires evaluating only three core trade-off axes:

```text
┌───────────────────────────┬───────────────────────────────────┬────────────────────────────────────┐
│ Trade-Off Axis            │ Option A (Enriched WorkflowResult)│ Option B (Composite Payload)       │
├───────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ 1. Object Boundary        │ Single unified object             │ Two distinct objects               │
│                           │ (WorkflowResult carries all)      │ (WorkflowResult + HandoffPayload)  │
├───────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ 2. Contract Impact        │ Surgical text alignment only      │ Structural amendment required      │
│                           │ (SYNTHESIS_CONTRACT.md Sec 3)     │ (SYNTHESIS_CONTRACT.md Sec 3 & 14) │
├───────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ 3. Model Coupling         │ Orchestrator result couples to    │ Orchestrator result remains        │
│                           │ synthesis metadata requirements   │ decoupled; Join Gate couples both  │
└───────────────────────────┴───────────────────────────────────┴────────────────────────────────────┘
```

---

## 5. Consequences That Necessarily Follow from Each Option

### 5.1 If Option A is Approved:
1. `src/biorch/orchestration/result.py` must add `synthesis_eligible: bool = False` to `WorkflowResult`, and enrich `step_results` (or add a structured step model) to hold `agent_id`, `is_essential`, and `artifacts`.
2. `src/biorch/orchestration/orchestrator.py` must retain `result.artifacts` at lines 332–337, compute `synthesis_eligible`, and propagate `agent_id` and `is_essential` into `step_results`.
3. `contracts/synthesis/SYNTHESIS_CONTRACT.md` Section 3 must add `synthesis_eligible` to its enumerated field list.
4. `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` Section 12 should be updated to list `synthesis_eligible`.
5. Existing `tests/test_orchestrator.py` and `tests/test_08_4D_execution.py` remain compatible as long as new fields provide defaults.
6. Phase 08.4F Join Gate can be implemented directly within `DeterministicOrchestrator`.

### 5.2 If Option B is Approved:
1. A new model (e.g. `HandoffPayload`) must be created in a new module (e.g. `src/biorch/orchestration/join_gate.py`), packaging `Workflow`, `WorkflowResult`, `synthesis_eligible: bool`, and worker `artifacts`.
2. `src/biorch/orchestration/result.py` (`WorkflowResult`) remains completely untouched.
3. `contracts/synthesis/SYNTHESIS_CONTRACT.md` Section 3 and Section 14.1 must be formally rewritten to declare `HandoffPayload` as the required input, replacing the current mandate to consume `WorkflowResult` exclusively.
4. `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md` Section 25.4 must specify that the Join Gate emits `HandoffPayload`.
5. `src/biorch/orchestration/orchestrator.py` must expose or preserve `Result.artifacts` so the Join Gate component can collect them.
6. A new schema (`schemas/synthesis_input.schema.json`) is likely required to formally validate the composite handoff payload.
7. Phase 08.4F Join Gate must be implemented as a distinct component that consumes `Workflow` + `WorkflowResult` + `Result` collection and outputs `HandoffPayload`.

---

## 6. Evidence Gaps or Contradictions Discovered

- **Evidence Completeness:** No evidence gaps were found. The primary baseline artifact (`PHASE_08_4F_08_4G_ARCHITECTURAL_DECISION_SUPPORT.md`) comprehensively accounts for all 14 required handoff fields, all 6 failure/eligibility pathways, and all working-tree data loss points.
- **Working Tree State:** The working-tree source files and contracts have not changed since the baseline investigation was generated.
- **Sufficiency:** The existing repository evidence and compiled artifacts are entirely sufficient for human decision-making. No further exploratory investigation is required prior to human architectural selection.

---

## 7. Confirmation of Status

- **NO Architectural Option Selected:** Confirmed. Neither Option A nor Option B has been selected, endorsed, or prioritized.
- **NO Implementation Performed:** Confirmed. No production code, contracts, schemas, tests, or governance files were created or modified.

*This addendum concludes the read-only decision-support phase. Next steps require a human architectural decision to choose Option A or Option B.*
