# Phase 07: TMDL Parser Candidate Investigation Report

## A. Investigation Scope
This investigation is a read-only assessment to identify reproducible, Linux-compatible TMDL parser candidates capable of satisfying the Phase 07 contract requirements against the existing `AdventureWorks Sales` Power BI fixture.

## B. Existing Fixture Requirements
The `AdventureWorks Sales` fixture consists of a `.pbip` file and a `SemanticModel` folder structure containing TMDL definition files (`.tmdl`).
The requirements for a candidate parser include the ability to parse:
Tables, Columns, Measures, Calculated Columns, Relationships (IDs, Cardinality, Cross-filtering, Active/Inactive), Hierarchies, Partitions, M Expressions, Calculation Groups, Annotations, lineageTag, DAX expressions, quoted identifiers, multiline expressions, culture/model metadata, and source/provenance information.

## C. Candidate Inventory
1. **`pytmdl`**: Pure Python, Pydantic-based.
2. **`tmdl-parser`**: Pure Python, typed structures.
3. **Microsoft .NET TOM (via `pythonnet`)**: Official .NET-based approach.
4. **Microsoft Fabric Semantic Link (`sempy_labs`)**: Cloud/Fabric-native approach.

## D. Candidate Capability Matrix

| Candidate | Fixture Compatibility | Contract Compatibility | Provenance Support |
| :--- | :--- | :--- | :--- |
| `pytmdl` | NOT_CONFIRMED | NOT_CONFIRMED | NOT_CONFIRMED |
| `tmdl-parser` | NOT_CONFIRMED | NOT_CONFIRMED | NOT_CONFIRMED |
| .NET TOM | CONFIRMED (Ref) | CONFIRMED | CONFIRMED |
| `sempy_labs` | CONFIRMED (Env) | CONFIRMED | CONFIRMED |

## E. Runtime/Dependency Matrix

| Candidate | Runtime/Language | OS Compatibility | Python 3.12 Compatibility |
| :--- | :--- | :--- | :--- |
| `pytmdl` | Python | Linux/Windows/Mac | Yes |
| `tmdl-parser` | Python | Linux/Windows/Mac | Yes |
| .NET TOM | .NET / Windows | Windows-focused | Dependent on Interop |
| `sempy_labs` | Cloud/Fabric | Fabric Env | Yes (in Fabric) |

## F. Provenance/Source-Location Matrix

| Candidate | Documented Public Source | Active Maintenance | Installation Mechanism |
| :--- | :--- | :--- | :--- |
| `pytmdl` | GitHub/PyPI | NOT_CONFIRMED | pip |
| `tmdl-parser` | GitHub/PyPI | NOT_CONFIRMED | pip |
| .NET TOM | Microsoft Docs | High | NuGet/.NET |
| `sempy_labs` | Microsoft Docs | High | pip |

## G. Fixture Compatibility Assessment
The pure Python parsers (`pytmdl`, `tmdl-parser`) require practical testing against the actual `examples/artifacts/powerbi/AdventureWorks Sales/` fixture to determine if they can handle complex constructs like nested folder structures, specific DAX/M expression escaping, and multi-line definitions present in the fixture.

## H. Contract Compatibility Assessment
The Phase 07 contract assumes a robust, production-grade parser. The pure Python candidates are likely community-driven and may lack comprehensive coverage for all advanced TMDL features (e.g., calculation groups, specific lineage tags).

## I. Unknowns Requiring Practical Testing
- Accuracy of parsing complex multi-line DAX/M expressions.
- Handling of folder-based hierarchical TMDL structures.
- Completeness of attribute mapping against the full TMDL specification.

## J. Risks of Replacing the Historical Baseline
- Community parsers might be abandoned.
- Parsing logic differences could lead to drift from official Microsoft interpretation of TMDL.
- Implementing a custom parser logic around a library may be fragile.

## K. Recommended NEXT Investigation Only
Conduct a restricted, read-only "parsing trial" (using a temporary, isolated script) on the `AdventureWorks Sales` fixture using `pytmdl` and `tmdl-parser` to determine if they successfully load the model structure without error and if the object metadata is accessible.

TMDL_PARSER_CANDIDATE_INVESTIGATION_COMPLETE
