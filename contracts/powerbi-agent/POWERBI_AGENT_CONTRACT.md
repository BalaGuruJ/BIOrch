# BIOrch Power BI Agent Contract

**Contract:** POWERBI_AGENT_CONTRACT  
**Version:** V1  
**Phase:** Phase 07 — PBIParser Integration  
**Status:** DRAFT — Architecture Definition  
**Capability:** Power BI Semantic Model Metadata Extraction

---

## 1. Purpose

This contract defines the architectural and behavioral boundary for the BIOrch
Power BI capability.

Phase 07 integrates Power BI Semantic Model metadata extraction into BIOrch.

The capability MUST provide deterministic extraction of Power BI Semantic Model
metadata and MUST expose the extracted metadata through the BIOrch integration
boundary.

This contract intentionally defines the capability independently of any specific
third-party TMDL parser implementation.

---

## 2. Phase 07 V1 Scope

Phase 07 V1 is limited to:

> Power BI Semantic Model metadata extraction.

The V1 input boundary is the Power BI `SemanticModel` directory.

V1 does NOT require the `.pbip` project file.

V1 does NOT extract Power BI Report/PBIR/visual metadata.

---

## 3. Explicitly Out of Scope

The following are outside Phase 07 V1:

- Power BI Report metadata
- Pages
- Visuals
- Visual configurations
- Visual-to-field bindings
- Report-level lineage
- Power BI Service APIs
- Fabric APIs
- Dataset execution
- Query execution
- DAX execution
- Power Query/M execution
- Data extraction
- Credential handling
- Authentication against Power BI services
- Cloud deployment
- LLM-based interpretation of semantic model metadata

These may be addressed by future phases/capabilities.

---

## 4. Input Contract

### 4.1 Required Input

The capability MUST accept a Power BI Semantic Model directory.

Example:

    <model>.SemanticModel/
    └── definition/
        ├── model.tmdl
        ├── relationships.tmdl
        ├── expressions.tmdl
        ├── tables/
        ├── cultures/
        └── ...

The implementation MUST NOT require the `.pbip` file for V1 extraction.

### 4.2 Input Integrity

The loader MUST:

- verify that the supplied path exists;
- verify that the expected Semantic Model structure is present;
- reject unsupported or malformed input deterministically;
- avoid silently treating an arbitrary directory as a valid Semantic Model.

---

## 5. Architectural Boundary

The implementation MUST maintain the following separation:

    SemanticModel
          |
          v
    Power BI Parser
          |
          v
    Parser Adapter
          |
          v
    BIOrch Canonical Metadata
          |
          v
    Relationship Resolution
          |
          v
    Validation
          |
          v
    Serialization
          |
          v
    Contracted Output

The third-party parser MUST NOT become the BIOrch canonical model.

Parser-specific implementation details MUST remain behind the adapter boundary.

The specific parser library MAY be replaced without requiring a redesign of
the Power BI Agent contract, provided the adapter contract remains satisfied.

---

## 6. Determinism Requirement

Semantic model extraction MUST be deterministic.

Given the same input Semantic Model and the same parser/integration version,
the implementation MUST produce semantically equivalent canonical metadata.

The extraction pipeline MUST NOT depend on:

- LLM responses;
- network calls;
- Power BI Service availability;
- nondeterministic external services;
- model-generated interpretation.

---

## 7. Canonical Metadata Scope

V1 SHOULD represent the following semantic objects when present and supported
by the source model:

### Model

- model identity;
- model metadata;
- culture information where available.

### Tables

- table identity;
- table name;
- hidden state where available;
- lineage metadata where available;
- table-level annotations where applicable.

### Columns

- column identity;
- name;
- data type;
- source column;
- hidden state;
- format metadata where available;
- summarization metadata where available;
- lineage metadata where available.

### Calculated Columns

- identity;
- name;
- DAX expression;
- relevant metadata;
- lineage metadata where available.

### Measures

- identity;
- name;
- DAX expression;
- format string where available;
- display folder where available;
- lineage metadata where available.

### Relationships

- relationship identity where available;
- source/from table;
- source/from column;
- target/to table;
- target/to column;
- cardinality;
- active/inactive state;
- cross-filtering behavior where available.

### Hierarchies

When present and reliably represented by the parser:

- hierarchy identity;
- hierarchy name;
- hierarchy levels;
- referenced columns.

### Partitions / Power Query Metadata

When present and reliably represented:

- partition identity;
- source information;
- M/Power Query expression text;
- relevant partition metadata.

### Calculation Groups

When present and reliably represented:

- calculation group identity;
- calculation items;
- calculation item expressions;
- relevant metadata.

Unsupported or unavailable metadata MUST NOT be fabricated.

---

## 8. Expression Handling

DAX and Power Query/M expressions MUST be treated as metadata.

The implementation MAY preserve expressions such as:

- measure DAX;
- calculated-column DAX;
- calculation-item DAX;
- Power Query/M expressions.

The implementation MUST NOT execute DAX or M as part of metadata extraction.

Expressions MUST be preserved as source metadata where supported.

---

## 9. Identity Model

The implementation MUST distinguish between:

1. BIOrch canonical identity;
2. Power BI source identity;
3. Power BI lineage metadata.

These concepts MUST NOT be conflated.

Where a Power BI lineage tag exists, it SHOULD be preserved as source metadata.

Canonical IDs MUST remain stable within the BIOrch representation and MUST NOT
depend exclusively on a Power BI lineage tag.

---

## 10. Provenance

Each canonical object SHOULD retain sufficient provenance to identify its source.

At minimum, provenance SHOULD identify:

- source file;
- source object/declaration where available.

Line/column ranges MAY be included when reliably exposed by the parser.

Line/column provenance is NOT a mandatory V1 requirement when the selected
parser cannot reliably provide it.

The implementation MUST NOT fabricate source locations.

---

## 11. Relationship Integrity

The integration MUST explicitly resolve relationships between canonical entities.

Examples include:

    Table -> Column
    Table -> Measure
    Relationship -> From Table
    Relationship -> From Column
    Relationship -> To Table
    Relationship -> To Column
    Hierarchy -> Level
    Hierarchy Level -> Column
    Partition -> Table
    Calculation Group -> Calculation Item

Validation MUST distinguish between:

- successfully resolved relationships;
- genuinely invalid relationships;
- unsupported source constructs;
- known, explicitly accepted unresolved metadata.

Unknown unresolved relationships MUST NOT be silently discarded.

---

## 12. Unresolved Metadata

The implementation MUST NOT use broad or unconditional exception handling to
suppress unresolved relationships.

If an unresolved relationship is intentionally accepted, the acceptance MUST:

- identify the specific condition;
- be narrowly scoped;
- be documented;
- be covered by validation tests.

A parser limitation MUST NOT automatically be classified as valid source metadata.

---

## 13. Validation

The validation layer MUST verify at minimum:

- canonical identity uniqueness;
- referenced tables exist;
- referenced columns exist;
- relationship endpoints resolve;
- hierarchy references resolve;
- calculation-group references resolve where supported;
- canonical entities are internally consistent.

Validation MUST fail deterministically when an unexpected integrity violation
is detected.

Validation rules MUST remain separate from parsing logic.

---

## 14. Serialization

The V1 implementation MUST provide a deterministic machine-readable output.

JSON is the required V1 serialization format.

The serialized representation MUST:

- represent canonical metadata;
- preserve required relationships;
- preserve applicable provenance;
- preserve supported DAX/M expressions;
- have a stable structure;
- validate against the Phase 07 JSON Schema.

CSV output is NOT required for Phase 07 V1 unless explicitly added by a later
contract revision.

---

## 15. JSON Schema

A Phase 07 JSON Schema MUST define the externally consumable serialized
representation.

The schema MUST be versioned independently from parser implementation details.

Schema validation MUST be part of the integration verification process.

---

## 16. Error Handling

The implementation MUST fail explicitly for:

- missing Semantic Model input;
- invalid Semantic Model structure;
- parser failure;
- canonicalization failure;
- unexpected relationship-resolution failure;
- serialization failure;
- schema-validation failure.

Errors MUST provide enough context to identify the failed stage.

The implementation MUST NOT silently convert fatal extraction errors into
successful empty output.

---

## 17. Agent Boundary

The Power BI Agent is responsible for orchestration of the Power BI capability.

The Agent MUST NOT contain:

- TMDL parsing logic;
- canonical entity construction logic;
- relationship-resolution algorithms;
- JSON serialization implementation.

Those responsibilities belong to the corresponding integration layers.

The Agent MAY invoke the Power BI integration capability through the approved
BIOrch tool/integration boundary.

---

## 18. LLM Boundary

The Phase 07 deterministic extraction pipeline MUST NOT require an LLM.

