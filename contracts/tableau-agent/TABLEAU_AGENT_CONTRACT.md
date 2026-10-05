# Tableau Agent Contract

- Contract ID: TABLEAU_AGENT_CONTRACT
- Version: 1.1
- Status: ACTIVE
- Phase: Phase 06 Baseline / Phase 11 Extension
- Owner: BIOrch Architecture
- Scope: Tableau workbook metadata capability (including Logical Layer Data Model Relationships)
- Last Updated: 2026-10-05
- Reference: BIORCH-ARCH-TABLEAU-LOGICAL-RELATIONSHIPS-001

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

`.twbx` support is NOT required by the baseline contract unless explicitly
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
- Relationships (vertical lineage and horizontal logical relationships)
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

The following canonical entity categories are part of the Tableau capability:

- Datasources
- Tables
- Columns
- Fields
- Column instances
- Worksheets

The following vertical lineage relationship categories are part of the
Phase 06 baseline:

- Datasource → Table
- Table → Column
- Column → Field
- Field → Column Instance
- Column Instance → Worksheet

The following horizontal logical-layer relationship category is governed by
this contract (extended per `BIORCH-ARCH-TABLEAU-LOGICAL-RELATIONSHIPS-001`):

- Logical Table ↔ Logical Table (Logical "Noodle" Relationship)

---

## 6.1 Tableau Logical Relationships Specification

Modern Tableau workbooks (Tableau 2020.2+ Object Model) introduce a dual-layer
architecture consisting of an underlying physical layer and a top-level logical
data model. The logical layer defines flexible, context-aware relationships
between logical tables ("noodles") that are evaluated dynamically at query time
based on visual level of detail (LOD).

This specification governs the representation of Tableau logical relationships.

### 6.1.1 Relationship Concept & Architectural Tier

To preserve architectural clarity, Tableau relationships are strictly
categorized into three tiers:

1. **Tier A: Vertical Lineage / Containment (Baseline)**
   Datasource → Table → Column → Field → ColumnInstance → Worksheet.
   Describes provenance, visual usage, and hierarchical structure.
2. **Tier B: Logical Relationships ("Noodles" — This Specification)**
   Horizontal multi-table semantic associations declared in `.twb` XML under
   `<object-graph><relationships><relationship>`.
3. **Tier C: Physical Joins & Custom SQL (Out of Scope)**
   Intra-table physical joins (`<relation type='join'>`) and custom SQL
   (`<relation type='text'>`) encapsulated inside physical table objects.
   Physical joins statically combine relations prior to the logical layer.

### 6.1.2 Endpoint Model

- Logical relationships are **binary** and **non-directional**.
- Endpoints are named neutrally: `first_table_id` and `second_table_id`.
- Directional naming (such as `left_table_id` / `right_table_id`) is forbidden
  to prevent false conflation with asymmetric SQL join semantics.
- Each endpoint maps to an existing canonical `Table` entity within the same
  enclosing datasource.

### 6.1.3 Commutative Semantic Identity & Canonical ID

- Logical relationships possess a commutative semantic identity:
  ```python
  LogicalRelationshipIdentity(datasource_id, table_a_id, table_b_id)
  ```
- Commutativity is enforced by lexicographical ordering of the endpoint table IDs:
  $$\text{identity\_tuple} = (\text{datasource\_id}, \min(T_1, T_2), \max(T_1, T_2))$$
- In Tableau, at most one logical relationship exists between any pair of
  logical tables within a datasource. The XML serialization order of endpoints
  (`<first-end-point>` vs `<second-end-point>`) MUST NOT alter the canonical ID.
- The canonical ID is generated deterministically using the standard registry:
  $$\text{canonical\_id} = \text{canonical\_id\_for}(\text{LogicalRelationshipIdentity}(\text{datasource\_id}, T_1, T_2))$$

### 6.1.4 Opaque Expression Rule

- The `<expression>` element within `<relationship>` defines the relationship
  join conditions.
- The entire `<expression>` subtree MUST be captured and preserved as opaque
  source data in the field `expression_raw`.
- **Deterministic Serialization:** `expression_raw` MUST be produced using
  canonical XML formatting (e.g., C14N2 or normalized attribute ordering with
  surrounding whitespace trimmed) to guarantee byte-for-byte determinism.
