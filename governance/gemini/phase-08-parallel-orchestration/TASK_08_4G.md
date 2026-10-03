# Task: Phase 08.4G — Result Synthesis

## 1. Task Identity

- Phase: 08 — Parallel Orchestration
- Sub-phase: 08.4G — Result Synthesis
- Task ID: BIORCH-08.4G
- Contract: BIORCH-SYNTH-001
- Status: PENDING IMPLEMENTATION

---

## 2. Objective

Implement the Phase 08.4G Result Synthesis boundary defined by the existing BIOrch synthesis contract.

The implementation MUST transform the validated handoff produced by the Phase 08.4F Join Gate into the governed `SynthesisResult` representation defined by the repository's existing synthesis contract and schema.

The implementation MUST remain deterministic, contract-driven, and framework-neutral.

---

## 3. Governing Principle

Phase 08.4G is a deterministic synthesis/aggregation boundary.

It is NOT an AI reasoning, summarization, prioritization, or semantic interpretation layer.

The implementation MUST NOT invent meaning that is not present in the incoming validated results.

The implementation MUST preserve the information and attribution supplied by the completed orchestration stages.

---

## 4. Required Pre-Implementation Investigation

Before modifying production code, inspect and use as authoritative:

### Existing governance

- `governance/gemini/phase-08-parallel-orchestration/TASK.md`
- `governance/gemini/phase-08-parallel-orchestration/TASK_08_4E.md`
- `governance/gemini/phase-08-parallel-orchestration/TASK_08_4F.md`
- `governance/gemini/phase-08-parallel-orchestration/PHASE_CLOSURE_08_4F.md`
- Relevant Phase 08 response/review/closure artifacts

### Existing contracts

