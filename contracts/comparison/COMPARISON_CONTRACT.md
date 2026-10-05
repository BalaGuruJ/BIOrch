# Phase 11 — BI Comparison Contract

**Contract ID:** BIORCH-COMPARISON-001

**Contract Name:** BI Comparison Artifact Contract

**Phase:** Phase 11 — BI Comparison

**Status:** DRAFT

---

## 1. Purpose

This contract defines the governed, deterministic artifact produced by Phase 11 when comparing the canonical metadata outputs of:

- Tableau
- Power BI

The purpose of Phase 11 is **structural cross-platform comparison**.

The comparison MUST NOT attempt to determine that Tableau and Power BI are semantically equivalent BI implementations.

The comparison engine MUST treat the two BI systems as independent source analyses and compare only explicitly approved structural entities.

---

## 2. Architectural Principle

Phase 11 operates downstream of the existing Tableau and Power BI metadata extraction pipelines.

The comparison layer MUST consume the existing canonical metadata artifacts rather than directly parsing:

- `.twb` files
- Power BI TMDL files
- DAX expressions
- M expressions
- Tableau calculated-field expressions
- visual definitions

The existing Tableau and Power BI agent contracts and canonical models remain authoritative.

Phase 11 MUST NOT modify those existing contracts or canonical models.

---

## 3. Comparable Entities

Only the following entity classes are comparable in Phase 11:

1. Tables
2. Columns
3. Relationships

No additional entity class may be introduced into the comparison result without an explicit contract revision.

### 3.1 Tables

Tables are compared using their canonical table identity/name within each source artifact.

The comparison MUST report:

- entities present in both artifacts
- entities present only in Tableau
- entities present only in Power BI

A table name match means only that the normalized comparison key is equal.

It MUST NOT be interpreted as proof of semantic equivalence.

### 3.2 Columns

Columns are compared using:

- normalized parent table comparison key
- normalized column name comparison key

A column match therefore requires both its parent table comparison key and column comparison key to match.

Column matching MUST NOT rely on:

- lineage tags
- source-system identifiers
- memory addresses
- generated runtime IDs
- provenance identifiers

### 3.3 Relationships

Relationships are compared using a deterministic structural relationship key derived from the participating table and column comparison keys.

Relationship comparison MUST consider at minimum:

- source table
- source column
- target table
- target column

Relationship identity MUST NOT depend on platform-specific relationship IDs or provenance identifiers.

Relationship directionality MUST be preserved in the comparison representation.

---

## 4. Matching Semantics

Phase 11 performs **structural key matching only**.

The following rule applies:

> Equal comparison keys indicate structural correspondence, not semantic equivalence.

The comparison engine MUST NOT infer:

- business meaning
- data equivalence
- metric equivalence
- calculation equivalence
- source-system equivalence
- data-quality equivalence
- analytical equivalence

For example, a Tableau table named `Sales` and a Power BI table named `Sales` may be reported as structurally matched, but Phase 11 MUST NOT claim that the two tables contain equivalent data.

---

## 5. Normalization Rules

Comparison keys MUST be deterministic.

At minimum:

- entity names MUST be treated consistently across both platforms
- surrounding whitespace MUST NOT create different comparison keys
- comparison key generation MUST be documented and implemented consistently
- original source names MUST remain available for reporting

Case sensitivity MUST be explicitly defined by the implementation and MUST be identical for both platforms.

The implementation MUST NOT perform aggressive transformations such as:

- synonym replacement
- stemming
- fuzzy matching
- semantic similarity
- AI-generated equivalence
- business-term inference

unless this contract is explicitly revised in a future phase.

---

## 6. Comparison Result Categories

Each comparable entity MUST resolve into one of the following structural states:

- `MATCHED`
- `TABLEAU_ONLY`
- `POWERBI_ONLY`
- `DIFFERENT`

`MATCHED` means the entity comparison keys correspond.

`TABLEAU_ONLY` means the entity exists in the Tableau artifact but not in the Power BI artifact.

`POWERBI_ONLY` means the entity exists in the Power BI artifact but not in the Tableau artifact.

`DIFFERENT` is reserved for entities that correspond at the comparison level but have explicitly reportable structural differences.

The implementation MUST NOT invent additional result categories without contract revision.

---

## 7. Non-Comparable Entities

The following are explicitly outside structural comparison:

### Power BI

- DAX expressions
- M expressions
- Measures
- Calculation groups
- Calculation items
- Partitions
- Power BI-specific hierarchy constructs
- Power BI visual/report layout constructs

### Tableau

- Tableau calculated-field expressions
- Worksheets
- Dashboards
- Marks/layout configuration
- Tableau-specific visual constructs

### Cross-platform

Any platform-specific construct without a meaningful structural counterpart is non-comparable.

Non-comparable entities MUST NOT affect the comparable-entity match/difference calculations.

Where included in the comparison artifact, non-comparable information MUST be clearly segregated by platform.

---

## 8. Provenance

The comparison artifact MUST identify the source Tableau and Power BI artifacts used to produce the report.

Provenance MAY contain:

- source artifact identifiers
- source artifact paths
- generation timestamp
- comparison report ID
- source metadata identifiers

Provenance information MUST NOT be used as a comparison key.

Runtime-specific values such as timestamps or generated report IDs MUST NOT influence the structural comparison result.

---

## 9. Comparison Artifact

A valid Phase 11 comparison artifact MUST contain:

### 9.1 Report Metadata

- unique report identifier
- generation timestamp
- Tableau source artifact reference
- Power BI source artifact reference

