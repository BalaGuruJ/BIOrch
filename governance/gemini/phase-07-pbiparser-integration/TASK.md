# Phase 07 — Power BI Integration (Implementation Task)

**Contract:** `contracts/powerbi-agent/POWERBI_AGENT_CONTRACT.md`

**Phase:** Phase 07 — Power BI Integration

**Status:** COMPLETED

**Capability:** Power BI Semantic Model Metadata Extraction

---

## 1. Objective

Implement a deterministic, reproducible, metadata-only Power BI Semantic Model
extraction capability for BIOrch.

The implementation MUST extract metadata from the Power BI Semantic Model,
canonicalize that metadata into the stable BIOrch canonical model, validate the
canonical representation, and produce deterministic JSON conforming to:

`schemas/phase07_metadata.schema.json`

The implementation MUST follow the authoritative
`POWERBI_AGENT_CONTRACT.md`.

---

## 2. Approved Parser Architecture

The approved parser architecture is:

```text
Power BI TMDL Semantic Model
        |
        v
Microsoft Analysis Services Tabular Object Model (TOM)
        |
        v
pythonnet / CoreCLR
        |
        v
Power BI Parser Adapter
        |
        v
BIOrch Canonical Model
        |
        v
Structural Validation
        |
        v
Deterministic Serialization
        |
        v
phase07_metadata.schema.json
````

The Microsoft Analysis Services Tabular Object Model is the selected parser
implementation for Phase 07.

The parser MUST be accessed from the Python BIOrch runtime through
`pythonnet` and CoreCLR.

The feasibility investigation demonstrated successful loading of the
AdventureWorks TMDL fixture using:

`TmdlSerializer.DeserializeDatabaseFromFolder`

The feasibility evidence is documented in:

`inspection/PHASE_07_TOM_DOTNET_INTEROP_FEASIBILITY.md`

The implementation MUST use this proven architecture as the starting point.

---

## 3. Runtime and Dependency Requirements

The implementation MUST support the established runtime architecture:

* Python 3.12-compatible environment
* .NET 8+ runtime
* CoreCLR
* `pythonnet`
* `Microsoft.AnalysisServices`
* required supporting interop dependencies

The implementation MUST explicitly declare all runtime dependencies.

The implementation MUST pin or otherwise deterministically constrain the
versions required for reproducibility.

The feasibility baseline used:

* Python 3.12.x
* .NET 8.0
* `pythonnet` 3.2.0
* `Microsoft.AnalysisServices` 19.117.0
* `clr_loader` 0.3.1
* `cffi` 2.1.1

These versions form the initial reproducibility baseline.

If implementation requires a different version, the change MUST be documented
with the reason and compatibility evidence.

The implementation MUST NOT rely on packages being installed implicitly in the
developer's environment.

The final dependency configuration MUST permit reproduction in a clean
environment.

---

## 4. Runtime Environment Boundary

The .NET runtime is an explicit dependency of the Phase 07 Power BI parser.

The implementation MUST clearly establish how the Python BIOrch runtime locates
and initializes CoreCLR.

Environment-specific configuration MUST NOT be silently assumed.

Where environment variables such as `DOTNET_ROOT` or
`PYTHONNET_RUNTIME=coreclr` are required, the installation and execution
documentation MUST describe them.

The implementation MUST fail clearly and deterministically when the required
.NET runtime or parser dependency is unavailable.

---

## 5. Input Boundary

The primary input is a Power BI Semantic Model definition directory containing
the TMDL semantic-model metadata.

The implementation MUST support the repository's AdventureWorks Sales
semantic-model fixture.

The `.pbip` wrapper file MUST NOT be required when the semantic-model
definition directory contains the required metadata.

The implementation MUST treat the semantic-model definition as the authoritative
input boundary.

Power BI report/visual metadata is outside this task.

---

## 6. Parser Adapter Boundary

TOM-specific and .NET-specific objects MUST remain behind the Power BI parser
adapter boundary.

The canonical BIOrch model MUST NOT expose:

* TOM classes
* .NET objects
* `pythonnet` objects
* parser-specific collections
* parser-specific implementation details

The adapter MUST convert parser output into BIOrch-owned representations.

The adapter boundary MUST be testable independently of the parser internals.

---

## 7. Canonical Model Requirements

The implementation MUST support canonical representation of:

* Model
* Table
* Column
* CalculatedColumn
* Measure
* Relationship
* Hierarchy
* HierarchyLevel
* Partition
* CalculationGroup
* CalculationItem
* Annotation
* SourceEvidence
* UnresolvedMetadata

The canonical model MUST remain independent of TOM implementation classes.

The canonical model MUST represent semantic distinctions required by the
authoritative contract.

---

## 8. Required Metadata Coverage

Where represented by the source model and exposed by the selected parser, the
implementation MUST preserve:

### Model

* model identity
* model metadata
* source evidence

### Tables

* table identity
* table name
* hidden state
* annotations
* lineage metadata
* provenance

### Columns

* column identity
* table identity
* column name
* data type
* source column
* hidden state
* display folder where available
* summarization behavior where available
* format information where available
* annotations
* lineage metadata
* provenance

### Calculated Columns

* calculated-column identity
* owning table
* expression text
* provenance

### Measures

* measure identity
* owning table
* measure name
* DAX expression text
* format string where available
* display folder where available
* hidden state where available
* annotations
* lineage metadata
* provenance

### Relationships

* relationship identity
* source relationship identity where available
* from-table
* from-column
* to-table
* to-column
* cardinality
* active/inactive state
* cross-filter direction where available
* provenance

### Hierarchies

* hierarchy identity
* owning table
* hierarchy name
* hierarchy levels
* level ordering
* referenced columns
* provenance

### Partitions

* partition identity
* owning table
* source information
* storage/source type where available
* M expression text where available
* provenance

### Calculation Groups

* calculation-group identity
* owning table/object
* calculation items
* calculation-item identity
* calculation-item expression
* ordering metadata where available
* annotations
* provenance

---

## 9. Expression Handling

DAX expressions and M expressions MUST be treated strictly as metadata.

The implementation MUST preserve expression text where available.

The implementation MUST NOT:

* execute DAX
* evaluate DAX
* execute M
* evaluate M
* execute arbitrary model expressions
* interpret metadata as executable code

Expression extraction MUST remain a metadata-only operation.

---

## 10. Identity Architecture

The implementation MUST maintain a strict distinction between:

1. Source Identity
2. BIOrch Canonical Identity
3. Lineage Identity/Metadata

Canonical identity MUST be:

* deterministic
* stable
* reproducible
* independent of parser object identity
* independent of memory addresses
* independent of traversal order

A source `lineageTag` MUST NOT automatically become the BIOrch canonical ID.

The canonical identity algorithm MUST be documented and tested.

---

## 11. Provenance Architecture

Provenance MUST be propagated from the parser/source into the canonical model
where source evidence is available.

Provenance SHOULD identify, where available:

* source type
* source file
* source object
* source location/range
* parser/source evidence

The implementation MUST NOT fabricate:

* line numbers
* column numbers
* source ranges
* source identifiers
* parser evidence

When precise source location is unavailable, the implementation MUST represent
that limitation explicitly.

Provenance generation MUST be deterministic.

---

## 12. Unsupported and Unresolved Metadata

The implementation MUST NOT silently discard semantic metadata.

Metadata states MUST distinguish:

* `SUPPORTED`
* `UNSUPPORTED`
* `UNRESOLVED`
* `UNAVAILABLE`
* `INVALID`

When a semantic construct is encountered but cannot currently be represented,
the implementation MUST preserve sufficient information to identify the
construct where technically possible.

The implementation MUST NOT fabricate metadata to fill parser gaps.

Required/structural metadata that is absent or invalid MUST result in
deterministic validation failure where required by the contract.

Optional unsupported metadata MUST be explicitly classified.

---

## 13. Structural Validation

Validation MUST occur after canonicalization.

Validation MUST be deterministic.

Validation MUST cover at minimum:

### Identity

* duplicate canonical IDs
* invalid canonical IDs
* source/canonical identity consistency

### References

* unresolved table references
* unresolved column references
* unresolved relationship endpoints
* unresolved hierarchy references
* unresolved partition ownership
* unresolved calculation-group references

### Structure

* malformed entities
* missing required fields
* invalid relationships
* invalid hierarchy structures
* invalid partition ownership
* invalid calculation-group structures

### Provenance

* malformed provenance
* invalid source references where detectable

### Serialization

* deterministic output
* JSON Schema compliance

The implementation MUST NOT create fabricated relationships or references merely
to satisfy validation.

---

## 14. Deterministic Serialization

The implementation MUST produce deterministic JSON.

For identical semantic-model input and identical parser/dependency versions,
the canonical output MUST be equivalent.

Output MUST NOT depend on:

* filesystem traversal order
* dictionary iteration accidents
* memory addresses
* timestamps
* random identifiers
* network responses

Collections MUST have deterministic ordering whenever source semantics do not
define an ordering.

The serializer MUST NOT expose TOM/.NET objects.

---

## 15. JSON Schema

The external representation MUST conform to:

`schemas/phase07_metadata.schema.json`

If implementation requires a schema change, the schema MUST be updated as part
of the same governed implementation change.

The schema MUST NOT be weakened merely to accommodate implementation
limitations.

Any schema change MUST be covered by tests.

---

## 16. Security and Runtime Constraints

The Phase 07 implementation MUST:

* require no LLM
* require no external network access during normal parsing
* perform local metadata extraction
* execute no DAX
* execute no M
* execute no arbitrary model expressions
* execute no arbitrary code contained in metadata
* avoid Power BI report execution
* avoid semantic-model modification

The parser MUST operate in a read-only extraction role.

TOM MUST NOT be used to modify or save the source semantic model.

---

## 17. Historical Parser Baseline

The historical parser artifacts remain reference evidence only.

In particular:

`examples/artifacts/powerbi/phase7_powerbi_parser/`

and any historical `tmdlparser` implementation MUST NOT become runtime
dependencies.

The implementation MUST NOT attempt to install or substitute an unrelated
package merely because it has the same or similar package name.

The historical parser MAY be inspected for comparison, but Phase 07 runtime
correctness MUST NOT depend on it.

---

## 18. AdventureWorks Reference Fixture

The AdventureWorks Sales semantic model is the primary Phase 07 reference
fixture.

The implementation MUST successfully process the fixture.

The fixture MUST NOT be modified merely to make tests pass.

The implementation MUST demonstrate extraction of the metadata supported by
the fixture, including at minimum:

* tables
* columns
* measures
* relationships
* hierarchies where present
* partitions where present
* applicable advanced metadata

Features not exercised by the primary fixture MUST receive dedicated fixtures
before the implementation claims complete coverage for those features.

---

## 19. Testing Requirements

The implementation MUST provide automated tests covering:

### Positive Tests

* valid AdventureWorks semantic model
* tables
* columns
* measures
* calculated columns where available
* relationships
* hierarchies where available
* partitions where available
* advanced metadata where available

### Negative Tests

* missing semantic-model directory
* invalid input path
* malformed TMDL
* missing required metadata
* unresolved references
* invalid relationship endpoints
* invalid hierarchy references
* invalid canonical structures

### Identity Tests

* deterministic canonical identity
* source/canonical identity separation
* repeatability across multiple runs
* independence from traversal ordering

### Provenance Tests

* source file preservation
* provenance propagation
* unavailable-location handling
* no fabricated source locations

### Adapter Tests

* TOM-to-canonical mapping
* parser object isolation
* parser-specific object non-leakage

### Serialization Tests

* deterministic JSON
* stable collection ordering
* JSON Schema validation
* invalid-model rejection

### Security Tests

* no DAX execution
* no M execution
* no network requirement
* no arbitrary metadata execution
* read-only behavior

### Environment Tests

* clean-environment installation
* .NET runtime availability
* pythonnet/CoreCLR initialization
* Microsoft.AnalysisServices dependency loading
* AdventureWorks parsing in the clean environment

### Regression Tests

Existing BIOrch functionality, particularly Phase 06 Tableau integration,
MUST remain protected.

---

## 20. Dependency Reproducibility Evidence

The implementation MUST produce evidence showing that a clean environment can
reproduce the Phase 07 parser runtime.

Evidence MUST include:

* Python version
* .NET runtime version
* pythonnet version
* Microsoft.AnalysisServices version
* supporting dependency versions
* installation procedure
* required environment configuration
* successful parser initialization
* successful AdventureWorks processing

The final dependency configuration MUST be committed as part of the governed
implementation.

---

## 21. Implementation Sequence

Implementation SHOULD proceed in the following controlled sequence:

1. Establish the reproducible Python/.NET/pythonnet environment.

2. Declare and pin/constrain parser dependencies.

3. Implement CoreCLR initialization and TOM loading boundary.

4. Implement the Power BI parser adapter.

5. Implement or update BIOrch canonical entities.

6. Implement TOM-to-canonical canonicalization.

7. Implement source identity and canonical identity handling.

8. Implement provenance propagation.

9. Implement unsupported/unresolved metadata classification.

10. Implement structural validation.

11. Implement deterministic serialization.

12. Update `phase07_metadata.schema.json` only where required by the
    authoritative canonical representation.

13. Implement comprehensive Phase 07 tests.

14. Add dedicated fixtures where the AdventureWorks fixture does not exercise
    required advanced features.

15. Run Phase 06 regression protection.

16. Perform clean-environment reproduction.

17. Produce implementation, validation, dependency, and reproducibility
    evidence.

18. Prepare the Phase 07 implementation response and review artifacts.

---

## 22. Implementation Constraints

Implementation MUST NOT:

* use the historical parser as a runtime dependency
* introduce an unrelated `tmdlparser` package as a substitute
* bypass the parser adapter boundary
* expose TOM objects as canonical entities
* execute DAX or M
* introduce an LLM into parsing
* introduce network-dependent parsing
* fabricate metadata
* silently discard discovered metadata
* weaken the JSON schema to hide implementation limitations
* modify the reference fixture solely to satisfy tests
* modify the authoritative contract to make implementation pass

If implementation discovers a conflict with the authoritative contract,
implementation MUST stop and report the conflict through governance.

---

## 23. Required Implementation Evidence

At completion, the implementation MUST provide evidence covering:

1. Selected parser and exact dependency versions.

2. Reproducible installation procedure.

3. .NET/CoreCLR runtime requirements.

4. Successful TOM initialization.

5. Successful AdventureWorks TMDL processing.

6. Canonical entity extraction.

7. Identity determinism.

8. Provenance propagation.

9. Unsupported/unresolved metadata handling.

10. Structural validation.

11. Deterministic serialization.

12. JSON Schema validation.

13. Security/runtime constraints.

14. Clean-environment reproduction.

15. Phase 06 regression results.

---

## 24. Phase 07 Acceptance Criteria

Phase 07 MUST NOT be considered complete until all applicable contract
acceptance criteria are satisfied.

At minimum:

1. Microsoft TOM is integrated through the approved Python/.NET architecture.

2. Runtime dependencies are explicitly declared and reproducible.

3. .NET 8+ / CoreCLR runtime requirements are documented and reproducible.

4. The historical parser is not required at runtime.

5. AdventureWorks can be processed successfully.

6. Canonical identities are deterministic.

7. Source identity and canonical identity remain distinct.

8. Lineage metadata remains distinct from canonical identity.

9. Provenance is propagated without fabrication.

10. Relationships are represented and validated.

11. Required supported metadata is represented.

12. Unsupported/unresolved metadata is explicitly classified.

13. No semantic metadata is fabricated or silently discarded.

14. Deterministic JSON serialization is implemented.

15. JSON output validates against `phase07_metadata.schema.json`.

16. Positive and negative tests are present.

17. Identity and provenance tests are present.

18. Adapter isolation is tested.

19. Security constraints are tested.

20. Clean-environment reproduction succeeds.

21. Phase 06 regression protection remains intact.

22. No DAX/M execution occurs.

23. No LLM or network dependency is required for normal parsing.

24. Implementation evidence is complete.

25. TASK, implementation response, validation evidence, and review artifacts
    remain consistent with the authoritative contract.

---

## 25. Explicit Non-Goals

This task does NOT implement:

* Power BI Report/visual parsing
* PBIR visual parsing
* report layout analysis
* visual lineage
* Power BI Service integration
* Fabric integration
* XMLA network access
* DAX execution
* M execution
* semantic-model modification
* report modification
* automatic metadata repair
* LLM-based semantic interpretation
* network-dependent parsing

These capabilities require future governed work.

---

## 26. Governance Relationship

The authoritative governance hierarchy is:

```text
POWERBI_AGENT_CONTRACT.md
            |
            v
         TASK.md
            |
            v
      Implementation
            |
            v
       RESPONSE.md
            |
            v
        REVIEW.md
            |
            v
      Phase Closure
```

`TASK.md` MUST NOT redefine, weaken, or contradict the authoritative contract.

If implementation discovers a requirement conflict, implementation MUST stop and
the contract MUST be reviewed through the governance process.

Implementation MUST NOT silently reinterpret the contract.

---

## 27. Final Architectural Principle

The parser is replaceable.

The BIOrch canonical contract is not.

Microsoft TOM is the approved Phase 07 parser implementation.

pythonnet/CoreCLR is the approved interoperability boundary.

The historical parser is evidence only.

The selected parser is an implementation dependency.

The BIOrch canonical model is the stable integration boundary.

No parser-specific limitation may silently redefine the BIOrch semantic model.

---