# BIOrch Power BI Agent Architecture Contract

**Contract:** POWERBI_AGENT_CONTRACT
**Version:** V2.0
**Phase:** Phase 07 — Power BI Integration
**Status:** AUTHORITATIVE — ARCHITECTURE BASELINE
**Capability:** Power BI Semantic Model Metadata Extraction

---

## 1. Purpose

This contract defines the authoritative architectural and behavioral boundary
for the BIOrch Power BI integration.

Phase 07 establishes a deterministic, reproducible, metadata-only capability
for extracting Power BI Semantic Model metadata and converting it into a
stable BIOrch canonical representation.

This contract defines the required BIOrch behavior independently of any
specific third-party parser implementation.

---

# 2. Architectural Objective

The Phase 07 architecture MUST establish the following pipeline:

    Power BI Semantic Model
            |
            v
    Parser Implementation Boundary
            |
            v
    Power BI Adapter
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
    Contracted JSON Artifact

The parser implementation is an internal implementation detail.

The canonical BIOrch representation is the architectural boundary that
protects the rest of BIOrch from parser-specific structures.

---

# 3. Scope

## 3.1 In Scope

Phase 07 covers metadata extraction from a Power BI Semantic Model,
including TMDL-based semantic model definitions.

The capability includes, where represented by the source model:

- model metadata
- tables
- columns
- calculated columns
- measures
- relationships
- relationship metadata
- hierarchies
- hierarchy levels
- partitions
- M expressions
- calculation groups
- calculation items
- annotations
- lineage metadata
- DAX expressions
- source metadata
- parser/source provenance

## 3.2 Explicitly Out of Scope

Phase 07 does NOT implement Power BI Report/visual metadata extraction.

The following are therefore outside the Phase 07 canonical semantic-model
boundary unless explicitly introduced by a future governed phase:

- report visuals
- visual configuration
- visual layout
- report pages
- bookmarks
- report interaction configuration
- report-level visual formatting

The presence of a PBIP project does not make report metadata part of the
Phase 07 semantic-model contract.

---

# 4. Input Boundary

The primary Phase 07 input is a Power BI Semantic Model definition.

The implementation MUST be capable of operating against the semantic-model
directory structure used by the supported PBIP/PBIR project representation.

The semantic-model definition is the authoritative input for semantic-model
metadata extraction.

The implementation MUST NOT require the `.pbip` wrapper file when the
semantic-model directory contains all required metadata.

The implementation MAY accept a higher-level PBIP path in the future, but
such support MUST resolve to the semantic-model boundary defined by this
contract.

---

# 5. Historical Parser Baseline

The existing artifact:

    examples/artifacts/powerbi/phase7_powerbi_parser/
    powerbi_parser_baseline/

is classified as:

    REFERENCE / NON-REPRODUCIBLE BASELINE

The repository evidence establishes that the historical adapter imports
`tmdlparser`, but the repository does not contain sufficient dependency
provenance to reproduce that parser.

The following have not been established:

- authoritative package source
- exact package version
- dependency declaration
- reproducible installation mechanism
- verified runtime compatibility

Therefore:

1. The historical parser MUST NOT be treated as a runtime dependency.
2. The historical parser MUST NOT be silently substituted with an unrelated
   package having the same or similar package name.
3. The historical parser artifact MUST be preserved as reference evidence
   unless a future governed decision explicitly changes that status.
4. The historical parser MAY be used for source-level comparison if it is
   available.
5. Phase 07 runtime correctness MUST NOT depend on successful execution of
   the historical parser.

The inability to reproduce the historical parser does not invalidate the
Power BI integration contract.

---

# 6. Parser Architecture Boundary

BIOrch MUST isolate parser-specific behavior behind a Power BI parser
adapter boundary.

The parser implementation MUST:

- operate deterministically;
- operate without an LLM;
- operate without network access during normal parsing;
- consume local semantic-model metadata;
- expose sufficient information for canonicalization;
- have explicitly declared dependencies;
- be reproducible in the supported BIOrch runtime;
- avoid exposing parser-specific objects beyond the adapter boundary.

The Phase 07 contract intentionally DOES NOT mandate a particular parser
library.

Parser selection is an implementation architecture decision that MUST be
made and documented before production implementation is considered complete.

A parser MUST NOT be selected solely because:

- a similarly named package exists;
- it is installable from PyPI;
- it happens to import successfully;
- it provides only a subset of the required metadata.

Parser selection MUST be based on demonstrated compatibility with the
Phase 07 requirements and the supported runtime.

---

# 7. Dependency Policy

All runtime parser dependencies MUST be:

1. explicitly declared;
2. reproducible;
3. deterministically version-constrained;
4. compatible with the supported BIOrch runtime;
5. installable through the project's documented dependency mechanism;
6. testable in a clean environment.

The implementation MUST NOT rely on an undeclared package existing in the
developer's local environment.

A dependency that cannot be reproduced from repository configuration MUST
NOT be considered a valid production runtime dependency.

The final selected parser dependency and its version/source MUST be recorded
by the implementation/governance artifacts before Phase 07 closure.

---

# 8. Canonical Model Boundary

The canonical model is the stable BIOrch representation.

Parser-specific classes MUST NOT become the BIOrch canonical model.

The canonical model MUST be capable of representing the following logical
entities:

- Model
- Table
- Column
- CalculatedColumn
- Measure
- Relationship
- Hierarchy
- HierarchyLevel
- Partition
- CalculationGroup
- CalculationItem
- Annotation
- SourceEvidence
- UnresolvedMetadata

The exact Python class structure is an implementation decision, but the
serialized contract MUST preserve the semantic distinctions above.

---

# 9. Model Metadata

The canonical model MUST provide a model-level identity and MUST provide
model metadata when such metadata exists in the source.

Model metadata MUST NOT be fabricated when unavailable.

Unavailable model metadata MUST be represented according to the unresolved
metadata policy defined by this contract.

---

# 10. Table Requirements

A canonical Table SHOULD include, where available:

- canonical identity
- source identity
- table name
- hidden state
- source/provenance information
- annotations
- lineage metadata
- associated partitions
- associated hierarchies

Table identity MUST be deterministic.

---

# 11. Column Requirements

A canonical Column SHOULD include, where available:

- canonical identity
- source identity
- table identity
- column name
- data type
- source column
- hidden state
- display folder
- summarization behavior
- format information
- lineage metadata
- annotations
- calculated-column expression where applicable
- provenance

Column references MUST resolve to an existing canonical table.

---

# 12. Measure Requirements

A canonical Measure SHOULD include, where available:

- canonical identity
- source identity
- table identity
- measure name
- DAX expression
- format string
- display folder
- hidden state
- annotations
- lineage metadata
- provenance

DAX MUST be preserved as metadata text.

DAX MUST NOT be executed by the Phase 07 extraction pipeline.

---

# 13. Calculated Column Requirements

Calculated columns MUST be represented distinctly from ordinary columns
when the source model identifies them as calculated columns.

Their expression MUST be preserved as metadata text where available.

Expressions MUST NOT be executed during parsing or canonicalization.

---

# 14. Relationship Requirements

Relationships MUST be represented explicitly.

Where available, a canonical Relationship SHOULD preserve:

- canonical relationship identity
- source relationship identity
- from-table identity
- from-column identity
- to-table identity
- to-column identity
- cardinality
- active/inactive state
- cross-filter direction
- provenance

Relationship endpoints MUST resolve to existing canonical entities.

The validator MUST detect unresolved relationship endpoints.

The implementation MUST NOT fabricate a relationship merely to satisfy
referential integrity.

---

# 15. Hierarchy Requirements

Where the source model contains hierarchies, the canonical model MUST
provide a representation for:

- hierarchy identity
- owning table
- hierarchy name
- hierarchy levels
- level ordering
- referenced columns
- provenance

Hierarchy references MUST resolve to valid canonical columns.

If a parser cannot extract a hierarchy, the implementation MUST NOT silently
discard it.

It MUST instead classify the construct according to the unresolved metadata
policy.

---

# 16. Partition and M Requirements

Where partitions are present, the canonical model MUST provide a partition
representation capable of preserving:

- partition identity
- owning table
- source information
- storage/source type where available
- M expression text where available
- provenance

M expressions MUST be treated as metadata.

M expressions MUST NOT be executed by Phase 07.

If M metadata cannot be parsed, it MUST NOT be fabricated or silently
discarded.

---

# 17. Calculation Groups

Where calculation groups are present, the canonical model MUST provide
representations for:

- calculation group identity
- owning table/object
- calculation items
- calculation item identity
- calculation item expression
- ordering metadata where available
- annotations
- provenance

Calculation-item expressions MUST be preserved as metadata and MUST NOT be
executed.

---

# 18. Annotations and Lineage

The implementation SHOULD preserve source annotations and lineage metadata
when exposed by the source format and parser.

Lineage metadata MUST remain distinct from BIOrch canonical identity.

A source `lineageTag` MUST NOT automatically become the BIOrch canonical ID.

---

# 19. Identity Architecture

Phase 07 MUST maintain a strict distinction between:

1. Source Identity
2. Canonical Identity
3. Lineage Identity/Metadata