### 9.2 Comparable Entity Results

Separate deterministic result collections for:

- tables
- columns
- relationships

Each result MUST identify its comparison state.

### 9.3 Non-Comparable Information

Platform-specific non-comparable entities MAY be reported, but MUST be separated into:

- Tableau
- Power BI

### 9.4 Summary

The report MUST contain deterministic aggregate counts for:

- matched entities
- different entities
- Tableau-only entities
- Power BI-only entities

Counts MUST be derivable from the detailed comparison results.

---

## 10. Determinism

For identical source artifacts, Phase 11 MUST produce the same structural comparison result across repeated executions.

Ordering MUST be deterministic.

At minimum:

- tables sorted by comparison key
- columns sorted by parent table comparison key and column comparison key
- relationships sorted by deterministic relationship key
- non-comparable entities sorted deterministically by platform and identifier

Generated timestamps and report IDs MAY differ between executions but MUST NOT affect comparison content.

---

## 11. Input Validation

The comparison layer MUST validate both input artifacts before comparison.

Inputs MUST conform to their existing governed schemas:

- Tableau canonical metadata schema
- Power BI canonical metadata schema

Invalid input MUST prevent comparison execution.

Phase 11 MUST NOT silently reinterpret malformed or incomplete canonical metadata.

---

## 12. Output Validation

The generated comparison artifact MUST conform to the governed:

`schemas/comparison_report.schema.json`

The schema MUST explicitly define the comparison artifact structure.

The schema MUST NOT use unrestricted `additionalProperties: true` for the core comparison structures.

The schema MUST enforce required fields and allowed comparison states.

---

## 13. Implementation Boundary

### In Scope

Phase 11 implementation includes:

1. ComparisonAgent or equivalent deterministic comparison component.
2. Comparison orchestration/wiring required to execute the comparison.
3. Comparison key generation.
4. Table comparison.
5. Column comparison.
6. Relationship comparison.
7. Non-comparable entity segregation.
8. Deterministic comparison report generation.
9. Comparison report JSON schema.
10. Automated tests.
11. Execution against the existing Tableau and Power BI canonical artifacts.

### Out of Scope

Phase 11 MUST NOT implement:

- semantic matching
- fuzzy matching
- AI-based entity matching
- DAX translation
- Tableau calculation translation
- DAX vs Tableau calculation comparison
- worksheet/visual comparison
- dashboard layout comparison
- business-rule inference
- data-value comparison
- data-quality comparison
- modification of Tableau agent contracts
- modification of Power BI agent contracts
- modification of existing canonical entity models
- Excel/export/report presentation logic

---

## 14. Required Test Coverage

Tests MUST cover at minimum:

1. Matching tables.
2. Tableau-only tables.
3. Power BI-only tables.
4. Matching columns under matching tables.
5. Columns under unmatched tables.
6. Matching relationships.
7. Different relationships.
8. Deterministic ordering.
9. Non-comparable entities remaining segregated.
10. Invalid input rejection.
11. Valid comparison artifact schema validation.
12. Repeated execution producing identical structural comparison content.

Tests MUST NOT depend on semantic equivalence between the existing Tableau and Power BI sample workbooks.

The existing samples are intentionally different BI datasets.

---

## 15. Existing Sample Constraint

The Phase 11 demonstration MUST use the existing Tableau and Power BI sample artifacts.

The samples are intentionally different:

- Tableau: Superstore sample workbook
- Power BI: AdventureWorks Sales sample

Therefore, the demonstration MUST be designed to prove that the comparison engine correctly reports structural matches and differences between independently modeled BI artifacts.

The demonstration MUST NOT require the two workbooks to represent the same business domain.

A low number of structural matches, or even zero matches for some entity classes, MUST NOT be considered a failure by itself.

Correct classification is the success criterion.

---

## 16. Relationship to Phase 12

Phase 11 produces the governed machine-readable comparison artifact.

Phase 12 consumes this artifact for analysis-ready/user-consumable output.

Phase 11 MUST NOT implement Excel generation, presentation formatting, or end-user reporting.

---

## 17. Architectural Restrictions

The implementation MUST:

- preserve existing BI agent boundaries
- preserve existing canonical metadata contracts
- remain deterministic
- keep platform-specific constructs isolated
- avoid executing DAX, M, or Tableau expressions
- avoid introducing semantic inference
- avoid modifying governance closure records

---

## 18. Acceptance Criteria

Phase 11 is complete only when all of the following are true:

1. The comparison contract is implemented.
2. The comparison JSON schema explicitly represents the governed artifact.
3. The ComparisonAgent/equivalent deterministic component is implemented.
4. Tableau and Power BI canonical artifacts are accepted as inputs.
5. Tables, columns, and relationships are structurally compared.
6. Comparison states are deterministic and correctly classified.
7. Platform-specific constructs remain non-comparable.
8. Provenance is preserved without affecting comparison keys.
9. Repeated comparison of identical inputs produces identical structural results.
10. Automated tests cover the required comparison cases.
11. The existing full test suite passes.
12. A real Phase 11 comparison run succeeds using the existing Tableau Superstore and Power BI AdventureWorks artifacts.
13. The resulting comparison artifact passes schema validation.
14. No existing Tableau or Power BI agent contract is modified.
15. No semantic equivalence is claimed between the two intentionally different sample workbooks.

---

## 19. Status

This contract remains `DRAFT` until reviewed and explicitly approved.

No Phase 11 implementation work may begin until the contract and implementation task are approved.