- `contracts/synthesis/SYNTHESIS_CONTRACT.md`
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`
- Any directly referenced Phase 08 contracts

### Existing schemas

- `schemas/synthesis_result.schema.json`
- `schemas/result.schema.json`
- Any directly referenced schemas

### Existing implementation

Inspect the current orchestration implementation and specifically determine:

- how Phase 08.4F produces the Join Gate handoff
- the exact `HandoffPayload` structure
- the exact `WorkflowResult` structure
- how workflow/task declaration order is represented
- how worker terminal states are represented
- how provenance is represented
- the current integration point in `orchestrator.py`
- whether a synthesis module already exists
- the existing package/export conventions
- existing test organization and test patterns

Do NOT assume a new module, export, or test filename is required until the repository structure confirms it.

---

## 5. Input Boundary

The synthesis implementation MUST consume the validated output of Phase 08.4F.

The exact input structure MUST be taken from the existing implementation and contract rather than recreated from assumptions.

Where the existing contract identifies the input as a `HandoffPayload`, preserve that terminology.

The synthesis layer MUST NOT bypass the Join Gate or independently reconstruct Join Gate validation.

---

## 6. Output Boundary

The synthesis implementation MUST produce the repository-defined `SynthesisResult`.

The output MUST conform strictly to:

`schemas/synthesis_result.schema.json`

The implementation MUST preserve the schema's actual required fields, types, enums, nesting, and constraints.

Do not add new fields or entities unless explicitly required by the existing contract/schema.

---

## 7. Deterministic Ordering

Result synthesis MUST be deterministic.

Where the contract defines declared workflow/task order, that order MUST be used for synthesized findings and task attribution.

The implementation MUST NOT order results according to:

- worker completion order
- thread scheduling
- asynchronous arrival order
- execution duration
- timestamps
- worker identity
- dictionary/set incidental ordering

Repeated synthesis with semantically identical inputs MUST produce the same governed output.

Do not introduce a new ordering policy if an authoritative ordering policy already exists in the Phase 08 contracts or implementation. Use the existing policy.

---

## 8. Task Attribution

Every synthesized task result MUST retain the task attribution required by the existing synthesis contract/schema.

At minimum, preserve the source task identity and associated worker/agent identity wherever those fields are defined by the contract.

The implementation MUST NOT:

- merge unrelated task results
- invent task identities
- lose task attribution
- silently discard terminal task states
- rewrite specialist findings into new semantic interpretations

---

## 9. Terminal-State Handling

The implementation MUST explicitly handle the terminal states defined by the existing orchestration contracts.

Known states include, where supported by the repository contract:

- `SUCCESS`
- `FAILED`
- `TIMEOUT`
- `NOT_EXECUTED`

The exact mapping from workflow/task state to synthesis status MUST be derived from:

- `BIORCH-SYNTH-001`
- `BIORCH-ORCH-001`
- the existing Phase 08 implementation

Do not invent additional state mappings.

Failed, timed-out, and unexecuted tasks MUST remain visible where required by the contract.

They MUST NOT be silently converted into successful results.

---

## 10. Synthesis Eligibility

The implementation MUST honor the existing `synthesis_eligible` decision supplied by the Join Gate.

If the contract defines `synthesis_eligible == false` as a fail-closed condition, synthesis MUST terminate according to that contract and MUST NOT emit synthesized findings that the contract prohibits.

The synthesis implementation MUST NOT override or reinterpret Join Gate eligibility.

---

## 11. Findings Handling

Synthesis MUST preserve findings according to the existing synthesis contract.

Unless the authoritative contract explicitly requires otherwise, the implementation MUST NOT:

- deduplicate findings
- summarize findings
- rewrite findings
- infer additional findings
- prioritize findings
- score findings
- classify findings by severity
- semantically reinterpret specialist output
- merge findings solely because they appear similar

The synthesis layer is an aggregation boundary, not a reasoning engine.

---

## 12. Provenance

The implementation MUST preserve incoming provenance information according to the existing synthesis contract.

If `BIORCH-SYNTH-001` explicitly requires synthesis metadata to be added, implement exactly those fields and values defined by the contract.

Do not invent additional provenance fields.

The implementation MUST NOT discard upstream provenance.

---

## 13. Schema Validation

The resulting `SynthesisResult` MUST validate against:

`schemas/synthesis_result.schema.json`

Schema validation MUST be demonstrated through tests.

Any validation failure MUST be surfaced deterministically and must not be silently converted into a successful synthesis result.

---

## 14. Integration Scope

Integrate synthesis into the existing orchestration flow only at the integration point defined by the current Phase 08 architecture.

Before changing `orchestrator.py`, establish from the existing code:

1. where the Phase 08.4F Join Gate completes,
2. what object it returns,
3. where downstream orchestration expects the synthesized result,
4. whether an existing abstraction already exists for this boundary.

Do not restructure the orchestration architecture merely to introduce synthesis.

Do not introduce a new framework or orchestration dependency.

Only modify package exports such as `__init__.py` if the repository's existing package conventions and actual import requirements demonstrate that they are necessary.

---

## 15. Non-Goals

Phase 08.4G MUST NOT implement:

- autonomous planning
- probabilistic reasoning
- LLM-based synthesis
- semantic summarization
- finding deduplication
- finding prioritization
- finding scoring
- domain-specific BI interpretation
- Tableau-specific synthesis logic
- Power BI-specific synthesis logic
- direct tool execution
- worker/subagent execution
- new workflow scheduling
- new parallel execution mechanisms
- CrewAI integration
- LangGraph integration
- external orchestration framework integration
- new entity types not defined by the existing contracts/schema

---

## 16. Production-Code Scope

Production modifications MUST remain limited to files demonstrably required by the existing architecture to implement Phase 08.4G.

The likely integration area is:

`src/biorch/orchestration/`

However, the exact files MUST be established through repository inspection before implementation.

Do not modify unrelated Phase 08, Phase 07, Tableau, Power BI, governance, or framework code.

---

## 17. Test Requirements

Add or update tests following the repository's existing testing conventions.

Tests MUST cover the behavior actually required by the authoritative contracts, including where applicable:

1. successful synthesis
2. deterministic declared workflow ordering
3. preservation of task attribution
4. synthesis eligibility handling
5. failed task handling
6. timeout handling
7. not-executed task handling
8. workflow-level status mapping
9. provenance preservation
10. schema conformance
11. repeated execution determinism
12. integration with the existing orchestration boundary

Do not create tests for behavior that is not supported by the authoritative contract.

Existing tests MUST continue to pass.

---

## 18. Regression Requirements

The implementation MUST NOT regress the completed Phase 08.4A–08.4F behavior.

In particular, verify that:

- existing schema behavior remains intact
- existing worker invocation behavior remains intact
- existing parallel dispatch behavior remains intact
- existing join/reconciliation behavior remains intact
- existing Join Gate behavior remains intact
- existing orchestrator behavior remains intact except for the intended 08.4G integration

---

## 19. Validation Requirements

Before declaring implementation complete:

1. Run the focused Phase 08.4G tests.
2. Run the relevant existing orchestration tests.
3. Run the full test suite.
4. Confirm schema validation succeeds.
5. Confirm deterministic behavior.
6. Confirm no unintended production files changed.
7. Confirm no governance/phase state is advanced prematurely.

Report exact commands and results.

---

## 20. Acceptance Criteria

Phase 08.4G is acceptable only when all applicable criteria below are demonstrated:

- [ ] Implementation conforms to `BIORCH-SYNTH-001`.
- [ ] Input is obtained from the validated Phase 08.4F boundary.
- [ ] Output conforms to `schemas/synthesis_result.schema.json`.
- [ ] Declared workflow ordering is preserved.
- [ ] Task attribution is preserved.
- [ ] Required terminal task states remain explicitly represented.
- [ ] Join Gate synthesis eligibility is honored.
- [ ] Required provenance is preserved.
- [ ] No unauthorized semantic reinterpretation occurs.
- [ ] No deduplication/prioritization/scoring is introduced.
- [ ] Repeated identical inputs produce deterministic results.
- [ ] Existing Phase 08.4A–08.4F behavior remains passing.
- [ ] Full test suite passes with zero unexplained regressions.
- [ ] Production changes remain within the demonstrated implementation scope.
- [ ] No unrelated governance or phase-state files are modified.

---

## 21. Required Implementation Evidence

The implementation response MUST provide:

1. Files inspected before implementation.
2. Production files modified.
3. Test files modified/created.
4. Exact implementation behavior.
5. Contract/schema validation evidence.
6. Determinism test evidence.
7. Relevant Phase 08 regression test evidence.
8. Full test-suite result.
9. `git diff --stat`.
10. `git status --short`.
11. Any unresolved issues or deviations.

---

## 22. Governance Restrictions

During this task:

- Do NOT advance Phase 08 state.
- Do NOT create Phase 08.4H artifacts.
- Do NOT modify Phase 08 closure records for 08.4G before implementation evidence exists.
- Do NOT modify unrelated governance records.
- Do NOT rewrite completed 08.4A–08.4F closure artifacts.
- Do NOT manufacture missing requirements.
- Do NOT silently resolve ambiguities by assumption.
- If the implementation discovers a contract inconsistency or missing requirement, STOP and report it rather than inventing a solution.

---

## 23. Completion Definition

Phase 08.4G implementation is complete only when the implementation, tests, schema validation, deterministic behavior, and regression evidence satisfy the acceptance criteria above.

Completion of this task does NOT authorize Phase 08.4H.

Phase 08.4H remains a separate governed task.