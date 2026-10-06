# Phase 11 — BI Comparison Task

## Objective

Implement the governed Phase 11 structural comparison capability for Tableau and Power BI.

The implementation MUST consume the existing canonical Tableau and Power BI metadata artifacts and produce the governed, deterministic comparison artifact defined by `contracts/comparison/COMPARISON_CONTRACT.md`.

The approved Comparison Contract and frozen Tableau Logical Relationship architecture are authoritative. Do not reinterpret or extend them.

---

## 1. Scope

### In Scope

1. Deterministic comparison of:

   * Tables
   * Columns
   * Relationships
2. Comparison result states:

   * `MATCHED`
   * `TABLEAU_ONLY`
   * `POWERBI_ONLY`
   * `DIFFERENT`
3. Deterministic comparison-key generation and normalization.
4. Deterministic result ordering.
5. Input validation against existing Tableau and Power BI canonical schemas.
6. Governed comparison-artifact generation.
7. Output validation against `schemas/comparison_report.schema.json`.
8. Automated unit/integration tests.
9. Real execution using the existing Tableau Superstore and Power BI AdventureWorks canonical artifacts.
10. Runtime/orchestration wiring required for the existing BIOrch execution path, if required by the current repository architecture.

### Explicitly Out of Scope

* Semantic equivalence or business-domain inference.
* Fuzzy, probabilistic, embedding-based, or AI-based matching.
* DAX, M, or Tableau expression translation, execution, or AST parsing.
* Worksheet, dashboard, visual, layout, or presentation comparison.
* Excel or Phase 12 functionality.
* Modification of existing Tableau/Power BI agent contracts.
* Modification of existing canonical entity models.
* Modification of frozen Tableau Logical Relationship architecture.

---

## 2. Relationship Rules

### Tableau

Tableau logical relationships MUST:

* Be compared at the non-directional Table-Pair grain.
* Use the governed commutative canonical Table-Pair identity.
* Remain binary and non-directional.
* Preserve `expression_raw` as an opaque immutable payload.
* NOT parse, evaluate, interpret, or decompose `expression_raw`.
* NOT synthesize source/target column endpoints.
* Treat column-pair interpretation as `OPAQUE_EXPRESSION_EVALUATION_DEFERRED`.

The implementation MUST NOT attempt to make Tableau relationship representation conform to Power BI column-level relationship representation.

### Power BI

Power BI relationships MAY use the native column-level relationship detail available in the canonical metadata.

Power BI-specific relationship directionality or other structural properties MUST be preserved only where defined by the approved comparison contract.

Power BI relationship handling MUST NOT impose column-level requirements on Tableau.

---

## 3. Structural Comparison Rules

1. Structural key equality means structural correspondence only.
2. Matching MUST use deterministic normalized comparison keys.
3. Source-system IDs, runtime IDs, provenance IDs, memory addresses, or timestamps MUST NOT determine structural identity.
4. Original source names MUST remain available for reporting.
5. Platform-specific/non-comparable entities MUST remain segregated.
6. The implementation MUST NOT invent additional comparison result states.
7. The implementation MUST NOT silently reinterpret malformed or incomplete canonical metadata.

---

## 4. Determinism

For identical canonical inputs:

* Comparison keys MUST be identical.
* Result classifications MUST be identical.
* Result ordering MUST be identical.
* Structural comparison content MUST be identical.

Generated timestamps and report IDs MAY differ, but MUST NOT affect structural comparison content.

Determinism MUST be demonstrated by repeated execution using identical inputs.

---

## 5. Required Validation & Tests

Tests MUST cover, at minimum:

1. Matching tables.
2. Tableau-only tables.
3. Power BI-only tables.
4. Matching columns under matching tables.
5. Columns under unmatched tables.
6. Matching relationships.
7. Different relationships.
8. Tableau Table-Pair commutative identity.
9. Tableau relationship non-directionality.
10. Tableau `expression_raw` remaining opaque and unparsed.
11. Tableau column-pair interpretation remaining deferred.
12. Power BI native relationship detail handling.
13. Deterministic ordering.
14. Repeated execution producing identical structural comparison content.
15. Non-comparable entity segregation.
16. Invalid input rejection.
17. Valid comparison-artifact schema validation.

The full existing regression suite MUST also pass.

---

## 6. Real Runtime Validation

Execute the completed Phase 11 comparison against:

* Tableau: existing Superstore canonical artifact.
* Power BI: existing AdventureWorks canonical artifact.

The samples are intentionally different BI datasets.

A low number of matches, including zero matches for an entity class, MUST NOT be treated as failure by itself. Correct deterministic classification is the criterion.

The runtime execution MUST demonstrate that the actual BIOrch comparison path can consume the canonical artifacts and produce the governed comparison artifact.

---

## 7. Implementation Constraints

Before implementation, inspect the current repository only as necessary to identify the existing comparison component, orchestration path, canonical artifact interfaces, schema location, and test conventions.

Do NOT redesign existing architecture merely to accommodate Phase 11.

If an existing component/path already satisfies a requirement, reuse it rather than creating a competing implementation.

If the repository contradicts an explicit requirement of the approved contract or frozen architecture:

1. STOP the affected implementation.
2. Report the exact contradiction and affected files.
3. Do NOT modify the contract, architecture, or agent contracts to resolve it.
4. Do NOT invent a workaround that changes the governed behavior.

---

## 8. Protected Artifacts

The following MUST NOT be modified as part of Phase 11 implementation:

* `contracts/comparison/COMPARISON_CONTRACT.md`
* `docs/architecture/BIORCH-ARCH-TABLEAU-LOGICAL-RELATIONSHIPS-001.md`
* Existing Tableau agent contracts.
* Existing Power BI agent contracts.
* Existing canonical entity models.

Any required change to these artifacts is outside this task and MUST be reported rather than implemented.

---

## 9. Acceptance Criteria

Phase 11 is complete only when all are true:

1. Implementation conforms to the approved `COMPARISON_CONTRACT.md`.
2. Tables, columns, and relationships are structurally compared.
3. Tableau relationships use the governed non-directional Table-Pair grain.
4. Tableau `expression_raw` remains opaque and is never parsed or evaluated.
5. Power BI native relationship detail is handled according to the contract.
6. Only governed result states are produced.
7. Platform-specific/non-comparable entities remain segregated.
8. Input validation succeeds for valid canonical artifacts and rejects invalid input.
9. Output passes `schemas/comparison_report.schema.json` validation.
10. Repeated identical-input executions produce identical structural comparison content.
11. Required automated tests pass.
12. Full regression suite passes.
13. Real Superstore + AdventureWorks comparison succeeds.
14. Existing agent contracts and canonical models remain unchanged.
15. No semantic, fuzzy, AI-based, or expression-based inference is introduced.
16. No Phase 12 or presentation functionality is implemented.

---

## 10. Required Completion Report

At completion, report:

1. Files created.
2. Files modified.
3. Files deleted, if any.
4. Implementation summary.
5. Comparison rules implemented.
6. Contract/architecture alignment confirmation.
7. Automated test results.
8. Full regression results.
9. Determinism/repeated-run evidence.
10. Schema validation evidence.
11. Superstore + AdventureWorks runtime comparison summary.
12. Confirmation that protected contracts/models were not modified.
13. Any limitations or unresolved issues.
14. Any deviation from this task, with explicit justification.

Do not claim Phase 11 completion if any acceptance criterion remains unmet.
