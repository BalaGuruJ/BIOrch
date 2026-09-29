# Phase 06 — TabUI Integration

## Objective

Establish the foundational Tableau capability for BIOrch by implementing and validating a deterministic, read-only end-to-end Tableau metadata extraction pipeline for `.twb` workbooks.

The pipeline shall transform:

`.twb workbook → Tableau metadata extraction → CanonicalEntities → consolidated canonical JSON artifact → JSON Schema validation`

The implementation must comply with:

`contracts/tableau-agent/TABLEAU_AGENT_CONTRACT.md`

The existing Phase 06 Tableau extractor baseline shall be treated as the reference implementation to be inspected, reused, adapted, and hardened rather than discarded and independently reimplemented without justification.

---

## Scope

This task covers the Tableau metadata foundation required for future TableauAgent consumption.

The implementation shall:

1. Accept a local Tableau `.twb` workbook as input.
2. Parse the workbook deterministically and read-only.
3. Extract the metadata represented by the existing Tableau extractor baseline.
4. Construct the existing `CanonicalEntities` representation.
5. Serialize the complete canonical metadata into one consolidated JSON document.
6. Validate the generated JSON against the canonical Tableau metadata JSON schema.
7. Validate deterministic behavior.
8. Exercise the pipeline against the real Phase 06 reference workbook:

   `examples/artifacts/tableau/superstore_base.twb`

The task is limited to the Tableau metadata foundation.

---

## Reference Baseline

The existing Tableau extractor baseline is located under:

`examples/artifacts/tableau/phase6_tableau_extractor/`

The baseline currently contains the extraction/canonicalization components including:

- loader
- extraction
- canonical entities
- entity definitions
- identity handling
- relationship resolution
- validation
- writer/serialization

The implementation must first inspect these components and preserve useful validated logic.

Any substantial deviation from the baseline architecture must be documented in RESPONSE.md and justified.

---

## Canonical Metadata Model

The implementation must preserve the existing logical metadata represented by `CanonicalEntities`.

The canonical representation must retain, where applicable:

### Entities

- datasources
- tables
- columns
- fields
- column_instances
- worksheets

### Relationships

- datasource_tables
- table_columns
- column_fields
- field_column_instances
- column_instance_worksheets

### Validation / Audit Information

- validation issues
- accepted unresolved relationships or equivalent existing validation evidence

No existing metadata category may silently disappear during the JSON transition.

---

## Canonical JSON Output

JSON is the canonical persistent Tableau metadata artifact for future TableauAgent consumption.

Requirements:

1. One consolidated JSON document per workbook.
2. Explicit `schema_version`.
3. Deterministic serialization.
4. Stable ordering where required for deterministic output.
5. Complete representation of `CanonicalEntities`.
6. JSON must conform to:

   `schemas/tableau_metadata.schema.json`

7. Serialization must operate directly from the canonical Python data model.
8. pandas must not be required for serialization.
9. CSV output may remain available for compatibility/debugging, but CSV is not the canonical agent artifact.

The JSON artifact must not require downstream consumers to reconstruct the workbook metadata by joining multiple CSV files.

---

## Parser Requirements

Implement or adapt a Tableau parser boundary in the BIOrch source tree as required by the existing architecture.

The parser must:

- accept a `.twb` input path;
- operate read-only;
- deterministically extract metadata;
- reuse the existing baseline extraction logic where practical;
- produce the established canonical representation;
- avoid introducing LLM reasoning;
- avoid network access;
- avoid Tableau Server/Cloud dependencies;
- avoid `.twbx` support in this phase.

Do not create a second competing Tableau metadata model if the existing `CanonicalEntities` model already satisfies the contract.

---

## Dependency Requirements

### pandas

pandas must not be introduced or required for Tableau metadata parsing or JSON serialization.

The current baseline's pandas declaration must be reviewed and removed from the active dependency path if it is confirmed to be unused.

### tableaudocumentapi

Do not retain or introduce `tableaudocumentapi` solely because it exists in the historical baseline dependency declaration.

Before changing/removing it, inspect its actual usage.

If the extraction pipeline can operate using the existing XML/lxml path without it, the implementation should avoid making it a runtime dependency.

Any decision to retain it must be documented with concrete technical justification.

### Other Dependencies

Do not add dependencies speculatively.

Any new dependency must have a demonstrated implementation requirement and be documented.

---

## BIOrch Architecture Boundary

The Tableau metadata parser is a deterministic capability.

It must not implement:

- LLM reasoning
- agent planning
- agent routing
- capability discovery
- autonomous decision making
- workflow orchestration
- parallel execution
- Tableau Server/Cloud integration
- external network access

The parser must remain independent of the Phase 04/05 orchestration implementation.

Do not modify the Phase 05 orchestrator or AgentResolver.

ToolGateway remains the authoritative boundary for tool-mediated operations.

If the parser only operates on a local workbook path and performs no external tool operation, do not artificially introduce ToolGateway calls merely to satisfy the task.

Document the boundary explicitly.

---

## Required Implementation

Implement/adapt the following conceptual components as required by the inspected architecture:

### 1. TableauParser

Responsible for:

- accepting `.twb`;
- loading/parsing the workbook;
- invoking the existing extraction logic;
- producing canonical metadata.

### 2. TableauMetadataSerializer

Responsible for:

- converting `CanonicalEntities` to the canonical JSON representation;
- deterministic serialization;
- schema-compatible output;
- preserving all required entities, relationships, and validation information.

### 3. Integration Boundary

Provide a deterministic end-to-end path:

`.twb → parser → CanonicalEntities → JSON`

The implementation must not duplicate parsing logic unnecessarily.

---

## Reference Workbook Validation

The implementation must be exercised against:

`/home/bala2703guru/BIOrch/examples/artifacts/tableau/superstore_base.twb`

The test/investigation must verify:

- file exists;
- workbook is readable;
- workbook is valid XML/TWB input;
- parser successfully executes;
- non-empty metadata is extracted;
- canonical entities are produced;
- JSON is generated;
- JSON passes schema validation;
- expected metadata categories are represented.

Do not modify the reference `.twb`.

Generated test artifacts should be written only to controlled temporary/test output locations.

---

## Testing Requirements

Tests must cover at minimum:

### Unit Tests

- Tableau parser initialization/input validation.
- Valid `.twb` loading.
- Invalid/missing input handling.
- Canonical entity construction.
- JSON serialization.
- Deterministic serialization.
- JSON schema validation.
- Relationship serialization.
- Invalid relationship graph handling.
- No pandas dependency for serialization.

### Integration Tests

At least one integration test must exercise:

`.twb → parser → CanonicalEntities → JSON → schema validation`

using the Phase 06 reference workbook or a controlled fixture derived from it.

### Regression Tests

Existing baseline tests must continue to pass where applicable.

The existing CSV writer, if retained, must remain functional.

---

## Determinism Requirements

Repeated execution against the same `.twb` must produce logically equivalent canonical metadata and deterministic JSON output.

Where byte-level determinism is claimed, verify it explicitly.

The implementation must not depend on:

- unordered filesystem traversal;
- timestamps;
- random identifiers;
- network responses;
- nondeterministic iteration order.

---

## Acceptance Criteria

Phase 06 foundation is considered complete only when:

1. A deterministic Tableau `.twb` parser exists within the BIOrch source architecture.
2. The existing canonical metadata model is reused.
3. The complete metadata representation can be serialized to one JSON document.
4. JSON contains `schema_version`.
5. JSON conforms to `schemas/tableau_metadata.schema.json`.
6. Entity and relationship metadata are preserved.
7. The real `superstore_base.twb` successfully passes through the end-to-end pipeline.
8. The resulting metadata is non-empty and structurally valid.
9. Repeated serialization is deterministic.
10. pandas is not required by the Tableau parser/serializer.
11. No unnecessary `tableaudocumentapi` runtime dependency is introduced.
12. Existing CSV functionality remains intact if retained.
13. No Phase 05 orchestration behavior is changed.
14. No LLM-based logic is introduced.
15. No network/Server/Cloud integration is introduced.
16. All relevant tests pass.
17. No source workbook is modified.
18. All implementation deviations are documented in RESPONSE.md.

---

## Non-Goals

Explicitly out of scope:

- `.twbx` packaged workbook support
- Tableau Server integration
- Tableau Cloud integration
- publishing workbooks
- Tableau REST API integration
- LLM-based Tableau reasoning
- natural-language Tableau querying
- agent planning
- agent routing
- parallel orchestration
- modification of Phase 05
- Power BI functionality
- BI comparison functionality
- Excel/report generation
- pandas-based processing
- redesign of the BIOrch core orchestration architecture

---

## Expected Files / Areas

Expected source areas may include:

- `src/biorch/integrations/tableau/`
- existing canonical model locations if required
- Tableau-related tests

Reference/baseline artifacts:

- `examples/artifacts/tableau/phase6_tableau_extractor/`

Schema:

- `schemas/tableau_metadata.schema.json`

Reference workbook:

- `examples/artifacts/tableau/superstore_base.twb`

Do not create duplicate Tableau implementations without first explaining why the existing baseline cannot be reused.

---

## Implementation Constraints

- Read-only workbook processing.
- Deterministic behavior.
- No network access.
- No pandas.
- No speculative dependencies.
- No changes to Phase 05 orchestration.
- No modification of the source `.twb`.
- Preserve existing canonical metadata semantics.
- Preserve existing CSV compatibility where retained.
- JSON is the canonical agent-facing artifact.

---

## Required Response

Upon implementation completion, RESPONSE.md must report:

1. Files created.
2. Files modified.
3. Files deleted, if any.
4. Implementation summary.
5. Baseline components reused.
6. Tests executed.
7. Test results.
8. Reference workbook validation results.
9. JSON schema validation results.
10. Determinism validation.
11. Dependency changes.
12. Architectural decisions.
13. Known limitations.
14. Any deviations from this TASK.md.
15. Confirmation that Phase 05 orchestration was not modified.

Implementation must stop and report if a requirement cannot be satisfied without changing the contract.