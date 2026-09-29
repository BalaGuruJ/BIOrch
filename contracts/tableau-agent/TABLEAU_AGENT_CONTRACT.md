# Tableau Agent Contract

- Contract ID: TABLEAU_AGENT_CONTRACT
- Version: 1.0
- Status: ACTIVE
- Phase: Phase 06
- Owner: BIOrch Architecture
- Scope: Tableau workbook metadata capability
- Last Updated: 2026-09-29

---

## 1. Purpose

This contract defines the architectural boundary between BIOrch and the
Tableau Agent capability.

The Tableau Agent is responsible for accepting a Tableau workbook artifact,
extracting and normalizing its metadata, and exposing that metadata through a
stable, machine-readable representation that can subsequently be consumed by
the BIOrch orchestration layer and future Tableau analysis workflows.

The contract establishes the externally observable behavior and boundaries of
the Tableau capability.

It does not prescribe a specific Tableau parsing library or internal parsing
algorithm.

---

## 2. Architectural Position

The Tableau capability operates as a specialized agent capability within
BIOrch.

The intended high-level flow is:

    Tableau Workbook (.twb)
            |
            v
    Tableau Metadata Parser
            |
            v
    Canonical Metadata Model
      (CanonicalEntities)
            |
            v
    Validated JSON Metadata Artifact
            |
            v
       Tableau Agent
            |
            v
       BIOrch Orchestrator

The parser and metadata extraction implementation remain internal to the
Tableau capability.

The canonical metadata representation is the boundary consumed by downstream
Tableau Agent functionality.

---

## 3. Supported Input

### 3.1 Primary Input

The primary supported input is a Tableau workbook definition file:

    .twb

The implementation must treat the supplied workbook path as an explicit input
and must not rely on a hard-coded workbook location in production code.

### 3.2 Future Input

Support for packaged Tableau workbooks:

    .twbx

may be introduced in a future phase.

`.twbx` support is NOT required by the Phase 06 contract unless explicitly
added to a subsequent task.

---

## 4. Input Safety

The Tableau capability must:

1. Read the supplied workbook.
2. Not modify the source workbook.
3. Not modify unrelated project files.
4. Not execute arbitrary content contained in the workbook.
5. Treat workbook content as untrusted input.
6. Operate within the BIOrch tool/security boundaries.

The Tableau capability must not bypass the ToolGateway or other established
BIOrch security boundaries.

---

## 5. Metadata Extraction Boundary

The Tableau parser is responsible for extracting metadata from the workbook.

The extraction layer may identify, where present:

- Workbooks
- Datasources
- Tables / relations
- Physical columns
- Logical fields
- Column instances
- Worksheets
- Relationships
- Worksheet-to-column usage
- Other metadata explicitly supported by the canonical model

The parser must not invent metadata that is not supported by the source
workbook or by the canonical model.

Parser implementation details are intentionally not fixed by this contract.

The implementation may use:

- XML parsing
- Tableau-specific libraries
- Python standard libraries
- Other approved deterministic parsing mechanisms

provided that the externally observable contract remains satisfied.

---

## 6. Canonical Metadata Model

The Tableau capability must normalize extracted metadata into the existing
BIOrch canonical metadata representation.

The canonical model is represented by `CanonicalEntities` and its associated
entity and relationship structures.

The canonical representation must preserve the identity and relationships
necessary to describe the extracted Tableau metadata.

The following logical entity categories are currently part of the Phase 06
baseline:

- Datasources
- Tables
- Columns
- Fields
- Column instances
- Worksheets

The following logical relationship categories are currently part of the
Phase 06 baseline:

- Datasource → Table
- Table → Column
- Column → Field
- Field → Column Instance
- Column Instance → Worksheet

Additional metadata may be added through an explicitly approved contract
change or future phase.

---

## 7. Canonical JSON Artifact

The canonical persistent output of the Tableau metadata extraction pipeline
is a single JSON metadata artifact.

The JSON artifact must:

1. Represent the complete canonical metadata graph produced by the parser.
2. Preserve entity records.
3. Preserve relationship records.
4. Preserve validation information where applicable.
5. Include an explicit schema version.
6. Be deterministic for the same canonical input.
7. Be machine-readable without requiring pandas.
8. Be independently schema-validatable.

The JSON artifact is governed by:

    schemas/tableau_metadata.schema.json

The JSON schema is a data-format contract supporting this architectural
contract. It does not replace this Tableau Agent architectural contract.

---

## 8. JSON Output Structure

The canonical JSON artifact follows this logical structure:

    {
      "schema_version": "...",
      "workbook_metadata": {
        "entities": {
          "datasources": [],
          "tables": [],
          "columns": [],
          "fields": [],
          "column_instances": [],
          "worksheets": []
        },
        "relationships": {
          "datasource_tables": [],
          "table_columns": [],
          "column_fields": [],
          "field_column_instances": [],
          "column_instance_worksheets": []
        },
        "validation": {
          "issues": [],
          "accepted_unresolved": []
        }
      }
    }

The exact field-level structure is governed by
`schemas/tableau_metadata.schema.json` and the canonical entity definitions.

---

## 9. Validation Requirements

Before a canonical JSON artifact is considered valid:

1. Canonical relationship validation must succeed.
2. The generated JSON must validate against
   `schemas/tableau_metadata.schema.json`.
3. Invalid relationship graphs must result in a deterministic validation
   failure.
4. The serializer must not silently discard canonical metadata.
5. Serialization must be deterministic.

Validation must use the existing BIOrch validation mechanisms wherever
applicable rather than introducing an unrelated validation system.

---

## 10. Serialization Requirements

The JSON serializer must:

- Serialize directly from the canonical metadata model.
- Not require pandas.
- Preserve supported dataclass values.
- Preserve supported enum values.
- Preserve supported set/frozenset values.
- Preserve supported immutable mapping values.
- Produce deterministic output.
- Remain independent of the TableauAgent reasoning layer.

The serializer must not become responsible for parsing Tableau workbooks.

---

## 11. CSV Compatibility

The existing CSV writer may remain available for:

- debugging
- investigation
- regression comparison
- legacy compatibility
- development

However:

**JSON is the canonical Phase 06 agent-facing metadata artifact.**

CSV is not the authoritative downstream Tableau Agent representation.

Removal or deprecation of CSV output requires a separate approved change.

---

## 12. Tableau Agent Boundary

The Tableau Agent may consume the canonical JSON metadata artifact.

The Tableau Agent may use the metadata to answer or support future questions
about Tableau workbook structure, including where supported:

- datasource structure
- table structure
- field structure
- worksheet structure
- metadata relationships
- lineage
- worksheet-to-field usage

The Tableau Agent must not modify the canonical metadata artifact as part
of ordinary metadata consumption.

Agent reasoning must remain separate from deterministic metadata extraction.

---

## 13. Determinism

Phase 06 metadata extraction and serialization must be deterministic.

For the same:

- input workbook
- parser configuration
- canonical model

the resulting canonical metadata representation must be equivalent.

LLM-based interpretation is not part of the Phase 06 extraction boundary.

---

## 14. LLM Boundary

LLM-based routing, planning, interpretation, summarization, or reasoning is
NOT required for Tableau metadata extraction.

The Tableau parser must remain deterministic.

Future LLM-based Tableau Agent behavior may consume the canonical metadata
artifact but must not alter the deterministic extraction contract.

---

## 15. ToolGateway Boundary

The Tableau Agent must respect the existing BIOrch ToolGateway contract.

The Tableau capability must not:

- bypass ToolGateway controls
- directly execute arbitrary external tools
- introduce unrestricted filesystem access
- introduce unrestricted network access
- weaken existing authorization or security boundaries

Any future Tableau-specific tool access must be introduced through the
existing BIOrch tool architecture.

---

## 16. Error Semantics