## 19.1 Source Identity

Represents identity supplied by Power BI/TMDL or the parser.

## 19.2 Canonical Identity

Represents the stable BIOrch identity.

Canonical identities MUST:

- be deterministic;
- be stable for the same semantic object;
- not depend on object traversal order;
- not depend on memory addresses;
- not depend on parser object identity.

## 19.3 Lineage

Lineage metadata describes source-system lineage information.

It MUST NOT be conflated with canonical identity.

---

# 20. Provenance Architecture

Every canonical entity SHOULD carry provenance when source evidence is
available.

Provenance SHOULD distinguish:

- source type
- source file
- source object
- source location/range where available
- parser/source evidence

The implementation MUST NOT fabricate line numbers, columns, ranges,
identifiers, or source evidence.

If precise source location is unavailable, provenance MUST explicitly indicate
that the location is unavailable rather than inventing one.

Provenance generation MUST be deterministic.

---

# 21. Unsupported and Unresolved Metadata Policy

The implementation MUST NOT silently discard semantic metadata solely
because the selected parser or adapter cannot currently represent it.

The architecture MUST distinguish between:

- SUPPORTED
- UNSUPPORTED
- UNRESOLVED
- UNAVAILABLE
- INVALID

Where metadata is encountered but cannot be represented, the implementation
MUST preserve sufficient information to identify the unresolved construct
when technically possible.

The implementation MUST NOT fabricate semantic metadata to fill gaps.

The exact warning/failure policy for individual unsupported constructs MUST
be defined before implementation closure.

At minimum:

- structurally required metadata MUST cause validation failure when absent
  or invalid;
- optional unsupported metadata MUST be explicitly classified;
- silently dropping discovered semantic constructs is prohibited.

---

# 22. Validation Architecture

Validation MUST occur after canonicalization.

Validation MUST be deterministic.

At minimum, validation MUST cover:

## Identity

- duplicate canonical IDs
- invalid canonical IDs
- inconsistent source/canonical identity mapping

## References

- unresolved table references
- unresolved column references
- unresolved relationship endpoints
- unresolved hierarchy references
- unresolved partition/table references
- unresolved calculation-group references

## Structure

- malformed canonical entities
- missing required fields
- invalid relationship structure
- invalid hierarchy structure
- invalid partition ownership
- invalid calculation-group structure

## Provenance

- malformed provenance
- fabricated/invalid source references where detectable

## Serialization

- deterministic output
- schema compliance

---

# 23. Determinism

For identical semantic-model input and identical parser implementation/version,
Phase 07 MUST produce equivalent canonical output.

Output MUST NOT depend on:

- dictionary iteration accidents;
- filesystem traversal order;
- process memory addresses;
- timestamps;
- random identifiers;
- network responses.

Collections MUST have deterministic ordering where ordering is not
semantically defined by the source.

---

# 24. Serialization

Phase 07 MUST provide deterministic machine-readable serialization.

JSON is the Phase 07 external serialization format.

Serialization MUST:

- represent the canonical model;
- preserve required metadata;
- preserve unresolved/unsupported classifications;
- be deterministic;
- validate against the Phase 07 JSON Schema.

Serializer output MUST NOT expose parser-specific implementation objects.

---

# 25. JSON Schema

The file:

    schemas/phase07_metadata.schema.json

defines the externally consumable Phase 07 metadata representation.

The schema MUST evolve together with the canonical model.

Any implementation change that alters the externally represented canonical
model MUST update the schema in the same governed change.

The schema MUST NOT be reduced merely to accommodate implementation
limitations.

---

# 26. Security Boundary

Phase 07 is a metadata extraction capability.

The parser and canonicalization pipeline MUST NOT:

- require an LLM;
- execute DAX;
- execute M;
- execute arbitrary model expressions;
- make external network requests as part of normal parsing;
- execute Power BI report content;
- execute arbitrary code contained within model metadata.

DAX and M are data to be extracted/preserved, not instructions to execute.

---

# 27. Testing Requirements

Phase 07 MUST include automated tests covering at least:

## Positive Tests

- valid AdventureWorks semantic model
- tables
- columns
- measures
- calculated columns
- relationships
- available advanced metadata

## Negative Tests

- missing semantic-model directory
- malformed TMDL
- missing required metadata
- duplicate canonical identities
- unresolved references
- invalid relationship endpoints
- invalid hierarchy references
- malformed serialization input

## Identity Tests

- deterministic identity generation
- source/canonical identity separation
- repeatability

## Provenance Tests

- source file preservation
- provenance propagation
- absence of fabricated locations

## Serialization Tests

- deterministic JSON
- JSON Schema validation
- invalid-model rejection

