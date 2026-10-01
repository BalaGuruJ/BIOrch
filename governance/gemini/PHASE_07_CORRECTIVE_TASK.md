# Phase 07 — SourceEvidence Architectural Reconciliation (Corrective Task)

**Phase:** Phase 07 — PBIParser Integration
**Task Type:** Implementation / Reconciliation
**Status:** DRAFT

## 1. Objective
Reconcile the architectural conflict regarding `SourceEvidence` definitions between `src/biorch/integrations/powerbi/canonical_entities.py` and `src/biorch/integrations/powerbi/entities.py`. Establish a single, contract-compliant definition and harmonize usage across the Phase 07 pipeline.

## 2. Constraints & Boundaries
- **Strictly Bounded:** Reconciliation is limited to `SourceEvidence`.
- **No Expansion:** Do not re-validate or re-implement Semantic Lineage or already-validated components unless evidence reveals a direct defect caused by the current `SourceEvidence` conflict.
- **No Closure:** This task does not close Phase 07.
- **Preservation:** Maintain the 87-test baseline and current runtime verification status.

## 3. Scope of Work
1. **Validation:** Analyze `CONTRACT.md` Section 20 regarding provenance requirements.
2. **Reconciliation:**
   - Determine the canonical definition of `SourceEvidence` that satisfies contract requirements for provenance.
   - Update `canonical_entities.py` and `entities.py` to harmonize the definition.
   - Update all consumers in `src/biorch/integrations/powerbi/` (including `canonicalizer.py`) to align with the canonical definition.
3. **Verification:**
   - Execute the target runtime path using the provisioned .NET 8 / CoreCLR environment as specified in `docs/phase-07-runtime-reproduction.md`.
   - Ensure existing tests pass (`tests/test_powerbi_...`, etc.).
   - Demonstrate the pipeline remains green in the real runtime environment.
4. **Documentation:**
   - Update Phase 07 governance evidence to reflect the resolved conflict.
   - Record exact environment prerequisites used for verification.

## 4. Acceptance Criteria
1. Single authoritative definition of `SourceEvidence` is established.
2. All Phase 07 pipeline components are functionally consistent with the new definition.
3. Contract-compliant provenance is propagated.
4. Existing repository test baseline (87 tests) remains green.
5. Runtime verification (Power BI integration) succeeds in the provisioned environment.