The Tableau capability must fail deterministically for conditions including:

- missing input workbook
- unreadable input workbook
- malformed/unsupported workbook structure
- metadata extraction failure
- canonical relationship validation failure
- JSON schema validation failure

Errors must not be silently converted into successful metadata output.

The exact exception hierarchy may remain an implementation concern unless
explicitly promoted to an architectural contract.

---

## 17. Read-Only Requirement

Phase 06 metadata extraction is read-only with respect to the source
workbook.

The parser must not:

- edit the `.twb`
- rewrite the workbook
- modify workbook XML
- publish the workbook
- alter Tableau Server/Cloud state

Generated metadata artifacts are outputs of the extraction process and do
not constitute modifications to the source workbook.

---

## 18. Dependency Boundary

The contract does not require a specific Tableau parsing dependency.

A dependency may be used if it:

1. Supports the required workbook input.
2. Operates within the project environment.
3. Does not violate BIOrch security boundaries.
4. Produces metadata compatible with the canonical model.
5. Does not introduce unnecessary coupling to the agent layer.

Dependency selection is an implementation decision unless promoted to a
separate architecture decision.

---

## 19. Phase 06 Scope

Phase 06 establishes the foundational Tableau capability.

In scope:

- Tableau workbook metadata ingestion
- Deterministic metadata extraction
- Canonical metadata construction
- Relationship resolution
- Metadata validation
- Canonical JSON serialization
- JSON schema validation
- Tableau Agent integration boundary

---

## 20. Phase 06 Non-Goals

The following are explicitly outside the Phase 06 contract unless separately
approved:

- LLM-based Tableau reasoning
- LLM-based metadata extraction
- Dynamic agent discovery
- Parallel orchestration
- Multi-workbook comparison
- Power BI parsing
- Tableau Server/Cloud publishing
- Workbook modification
- Automatic dashboard generation
- Natural-language visualization generation
- Autonomous Tableau actions
- External web crawling
- Arbitrary network access
- Replacing the BIOrch ToolGateway
- Removing CSV support

---

## 21. Backward Compatibility

Phase 06 must not break the established BIOrch contracts from earlier
phases.

In particular:

- Agent contracts remain unchanged.
- Orchestrator contracts remain unchanged.
- ToolGateway contracts remain unchanged.
- Existing deterministic orchestration behavior remains unchanged.
- Existing canonical models must not be casually rewritten to accommodate
  Tableau-specific behavior.

Any required breaking change must be introduced through an explicit contract
revision.

---

## 22. Contract Change Policy

Changes to this contract require:

1. Explicit identification of the affected contract section.
2. A documented reason for the change.
3. Review of downstream impact.
4. An updated contract version.
5. A corresponding implementation task.
6. Independent review before closure.

Implementation must not silently redefine this contract.

---

## 23. Acceptance Boundary

Phase 06 Tableau capability is considered contract-compliant only when the
following can be demonstrated:

    .twb
      ↓
    deterministic extraction
      ↓
    CanonicalEntities
      ↓
    relationship validation
      ↓
    canonical JSON
      ↓
    JSON Schema validation
      ↓
    Tableau Agent-consumable metadata

The implementation must provide evidence for each applicable stage.

A serializer-only test does not constitute proof of end-to-end Tableau
workbook extraction.

---

## 24. Current Phase 06 Baseline

The current Phase 06 implementation baseline contains:

- Tableau `.twb` sample workbook
- Tableau metadata extractor implementation
- Canonical entity model
- Relationship resolution
- Validation
- CSV writer
- JSON writer
- JSON schema
- Serialization tests

The real `.twb → CanonicalEntities → JSON` execution path remains an
implementation validation milestone.

---

## 25. Contract Status

This contract is authoritative for Phase 06 Tableau Agent capability
development.

Implementation tasks must derive their scope from this contract.

Where an implementation task conflicts with this contract, the contract
takes precedence unless the contract is explicitly revised and approved.