## Regression Tests

Existing BIOrch functionality, particularly Phase 06 Tableau integration,
MUST remain protected.

---

# 28. Reference Fixture

The AdventureWorks Sales semantic model is the primary Phase 07 reference
fixture.

The fixture MUST be treated as test evidence.

The fixture MUST NOT be modified merely to make the implementation pass.

Additional fixtures MAY be introduced when the primary fixture does not
exercise a contract requirement.

Advanced features that are absent from the primary fixture MUST be tested
with dedicated fixtures before claiming full coverage.

---

# 29. Parser Selection Decision

A parser implementation MUST be selected through a governed implementation
decision.

The decision MUST document:

- parser name
- source repository/project
- exact version
- license/reuse basis where relevant
- supported runtime
- installation mechanism
- dependency declarations
- tested TMDL capabilities
- known unsupported constructs
- AdventureWorks test results
- reproducibility evidence

The historical `tmdlparser` import MUST NOT be assumed to identify the
correct implementation.

A package with the same name MUST NOT be accepted as the historical baseline
without provenance evidence.

---

# 30. Implementation Boundary

The implementation SHOULD maintain the following logical separation:

    parser/
        Parser-specific parsing

    adapter/
        Parser-to-BIOrch boundary

    canonicalizer/
        Canonical BIOrch mapping

    entities/
        Canonical data structures

    validator/
        Structural validation

    serializer/
        External representation

Parser-specific implementation details MUST NOT leak into the canonical
entity contract.

---

# 31. Phase 07 Acceptance Criteria

Phase 07 MUST NOT be considered complete until all of the following are true:

1. A reproducible parser implementation has been selected and documented.

2. All runtime parser dependencies are explicitly declared and
   reproducible.

3. The historical parser baseline is no longer required for runtime
   execution.

4. The AdventureWorks semantic model can be processed successfully.

5. Canonical identities are deterministic.

6. Source identity and canonical identity remain distinct.

7. Provenance is propagated without fabrication.

8. Relationships are represented and validated.

9. Supported advanced metadata is represented.

10. Unsupported/unresolved metadata is explicitly classified.

11. No semantic metadata is silently fabricated or silently discarded.

12. Deterministic JSON serialization is implemented.

13. Serialized output validates against `phase07_metadata.schema.json`.

14. Positive and negative tests are present.

15. Identity and provenance tests are present.

16. Existing Phase 06 regression protection remains intact.

17. The implementation performs no DAX/M execution.

18. The implementation requires no LLM or network access for normal parsing.

19. A clean-environment reproduction test succeeds.

20. The implementation, task response, validation evidence, and review
    artifacts are consistent with this contract.

---

# 32. Phase 07 Non-Goals

Phase 07 does NOT include:

- Power BI report/visual parsing;
- report layout analysis;
- visual lineage;
- DAX execution;
- M execution;
- automatic metadata repair;
- semantic-model modification;
- report modification;
- LLM-based semantic interpretation;
- network-dependent parsing.

These capabilities require future governed work if introduced.

---

# 33. Governance Relationship

This contract is the authoritative architectural requirement for Phase 07.

The governance hierarchy is:

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

`TASK.md` MUST NOT redefine or weaken this contract.

If implementation discovers a requirement conflict, implementation MUST stop
and the contract MUST be reviewed through the governance process.

Implementation MUST NOT silently reinterpret the contract.

---

# 34. Required Pre-Implementation Decisions

Before implementation begins, the following decisions MUST be resolved:

1. Parser implementation selection.
2. Parser dependency/version strategy.
3. Unsupported/unresolved metadata policy.
4. Canonical identity algorithm.
5. Provenance representation.
6. Canonical model entity structure.
7. JSON Schema representation.
8. Required advanced-metadata coverage for Phase 07 closure.

These decisions MUST be documented in the Phase 07 implementation/governance
evidence.

---

# 35. Change Control

Any change to this contract after implementation begins MUST be treated as
a governed architecture change.

The implementation MUST NOT modify the contract merely to make an existing
implementation pass validation.

Contract changes MUST include:

- reason for change;
- affected requirements;
- impact on implementation;
- impact on tests;
- impact on schema;
- impact on Phase 07 acceptance criteria.

---

# 36. Final Architectural Principle

The central architectural principle of Phase 07 is:

    The parser is replaceable.
    The BIOrch canonical contract is not.

The historical parser is evidence.

The selected parser is an implementation dependency.

The BIOrch canonical model is the stable integration boundary.

No parser-specific limitation may silently redefine the BIOrch semantic
model.

---

**PHASE_07_POWERBI_AGENT_CONTRACT_V2_AUTHORITATIVE**