- **No AST / Semantic Evaluation:** The extraction and canonical layers MUST NOT
  perform AST traversal, SQL operator evaluation, or column-pair decomposition
  in this phase.

### 6.1.5 Object-to-Table Resolution Rules

In `.twb` XML, relationship endpoints reference `<object id="...">` tags,
whereas the canonical model represents tables as `Table` entities constructed
from underlying `<relation>` tags. Resolution MUST proceed through the
following deterministic steps:

1. **Extraction Mapping:** Extraction records the mapping:
   $$\text{object\_id} \longmapsto \text{source\_locator of enclosed root relation}$$
2. **Table Lookup:** For each endpoint (`first-end-point/@object-id` and
   `second-end-point/@object-id`), lookup the canonical `Table` whose
   `source_evidence` contains the relation at that locator.
3. **Datasource Boundary Validation:** Both resolved tables MUST belong to the
   same `datasource_id` enclosing the relationship.
4. **Deterministic Issue Generation:**
   - If an `object-id` fails to match an `<object>` entry: emit
     `TableLogicalRelationshipResolutionIssue("referenced object-id not found")`.
   - If an underlying relation was not constructed into a canonical table: emit
     `TableLogicalRelationshipResolutionIssue("underlying relation not constructed as table")`.
   - If endpoints span across distinct datasources: emit
     `TableLogicalRelationshipResolutionIssue("cross-datasource logical relationship not permitted")`.
   - Unresolved relationships MUST NEVER be silently discarded.

### 6.1.6 Optional Cardinality & Performance Options

- Where explicitly present in source XML attributes (e.g., `cardinality`,
  `assume-referential-integrity`), cardinality metadata may be captured in an
  optional `cardinality: Optional[str] = None` field.
- When omitted from the source, `cardinality` defaults to `None`.

### 6.1.7 Scope Boundaries

- **IN SCOPE:**
  - Parsing `<relationship>` nodes under `<object-graph><relationships>`.
  - Binary, non-directional Table-to-Table logical relationships.
  - Commutative identity hashing and deterministic SHA-256 canonical ID generation.
  - Opaque, lossless XML preservation of `<expression>` (`expression_raw`).
  - Optional cardinality capture.
  - Deterministic resolution issue reporting.
  - Parity across JSON and CSV serialization.
- **OUT OF SCOPE:**
  - Expression AST decomposition (no foreign-key column pairs extracted in this phase).
  - Physical join trees (`<relation type='join'>`) inside an `<object>`.
  - Custom SQL parsing (`<relation type='text'>`) inside an `<object>`.
  - Multi-table physical decomposition when an `<object>` encapsulates joined relations.
  - Cross-datasource blending (`<blend-relationships>`).
  - Semantic equivalence assertions or business logic inference.

---

## 7. Canonical JSON Artifact

The canonical persistent output of the Tableau metadata extraction pipeline
is a single JSON metadata artifact.

The JSON artifact must:

1. Represent the complete canonical metadata graph produced by the parser.
2. Preserve entity records.
3. Preserve relationship records (both vertical lineage and logical relationships).
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
          "column_instance_worksheets": [],
          "logical_relationships": []
        },
        "validation": {
          "issues": [],
          "accepted_unresolved": []
        }
      }
    }

Each entry in `logical_relationships` contains:

- `canonical_id` (string, required): Deterministic SHA-256 identifier.
- `datasource_id` (string, required): Enclosing canonical datasource identifier.
- `first_table_id` (string, required): Canonical table ID of the first endpoint.
- `second_table_id` (string, required): Canonical table ID of the second endpoint.
- `expression_raw` (string, required): Canonicalized, opaque C14N XML string of `<expression>`.
- `cardinality` (string or null, optional): Cardinality metadata if present.

The exact field-level structure is governed by
`schemas/tableau_metadata.schema.json` and the canonical entity definitions.

---

## 9. Validation Requirements

Before a canonical JSON artifact is considered valid:

1. Canonical relationship validation must succeed:
   - All vertical lineage relationships must satisfy existing grain and foreign-key checks.
   - For every `TableLogicalRelationship`:
     - `first_table_id` and `second_table_id` must exist in `entities.tables`.
     - Both tables must belong to the specified `datasource_id`.
     - `first_table_id != second_table_id` (self-referential relationships are rejected).
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

When logical relationships are present, the CSV writer may export:

    table_logical_relationships.csv

