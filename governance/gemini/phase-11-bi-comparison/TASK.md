# Phase 11 — BI Comparison

## Objective

Implement the governed Phase 11 structural comparison capability for Tableau and Power BI.

The implementation MUST consume the existing canonical Tableau and Power BI metadata artifacts and produce a deterministic machine-readable comparison report.

Phase 11 is a structural comparison capability.

It MUST NOT attempt semantic equivalence, business-rule inference, fuzzy matching, or cross-platform expression translation.

---

## Prerequisites

The following MUST already be complete:

- Phase 11 BI Comparison investigation.
- Phase 10 LLM-Based Planning closure.
- Existing Tableau canonical metadata pipeline.
- Existing Power BI canonical metadata pipeline.
- Approved `BIORCH-COMPARISON-001` contract.

---

## Important Sample Constraint

The existing demonstration inputs are intentionally different BI datasets:

- Tableau: Superstore sample workbook.
- Power BI: AdventureWorks Sales sample.

These datasets are NOT expected to be semantically equivalent.

Phase 11 success MUST therefore be measured by correct structural classification rather than by achieving a high number of matches.

The comparison engine MUST be capable of reporting legitimate unmatched structures.

---

## Scope

### In Scope

1. Implement the deterministic comparison component.
2. Implement comparison key generation.
3. Compare Tables.
4. Compare Columns.
5. Compare Relationships.
6. Classify comparison results as:
   - `MATCHED`
   - `TABLEAU_ONLY`
   - `POWERBI_ONLY`
   - `DIFFERENT`
7. Segregate platform-specific non-comparable entities.
8. Generate the governed comparison report.
9. Create the finalized `schemas/comparison_report.schema.json`.
10. Validate comparison inputs against existing canonical schemas.
11. Validate comparison output against the new comparison schema.
12. Add automated unit/integration tests.
13. Execute a real Phase 11 comparison using the existing Tableau and Power BI samples.

---

## Explicitly Out of Scope

DO NOT implement:

- semantic equivalence
- fuzzy matching
- AI-based matching
- synonym matching
- business-domain inference
- DAX translation
- Tableau calculated-field translation
- DAX vs Tableau calculation comparison
- worksheet comparison
- dashboard comparison
- visual comparison
- data-value comparison
- data-quality comparison
- Excel generation
- end-user presentation formatting
- modification of Tableau agent contracts
- modification of Power BI agent contracts
- modification of existing canonical entity models

---

## Comparison Rules

### Tables

Compare tables using deterministic normalized comparison keys.

Report:

- matched tables
- Tableau-only tables
- Power BI-only tables

A table-name match MUST NOT be described as semantic equivalence.

### Columns

Compare columns using:

- parent table comparison key
- column comparison key

A column MUST NOT match solely because the column name is identical under different unmatched tables.

### Relationships

Compare relationships using deterministic structural keys derived from:

- source table
- source column
- target table
- target column

Relationship direction MUST be preserved.

Platform-specific relationship IDs MUST NOT be used as comparison keys.

---

## Non-Comparable Structures

The implementation MUST NOT compare:

### Tableau

- calculated-field expressions
- worksheets
- dashboards
- visual/layout constructs

### Power BI

- DAX expressions
- M expressions
- measures
- calculation groups
- calculation items
- partitions
- visual/report layout constructs

Non-comparable structures MUST NOT affect comparable-entity results.

---

## Determinism Requirements

For identical canonical inputs:

- comparison keys MUST be identical
- comparison classifications MUST be identical
- detailed result ordering MUST be identical
- aggregate counts MUST be identical

Ordering MUST be deterministic.

Runtime timestamps and generated report IDs MUST NOT affect structural comparison content.

---

## Schema Requirements

The existing provisional comparison schema MUST NOT be treated as final.

The implementation MUST create the finalized:

`schemas/comparison_report.schema.json`

The finalized schema MUST:

