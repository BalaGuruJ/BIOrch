# PHASE_07_BASELINE_RUNTIME_INVESTIGATION

## 1. Executive Summary
This report documents a read-only investigation into the existing Power BI parser baseline, designed to identify its capabilities and runtime requirements. The investigation reveals that the parser relies on an unavailable third-party dependency (`tmdlparser`), rendering runtime execution impossible in the current environment. Analysis of the baseline adapter code (`tmdl_parser_adapter.py`) shows it only exposes tables, columns, and measures, while ignoring other semantic constructs like relationships, even though the reference fixture (`AdventureWorks Sales`) contains them.

## 2. Baseline Dependency Requirements
- **Package Name**: `tmdlparser`
- **Installation Status**: Unavailable in the project environment (`ModuleNotFoundError`).
- **Compatibility**: Unknown (No dependency declaration found in the baseline directory).

## 3. Baseline Parser Architecture
- **Adapter (`tmdl_parser_adapter.py`)**: Defines `TMDLParserAdapter` which encapsulates the `tmdlparser` dependency.
- **Parsing Strategy**: Traverses a directory, identifies `.tmdl` files, and delegates parsing to `tmdlparser.TMLDParser.parse_file()`.
- **Mapping Strategy**: Iterates only over `table ` elements. Maps properties like `column`, `measure`, `lineageTag`, `dataType`, `formatString`, `summarizeBy`, `sourceColumn`, `displayFolder`, `isHidden`.

## 4. Parser Entry Points
- `parse_semantic_model(model_directory: str)`: Loads all `.tmdl` files in a directory.
- `parse_tmdl_fragment(fragment: str, source_file: str)`: Parses an individual TMDL string fragment.

## 5. Runtime Environment
- Current environment: `linux`
- Virtual environment: `.venv/`
- Dependencies: `tmdlparser` is missing.

## 6. Runtime Execution Result
- **Status**: UNVERIFIED
- **Reason**: `ModuleNotFoundError: No module named 'tmdlparser'`

## 7. AdventureWorks Fixture Inventory
- **TMDL files**: `database.tmdl`, `model.tmdl`, `relationships.tmdl`, and 10 table definitions (Category, Customer, Date, Date Role, Product, Reseller, Sales Order, Sales Territory, Sales, Time Intelligence).
- **Constructs present**: Relationships, tables, columns, measures.

## 8. Parser-library Capability Matrix
- **Tables/Columns/Measures**: UNVERIFIED (Parser library API call not testable).
- **Relationships**: UNVERIFIED.

## 9. Baseline-adapter Capability Matrix
- **Tables/Columns/Measures**: SUPPORTED
- **Relationships**: UNSUPPORTED (Ignored by adapter logic)

## 10. Runtime-verified Capability Matrix
- **All constructs**: UNVERIFIED due to dependency failure.

## 11. Parser vs adapter vs canonicalizer distinction
- The **parser library** is unknown/untestable.
- The **adapter** consciously limits parsing to `table ` elements only, discarding `relationships` and other metadata.
- The **canonicalizer** only consumes tables/columns/measures, ignoring everything else passed by the adapter.

## 12. Provenance Capability
- **Source File**: `Provenance(source_type='TMDL', file=source_file, range=None)`
- **Range (Line/Col)**: NOT_SUPPORTED (Explicitly omitted).

## 13. Identity Capability
- Uses `Identity.table_id()` and `Identity.column_id()`.

## 14. Expression Capability
- Measure/Calculated Column DAX: SUPPORTED (as string).
- M expressions: UNSUPPORTED.

## 15. Unsupported vs Unverified classification
- Capability classification:
    - Tables/Columns/Measures: ADAPTER_SUPPORTED
    - Relationships: ADAPTER_IGNORED
    - Dependency: MISSING

## 16. Exact Dependency Failure Evidence
```
WARNING: Package(s) not found: tmdlparser
```

## 17. Known Limitations
- Adapter is coupled to an unavailable third-party parser.
- Adapter ignores relationship metadata even when present in fixture.

## 18. Open Questions
- What is the canonical source for the `tmdlparser` package?
- Can the existing adapter be extended to handle `relationships` definitions?

## 19. Explicit Non-Goals
- Any implementation, architectural redesign, or dependency modification.

---

### Integrity Requirements
- Files created: `inspection/PHASE_07_BASELINE_RUNTIME_INVESTIGATION.md`
- Files modified: None
- Baseline files modified: NO
- Contract modified: NO
- Governance modified: NO
- Schema modified: NO
- Tests modified: NO
- Dependencies permanently added: NO
- Reference fixture modified: NO

BASELINE_RUNTIME_INVESTIGATION_COMPLETE