containing: `(relationship_id, datasource_id, first_table_id, second_table_id, cardinality)`.

However:

**JSON is the canonical agent-facing metadata artifact.**

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
- metadata relationships (vertical lineage and logical table associations)
- lineage
- worksheet-to-field usage

The Tableau Agent must not modify the canonical metadata artifact as part
of ordinary metadata consumption.

Agent reasoning must remain separate from deterministic metadata extraction.

---

## 13. Determinism

Metadata extraction and serialization must be deterministic.

For the same:

- input workbook
- parser configuration
- canonical model

the resulting canonical metadata representation must be equivalent.

LLM-based interpretation is not part of the extraction boundary.

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

Metadata extraction is read-only with respect to the source workbook.

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

## 19. Scope

In scope:

- Tableau workbook metadata ingestion
- Deterministic metadata extraction
- Canonical metadata construction (entities, vertical lineage, and logical relationships)
- Relationship resolution
- Metadata validation
- Canonical JSON serialization
- JSON schema validation
- Tableau Agent integration boundary

---

## 20. Non-Goals

The following are explicitly outside the contract unless separately
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
- Physical join tree parsing (`<relation type='join'>`)
- Custom SQL statement parsing (`<relation type='text'>`)
- Relationship expression AST evaluation or foreign-key pair extraction
- Cross-datasource data blending (`<blend-relationships>`)
- Semantic equivalence inference between Tableau and other BI platforms

---

## 21. Backward Compatibility

This contract preserves backward compatibility with earlier phases.

In particular:

- Agent contracts remain unchanged.
- Orchestrator contracts remain unchanged.
- ToolGateway contracts remain unchanged.
- Existing deterministic orchestration behavior remains unchanged.
- Existing vertical lineage canonical models and CSV datasets remain intact.
- Workbooks without logical relationships (e.g., pre-2020.2 workbooks) produce
  an empty `logical_relationships: []` list without validation failure.

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

Tableau capability is considered contract-compliant only when the
following can be demonstrated:

    .twb
      ↓
    deterministic extraction (entities + vertical lineage + logical relationships)
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

## 24. Current Baseline

The current implementation baseline contains:

- Tableau `.twb` sample workbook (`superstore_base.twb`)
- Tableau metadata extractor implementation
- Canonical entity model
- Vertical lineage relationship resolution
- Validation
- CSV writer
- JSON writer
- JSON schema
- Serialization tests

Implementation of logical relationships remains a future implementation
milestone governed by this contract.

---

## 25. Contract Status

This contract is authoritative for Tableau Agent capability development.

Implementation tasks must derive their scope from this contract.

Where an implementation task conflicts with this contract, the contract
takes precedence unless the contract is explicitly revised and approved.

---

## 26. Phase 11 Downstream Compatibility

This section governs the consumption of Tableau logical relationships by
downstream Phase 11 Cross-Platform Comparison workflows:

1. **Table-Grain Relationship Comparison:**
   Because Tableau logical relationships preserve `<expression>` as an opaque
   payload (`expression_raw`), Phase 11 comparison is authorized to compare
   relationships at the **Table-Pair Grain**:
   $$\text{Relationship Key} = \text{TableA} \longleftrightarrow \text{TableB}$$
2. **Column-Grain Comparison Deferral:**
   Downstream comparison agents MUST NOT fail or halt due to the absence of
   decomposed foreign-key column pairs. Column-grain comparison is marked as
   `OPAQUE_EXPRESSION_EVALUATION_DEFERRED` until a future approved contract
   revision introduces expression parsing.
3. **No Semantic Equivalence:**
   Matching Table-Pair keys indicates structural correspondence only and
   MUST NOT be interpreted as data, metric, or calculation equivalence.

---

## 27. Revision History

- **Version 1.0 (2026-09-29):** Initial Phase 06 baseline contract defining
  entities, vertical lineage, and JSON serialization.
- **Version 1.1 (2026-10-05):** Extended with Tableau Logical Data Model
  Relationship ("noodle") capability pursuant to frozen architectural design
  `BIORCH-ARCH-TABLEAU-LOGICAL-RELATIONSHIPS-001`. Added Section 6.1, updated
  JSON output structure (Section 8), validation rules (Section 9), non-goals
  (Section 20), and downstream Phase 11 comparison compatibility (Section 26).
