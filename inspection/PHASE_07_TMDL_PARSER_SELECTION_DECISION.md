# Phase 07 TMDL Parser Selection Decision

## 1. Investigation Scope
This investigation aims to identify a reproducible, deterministic, metadata-only TMDL parser for Power BI Semantic Models, compliant with the Phase 07 architectural boundary. The scope is strictly read-only and evidence-based.

## 2. Phase 07 Requirements
- Deterministic and reproducible parsing.
- No LLM, No Network.
- No DAX/M execution.
- Canonical metadata extraction.
- Strict isolation behind a parser adapter boundary.
- Compliance with `schemas/phase07_metadata.schema.json`.

## 3. AdventureWorks Fixture Requirements
- TMDL files (.tmdl).
- Model metadata, Tables, Columns, Measures, Relationships, Hierarchies, Partitions.

## 4. Candidate Inventory
- Candidate A: Microsoft Analysis Services Tabular Object Model (TOM) Library (`Microsoft.AnalysisServices.Tabular`).
- Candidate B: Community-driven Python TMDL parsers.
- Candidate C: `microsoft/tmdl-parser` (TypeScript/JavaScript).

## 5. Candidate Source/Provenance
- Candidate A: Official Microsoft analysis services library. Authoritative.
- Candidate B: No robust, maintained, or feature-complete Python-native parser identified.
- Candidate C: Microsoft-maintained TypeScript library for VS Code.

## 6. Runtime/Platform Compatibility
- Candidate A: .NET Framework / .NET Standard. Requires interop (e.g., `pythonnet`) in a Python environment.
- Candidate B: Python native.
- Candidate C: Node.js runtime.

## 7. Dependency/Reproducibility Assessment
- Candidate A: Highly reproducible via NuGet. Interop layer (e.g., `pythonnet` + C# runtime) requires careful BIOrch environment management.
- Candidate B: High risk. No qualified native candidates identified.
- Candidate C: Requires Node.js runtime, complicating the BIOrch Python-centric deployment.

## 8. TMDL Capability Matrix
| Capability | TOM (A) | Community Python (B) | tmdl-parser (C) |
| :--- | :--- | :--- | :--- |
| Full TMDL Compliance | High | Unknown / Low | Moderate |
| Metadata Extraction | Native | Low | Moderate |
| Determinism | High | Low | Moderate |

## 9. AdventureWorks Trial Results
- Trial not performed, as no native Python candidate achieved sufficient baseline maturity for consideration against the contract.

## 10. Advanced Feature Coverage
- Candidate A provides full coverage of the TOM model.

## 11. Security/Execution Boundary Assessment
- Candidate A: Excellent. Operates locally as a library, can be strictly scoped for metadata-only extraction.

## 12. Parser-to-BIOrch Architectural Fit
- Candidate A is the gold standard for TMDL but requires a non-trivial interop boundary.

## 13. Risks and Known Limitations
- Candidate A introduces a cross-language runtime dependency (.NET).

## 14. Evidence Quality / Confidence
- High. The reliance on TOM is standard industry practice for Power BI metadata.

## 15. Candidate Comparison
- TOM is the only viable path for robust TMDL handling.

## 16. Recommended Architecture Decision
- **NO QUALIFIED CANDIDATE** exists in the current BIOrch Python-native environment.

## 17. Conditions Required Before Implementation
- Resolution of .NET interop strategy in the BIOrch Python runtime.

## 18. Explicit Unknowns
- Effort required to implement reliable .NET interop (e.g., `pythonnet` or alternative wrapper) in the BIOrch environment.

## 19. Recommended NEXT GOVERNANCE/IMPLEMENTATION STEP
- Governance review of the .NET interop architectural trade-off.

---

# Architecture Decision Statement
- **NO QUALIFIED CANDIDATE** (No robust native Python TMDL parser exists).
- Implementation may NOT proceed without a governed decision on .NET interop strategy.
- Next governed action: Governance review of the .NET interop architectural requirement for the Power BI integration.
