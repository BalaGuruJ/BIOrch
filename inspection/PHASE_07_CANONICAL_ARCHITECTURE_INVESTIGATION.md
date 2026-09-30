# PHASE_07_CANONICAL_ARCHITECTURE_INVESTIGATION.md

## 1. Executive Summary

This report provides a read-only architectural investigation of the existing Phase 07 Power BI implementation against the authoritative `contracts/powerbi-agent/POWERBI_AGENT_CONTRACT.md`. The current implementation provides a basic functional baseline (canonicalization, serialization, and minimal validation) but is significantly incomplete regarding contract requirements for advanced metadata, provenance, and robust structural validation.

## 2. Existing BIOrch Canonical Architecture

BIOrch canonical entities are primarily defined within the integration-specific boundaries (e.g., `src/biorch/integrations/powerbi/canonical_entities.py`). Currently, these entities are isolated to the Power BI integration and do not utilize generic BIOrch canonical structures, creating a siloed approach that may need reconciliation if multi-BI tool comparison (Phase 11) is to be unified.

## 3. Existing Power BI Architecture

The implementation follows a modular structure:
- **Adapter (`adapter.py`)**: Interfaces with the third-party baseline parser.
- **Canonicalizer (`canonicalizer.py`)**: Maps parser output to `CanonicalModel`.
- **Entities (`canonical_entities.py`)**: Defines simple data classes for the canonical model.
- **Validator (`validator.py`)**: Performs existence checks for table/column/relationship references.
- **Serializer (`serializer.py`)**: Converts `CanonicalModel` to JSON.

## 4. Contract-to-Implementation Gap Matrix

| Requirement | Classification | Gap | Recommended Resolution |
|---|---|---|---|
| Model metadata | MISSING | Not supported | Extend `CanonicalModel` |
| Lineage | MISSING | Not supported | Extend entities/schema |
| Provenance | MISSING | Unused | Populate `SourceEvidence` |
| Hierarchies | MISSING | Not supported | Add entity |
| Partitions/M | MISSING | Not supported | Add entity |
| Relationship val. | PARTIAL | Basic existence | Enhance validation rules |
| Negative testing | MISSING | Entirely absent | Add comprehensive tests |
| Schema validation | PARTIAL | Schema is too minimal | Expand schema |

## 5. Canonical Entity Mapping

Entities require substantial extension:
- `Model`: Currently nonexistent.
- `Table`/`Column`/`Measure`: Need to add advanced metadata attributes.
- `Relationships`: Need to add cardinality, active state, filtering behavior.
- `Hierarchies`/`Partitions`/`CalculationGroups`: Need new entities.

## 6. Identity Strategy Recommendation

The current implementation implicitly uses source-provided IDs. The strategy must be enhanced to separate `SourceID` (Power BI specific) from `CanonicalID` (BIOrch stable) to ensure stability across parser changes.

## 7. Provenance Strategy Recommendation

`SourceEvidence` in `entities.py` exists but is currently ignored by `canonicalizer.py`. The recommended approach is to ensure the adapter exposes parsing context, allowing the canonicalizer to populate `SourceEvidence` for every entity.

## 8. Relationship Resolution Analysis

Basic reference existence checks exist in `validator.py`. Missing are complex validation rules (e.g., table-to-column relationship validity, hierarchy-to-level mapping validity, partition-to-table integrity).

## 9. Unsupported / Unresolved Metadata Strategy

Currently, metadata is implicitly ignored if not handled by `canonicalizer.py`. The contract requires explicit handling. A `MetadataCollector` or similar construct should be designed to capture unresolved items, which the validator can then check against accepted-unresolved-metadata policy.

## 10. Validation Architecture

The current validation in `validator.py` is integration-specific and overly simple. It should be refactored into a layered validation approach (generic BIOrch structural validation + Power BI specific metadata constraints).

## 11. Schema Gap Analysis

`schemas/phase07_metadata.schema.json` is severely limited. It requires expansion to include the entities and attributes listed in the contract (hierarchies, partitions, metadata fields).

## 12. Test Matrix

A comprehensive test matrix is required covering:
- **Positive**: Full entity extraction exercise (using AdventureWorks).
- **Negative**: Missing/malformed model, duplicate IDs, invalid references, serialization failure.
- **Regression**: Existing Tableau integration tests.

## 13. Baseline Parser Capability Matrix

| Feature | Supported | Status |
|---|---|---|
| Table/Col/Measure | Yes | SUPPORTED |
| Relationships | Basic | SUPPORTED |
| Hierarchies | No | NOT_SUPPORTED |
| Partitions/M | No | NOT_SUPPORTED |
| Provenance | No | UNKNOWN |

*Note: Further investigation of the `powerbi_parser_baseline` is needed to confirm full capabilities.*

## 14. AdventureWorks Fixture Evidence

The fixture (`examples/artifacts/powerbi/AdventureWorks Sales/`) provides tables, columns, measures, and basic relationships. It lacks advanced structures like hierarchies and calculation groups, necessitating additional fixtures to fully exercise the contract.

## 15. Recommended Implementation Sequence

1. Define comprehensive `CanonicalModel` and `Schema`.
2. Update `canonicalizer.py` and `validator.py` to support advanced metadata.
3. Integrate `SourceEvidence` population.
4. Implement comprehensive test suite (including negative tests).
5. Update `serializer.py` and `schema` to output enhanced metadata.

## 16. Open Design Decisions

- How to unify BIOrch canonical entities across Power BI and Tableau (Phase 11 alignment).
- Policy for handling unresolved/unsupported metadata (strict failure vs. warning).

## 17. Explicit Non-Goals

- Report metadata parsing (Scope: Semantic Model only).
- Automated metadata repair.

## 18. Conclusion

Phase 07 requires substantial hardening. The current baseline is a functional skeleton, but it does not meet the authoritative Phase 07 V1 contract requirements for robustness, provenance, validation, and metadata coverage.

---

CANONICAL_ARCHITECTURE_INVESTIGATION_COMPLETE

- **Files created**: `inspection/PHASE_07_CANONICAL_ARCHITECTURE_INVESTIGATION.md`
- **Files modified**: None
- **Implementation changes**: None
- **Contract changes**: None
- **Governance changes**: None
- **Baseline changes**: None
- **Dependencies added**: None
- **Major design decisions identified**: Identity separation (Source vs. Canonical), Provenance integration, Advanced Metadata entities, Unified Validation.
- **Major remaining gaps**: Provenance, Hierarchies, Calculation Groups, Advanced validation rules, Negative tests.