LLMs MUST NOT be used to:

- parse TMDL;
- invent missing metadata;
- resolve relationships through semantic guessing;
- modify extracted expressions;
- determine whether source metadata exists;
- fabricate provenance.

Future LLM-based analysis may consume the canonical Power BI metadata as a
separate capability.

---

## 19. Baseline Relationship

The existing Power BI parser located under:

    examples/artifacts/powerbi/phase7_powerbi_parser/
    powerbi_parser_baseline/

is a reference implementation/baseline.

It is NOT itself the BIOrch contract.

The baseline MAY be reused through an adapter where its behavior satisfies
this contract.

Differences between baseline behavior and this contract MUST be documented
rather than silently inherited.

The baseline MUST remain preserved as a reference artifact.

---

## 20. Reference Fixture

The AdventureWorks Sales Semantic Model is the primary Phase 07 V1 reference
fixture.

The fixture SHOULD be used to verify:

- table extraction;
- column extraction;
- measure extraction;
- relationship extraction;
- hierarchy extraction where present;
- partition/M metadata where present;
- calculation-group metadata where present;
- provenance;
- deterministic serialization;
- schema validation.

Expected counts and other factual assertions MUST be derived from the actual
reference fixture and recorded as validation evidence.

---

## 21. Testing Requirements

The implementation MUST include tests covering:

### Positive Tests

- valid Semantic Model loading;
- model extraction;
- table extraction;
- column extraction;
- measure extraction;
- relationship extraction;
- supported hierarchy extraction;
- supported partition extraction;
- supported calculation-group extraction;
- serialization;
- JSON Schema validation.

### Negative Tests

- missing input;
- invalid Semantic Model structure;
- unresolved relationship;
- invalid relationship endpoint;
- malformed source metadata;
- serialization failure where practical.

### Regression Tests

The implementation MUST verify that supported behavior does not regress when
the integration implementation changes.

---

## 22. Dependency Boundary

Phase 07 MAY introduce parser-specific dependencies required for deterministic
Semantic Model parsing.

Dependencies MUST be:

- explicitly declared;
- necessary for the implementation;
- isolated from unrelated BIOrch capabilities where practical.

No dependency may be introduced solely for LLM-based interpretation.

---

## 23. Security Boundary

The V1 parser is a metadata extraction capability.

It MUST NOT:

- execute DAX;
- execute M;
- execute arbitrary source queries;
- make external network requests as part of normal parsing;
- access Power BI credentials;
- authenticate against Power BI Service.

Source expressions are data, not executable instructions.

---

## 24. V1 Completion Criteria

Phase 07 may be considered implementation-complete only when:

1. A Semantic Model can be loaded successfully.
2. Supported semantic entities are converted into BIOrch canonical metadata.
3. Relationships are resolved and validated.
4. Unexpected unresolved relationships fail validation.
5. Supported provenance is preserved.
6. DAX/M expressions are preserved without execution.
7. Output is deterministic.
8. Output validates against the Phase 07 JSON Schema.
9. The AdventureWorks reference fixture passes the complete pipeline.
10. Tests provide evidence for both successful and failure paths.
11. The Power BI Agent boundary remains separate from parser implementation.
12. No Report/PBIR functionality is required for V1.

---

## 25. Explicit V1 Non-Goals

The following MUST NOT be added merely to increase Phase 07 scope:

- Report parsing;
- visual parsing;
- PBIR integration;
- Power BI Service integration;
- Fabric integration;
- query execution;
- DAX execution;
- M execution;
- LLM-based metadata interpretation;
- automatic repair of malformed Semantic Models.

Such capabilities require separate design decisions and contract revisions.

---

## 26. Architectural Principle

The Power BI parser is an implementation detail.

The BIOrch canonical metadata contract is the stable boundary.

Therefore:

    Power BI source format
            ↓
       Parser
            ↓
       Adapter
            ↓
    BIOrch canonical model
            ↓
       Validation
            ↓
       Serialization

must remain separable.

This permits future replacement or improvement of the underlying parser without
requiring a redesign of the BIOrch Agent architecture.

---

## 27. Contract Status

This document defines the proposed Phase 07 V1 architecture and behavioral
boundary.

Implementation MUST NOT begin until the contract has been reviewed and
approved.

Any implementation requirement that conflicts with this contract MUST be
resolved through an explicit contract revision rather than silently changing
the implementation scope.