- explicitly define the comparison artifact
- define required fields
- define comparison states
- define table comparison results
- define column comparison results
- define relationship comparison results
- define summary counts
- define provenance fields
- reject structurally invalid reports

Core comparison structures MUST NOT use unrestricted:

`"additionalProperties": true`

---

## Required Tests

Tests MUST cover at minimum:

1. Matching tables.
2. Tableau-only tables.
3. Power BI-only tables.
4. Matching columns.
5. Columns under unmatched tables.
6. Matching relationships.
7. Different relationships.
8. Deterministic ordering.
9. Non-comparable entity segregation.
10. Invalid canonical input.
11. Valid comparison report.
12. Invalid comparison report.
13. Repeated comparison producing identical structural output.
14. Existing Tableau + Power BI sample execution.

The tests MUST NOT assume that the Superstore and AdventureWorks samples are semantically equivalent.

---

## Required Runtime Demonstration

The implementation MUST perform one real comparison using:

### Tableau

The existing Superstore canonical metadata artifact produced by the Tableau pipeline.

### Power BI

The existing AdventureWorks Sales canonical metadata artifact produced by the Power BI pipeline.

The demonstration MUST produce a comparison report containing:

- source artifact references
- table comparison results
- column comparison results
- relationship comparison results
- non-comparable entity segregation where applicable
- deterministic summary counts

The demonstration MUST successfully validate the generated report against the comparison schema.

---

## Files / Areas Expected to Change

Expected implementation areas include only those required for:

- comparison contract consumption
- comparison logic
- comparison orchestration/wiring
- comparison schema
- comparison tests

The implementation MUST NOT modify existing Tableau or Power BI agent contracts or canonical models.

The implementation agent MUST report the exact files modified before completion.

---

## Acceptance Criteria

Phase 11 implementation is accepted only if:

1. `BIORCH-COMPARISON-001` is implemented as specified.
2. The finalized comparison schema exists.
3. The comparison component is implemented.
4. Tableau canonical metadata can be consumed.
5. Power BI canonical metadata can be consumed.
6. Tables are deterministically compared.
7. Columns are deterministically compared.
8. Relationships are deterministically compared.
9. Comparison states are correctly classified.
10. Non-comparable platform-specific structures remain isolated.
11. Provenance does not participate in comparison keys.
12. Identical inputs produce identical structural comparison results.
13. Required automated tests pass.
14. The full existing test suite passes.
15. A real comparison run succeeds against Superstore + AdventureWorks.
16. The generated comparison report passes JSON-schema validation.
17. No Tableau or Power BI agent contract was modified.
18. No semantic equivalence is claimed between the two sample workbooks.
19. No Phase 12 functionality is implemented.

---

## Execution Restrictions

DO NOT:

- modify existing agent contracts
- modify canonical entity definitions
- modify Phase 10 closure records
- modify governance closure records
- implement Phase 12
- implement Excel/report presentation
- introduce semantic or fuzzy matching
- introduce AI-based comparison
- execute DAX, M, or Tableau expressions
- silently broaden the comparison scope

If an architectural limitation or required change outside this task is discovered, STOP and report it rather than expanding scope.

---

## Expected Response Format

At completion, report:

1. Files created.
2. Files modified.
3. Files deleted.
4. Comparison architecture implemented.
5. Exact comparison rules implemented.
6. Exact schema implemented.
7. Tests executed and exact results.
8. Full-suite test result.
9. Real Superstore + AdventureWorks comparison result.
10. Generated comparison artifact location.
11. Schema validation result.
12. Confirmation that existing Tableau/Power BI contracts were not modified.
13. Confirmation that no semantic comparison was implemented.
14. Any deviations from this task.
15. Any remaining limitations.

---

## Completion State

Phase 11 remains open until the implementation, automated tests, full regression suite, and real runtime comparison have all passed.

No Phase 12 work may begin until Phase 11 is explicitly reviewed and closed.