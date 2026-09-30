# PHASE_07_BASELINE_CAPABILITY_INVESTIGATION.md

## 1. Executive Summary
This report documents a read-only investigation of the existing Power BI parser baseline against the authoritative Phase 07 V1 contract. Due to environmental limitations, runtime execution of the baseline parser was not possible; therefore, all capability assessments are derived from a static analysis of the parser's source code and the `src/biorch/integrations/powerbi` implementation. The findings reveal that the parser provides basic support for tables, columns, and measures, but lacks robust support for advanced entities like hierarchies, calculation groups, and sophisticated relationship metadata required by the contract.

## 2. Baseline Parser Architecture
- **Adapter (`tmdl_parser_adapter.py`)**: Uses a third-party `tmdlparser` library. It iterates over a directory looking for `.tmdl` files and maps them to a simple canonical structure.
- **Mapping Strategy**: Direct mapping of TMDL `table`, `column`, `measure` definitions.
- **Metadata Handling**: Extracts `lineageTag`, `dataType`, `formatString`, `summarizeBy`, `sourceColumn`, `displayFolder`, `isHidden`.
- **Expression Handling**: Extracts `expression` for `CalculatedColumn` and `Measure`.

## 3. Actual Parser Execution Evidence
- **Status**: Execution attempted but failed due to missing `tmdlparser` dependency in the environment.
- **Evidence**: `ModuleNotFoundError: No module named 'tmdlparser'`.

## 4. Capability Matrix

| Capability | Present in Fixture | Parser Exposes It | Evidence | Notes |
|---|---|---|---|---|
| Table/Col/Measure | Yes | Yes | `tmdl_parser_adapter.py` | Full mapping logic exists |
| Relationships | Yes | No | `canonicalizer.py` (empty list) | Parser does not map these |
| Hierarchies | Yes | No | Static Analysis | Not in code |
| Partitions/M | Yes | No | Static Analysis | Not in code |
| Lineage | Yes | Partially | `lineageTag` | Partial mapping |

## 5. AdventureWorks Fixture Evidence (Static Analysis)
- The fixture (`examples/artifacts/powerbi/AdventureWorks Sales/`) contains `.tmdl` files (SemanticModel and Report). The parser is designed to iterate through `.tmdl` files in the directory.

## 6. Provenance Capability
- **Source File**: `Provenance(source_type='TMDL', file=source_file, range=None)`.
- **Range (Line/Col)**: NOT_SUPPORTED (Explicitly omitted in code).
- **Source Span**: NOT_SUPPORTED.

## 7. Identity Capability
- Uses `Identity.table_id()` and `Identity.column_id()` to generate stable IDs based on object names.

## 8. Expression Capability
- Measure DAX: Exposed as `expression` string.
- Calculated Column DAX: Exposed as `expression` string.
- M expressions: NOT_SUPPORTED (no mapping in adapter).

## 9. Unsupported Metadata
- Hierarchies, Partitions, M expressions, Calculation Groups are unsupported by the baseline parser code.

## 10. Existing Adapter Evidence
- `src/biorch/integrations/powerbi/adapter.py` forwards the model directly from the baseline parser without additional filtering or augmentation.

## 11. Existing Canonicalizer Evidence
- `src/biorch/integrations/powerbi/canonicalizer.py` consumes tables, columns, and measures but completely discards relationship and partition information.

## 12. Contract-Relevant Findings
- The current implementation is incomplete and fails to meet the contract requirements for relationships, hierarchies, and M expressions.

## 13. Open Questions
- What is the required environment setup to run the baseline parser successfully?
- Can the third-party `tmdlparser` library be updated or configured to expose missing metadata like relationships?

## 14. Explicit Non-Goals
- Any attempt at implementation changes, contract modifications, or architectural design decisions was strictly excluded.

## 15. Conclusion
Phase 07 requires significant enhancements to the parser baseline and integration logic. The baseline provides a starting point for basic structural components but lacks critical functionality for a complete semantic model representation as defined in the contract.

---

BASELINE_CAPABILITY_INVESTIGATION_COMPLETE

- Files created: `inspection/PHASE_07_BASELINE_CAPABILITY_INVESTIGATION.md`
- Files modified: None
- Parser modifications: None
- Implementation modifications: None
- Contract modifications: None
- Governance modifications: None
- Dependencies added: None
- Capabilities confirmed: Tables, Columns, Measures, Basic Metadata (lineageTag, dataType, etc.)
- Capabilities unavailable: Relationships, Hierarchies, Partitions, M expressions, Line/Column range information.
- Capabilities uncertain: Relationship parsing (assumed unsupported based on `canonicalizer.py`).
