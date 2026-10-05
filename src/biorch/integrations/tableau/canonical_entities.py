"""Construction of immutable V1 canonical entities from source evidence only."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
import re

from .entities import EvidenceType, SourceEvidence
from .identity import (
    ColumnIdentity,
    ColumnInstanceIdentity,
    DatasourceIdentity,
    FieldIdentity,
    IdentityRegistry,
    TableIdentity,
    WorksheetIdentity,
)


@dataclass(frozen=True)
class TableLogicalRelationship:
    """Canonical representation of a Tableau logical-layer relationship ('noodle').

    Represents a binary, context-aware semantic association between two logical
    tables within a single datasource.
    """

    canonical_id: str
    datasource_id: str
    first_table_id: str
    second_table_id: str
    expression_raw: str
    cardinality: Optional[str] = None
    source_evidence: frozenset[SourceEvidence] = field(default_factory=frozenset)


@dataclass(frozen=True)
class TableLogicalRelationshipResolutionIssue:
    """Represents a failure to resolve a relationship endpoint to a canonical Table."""

    relationship_locator: str
    datasource_id: Optional[str]
    missing_endpoint_object_id: str
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class Datasource:
    canonical_id: str
    identity: DatasourceIdentity
    name: str
    connection_class: str
    version: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class Table:
    canonical_id: str
    identity: TableIdentity
    datasource_id: str
    relation_name: str
    connection_name: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class Column:
    canonical_id: str
    identity: ColumnIdentity
    datasource_id: str
    parent_name: str
    remote_name: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class Field:
    canonical_id: str
    identity: FieldIdentity
    datasource_id: str
    field_name: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class ColumnInstance:
    canonical_id: str
    identity: ColumnInstanceIdentity
    datasource_id: str
    column_instance_name: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class Worksheet:
    canonical_id: str
    identity: WorksheetIdentity
    worksheet_name: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class ConstructionIssue:
    """Evidence that cannot form a V1 entity without guessing."""

    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class CanonicalEntities:
    datasources: tuple[Datasource, ...]
    tables: tuple[Table, ...]
    columns: tuple[Column, ...]
    fields: tuple[Field, ...]
    column_instances: tuple[ColumnInstance, ...]
    worksheets: tuple[Worksheet, ...]
    issues: tuple[ConstructionIssue, ...]


_DATASOURCE_LOCATOR = re.compile(r"^(/workbook/datasources/datasource\[\d+\])(?:/|$)")


def _required(attributes: Mapping[str, object], name: str) -> str | None:
    value = attributes.get(name)
    return value if isinstance(value, str) and value else None


def _datasource_locator(evidence: SourceEvidence) -> str | None:
    match = _DATASOURCE_LOCATOR.match(evidence.source_locator)
    return match.group(1) if match else None


def _connection_class(evidence: SourceEvidence) -> str | None:
    direct = _required(evidence.source_attributes, "class")
    if direct is not None:
        return direct
    connection = evidence.source_attributes.get("connection")
    if isinstance(connection, Mapping):
        return _required(connection, "class")
    return None


def _add_evidence(entity, evidence: SourceEvidence):
    return replace(entity, source_evidence=entity.source_evidence | frozenset({evidence}))


def construct_canonical_entities(
    evidence_items: Iterable[SourceEvidence], *, registry: IdentityRegistry | None = None
) -> CanonicalEntities:
    """Construct entities from evidence without resolving inter-entity links.

    Datasource containment is used solely to supply an entity's required
    datasource ID identity component.  No relationship object is created.
    """
    registry = registry or IdentityRegistry()
    evidence_items = tuple(evidence_items)
    issues: list[ConstructionIssue] = []
    datasources: dict[str, Datasource] = {}
    tables: dict[str, Table] = {}
    columns: dict[str, Column] = {}
    fields: dict[str, Field] = {}
    column_instances: dict[str, ColumnInstance] = {}
    worksheets: dict[str, Worksheet] = {}
    datasource_ids_by_locator: dict[str, str] = {}
    datasource_ids_by_name: dict[str, set[str]] = {}
    hyper_datasource_locators: set[str] = set()

    for evidence in evidence_items:
        if evidence.evidence_type != EvidenceType.DATASOURCE:
            continue
        name = _required(evidence.source_attributes, "name")
        connection_class = _connection_class(evidence)
        version = _required(evidence.source_attributes, "version")
        if not all((name, connection_class, version)):
            issues.append(ConstructionIssue(evidence, "missing datasource identity attribute"))
            continue
        identity = DatasourceIdentity(name, connection_class, version)
        canonical_id = registry.register(identity, source_locator=evidence.source_locator)
        datasource_ids_by_locator[evidence.source_locator] = canonical_id
        datasource_ids_by_name.setdefault(name, set()).add(canonical_id)
        entity = Datasource(canonical_id, identity, name, connection_class, version, frozenset({evidence}))
        datasources[canonical_id] = _add_evidence(datasources[canonical_id], evidence) if canonical_id in datasources else entity

    # Hyper-backed datasources expose physical columns through metadata-records
    # rather than datasource-level <column> field nodes. Detect this from the
    # direct relation connection identifier; no workbook-specific names are used.
    for evidence in evidence_items:
        if evidence.evidence_type != EvidenceType.RELATION:
            continue
        connection = _required(evidence.source_attributes, "connection")
        if connection is None or not connection.startswith("hyper."):
            continue
        locator = _datasource_locator(evidence)
        if locator is not None:
            hyper_datasource_locators.add(locator)

    for evidence in evidence_items:
        datasource_locator = _datasource_locator(evidence)
        datasource_id = datasource_ids_by_locator.get(datasource_locator or "")
        if evidence.evidence_type == EvidenceType.RELATION:
            relation_name = _required(evidence.source_attributes, "name")
            connection_name = _required(evidence.source_attributes, "connection")
            if not datasource_id or not relation_name or not connection_name:
                issues.append(ConstructionIssue(evidence, "missing table identity attribute or datasource context"))
                continue
            identity = TableIdentity(datasource_id, relation_name, connection_name)
            canonical_id = registry.register(identity, source_locator=evidence.source_locator)
            entity = Table(canonical_id, identity, datasource_id, relation_name, connection_name, frozenset({evidence}))
            tables[canonical_id] = _add_evidence(tables[canonical_id], evidence) if canonical_id in tables else entity
        elif evidence.evidence_type == EvidenceType.METADATA_RECORD and evidence.source_attributes.get("class") == "column":
            parent_name = _required(evidence.source_attributes, "parent-name")
            remote_name = _required(evidence.source_attributes, "remote-name")
            if not datasource_id or not parent_name or not remote_name:
                issues.append(ConstructionIssue(evidence, "missing column identity attribute or datasource context"))
                continue
            identity = ColumnIdentity(datasource_id, parent_name, remote_name)
            canonical_id = registry.register(identity, source_locator=evidence.source_locator)
            entity = Column(canonical_id, identity, datasource_id, parent_name, remote_name, frozenset({evidence}))
            columns[canonical_id] = _add_evidence(columns[canonical_id], evidence) if canonical_id in columns else entity
        elif evidence.source_structure == "column":
            field_name = _required(evidence.source_attributes, "name")
            if not datasource_id or not field_name:
                issues.append(ConstructionIssue(evidence, "missing field identity attribute or datasource context"))
                continue
            identity = FieldIdentity(datasource_id, field_name)
            canonical_id = registry.register(identity, source_locator=evidence.source_locator)
            entity = Field(canonical_id, identity, datasource_id, field_name, frozenset({evidence}))
            fields[canonical_id] = _add_evidence(fields[canonical_id], evidence) if canonical_id in fields else entity
        elif evidence.evidence_type == EvidenceType.COLUMN_INSTANCE:
            name = _required(evidence.source_attributes, "name")
            if not datasource_id:
                datasource_name = _required(evidence.source_attributes, "datasource")
                datasource_candidates = datasource_ids_by_name.get(datasource_name or "", set())
                if len(datasource_candidates) == 1:
                    datasource_id = next(iter(datasource_candidates))
            if not datasource_id or not name:
                issues.append(ConstructionIssue(evidence, "missing column instance identity attribute or datasource context"))
                continue
            identity = ColumnInstanceIdentity(datasource_id, name)
            canonical_id = registry.register(identity, source_locator=evidence.source_locator)
            entity = ColumnInstance(canonical_id, identity, datasource_id, name, frozenset({evidence}))
            column_instances[canonical_id] = _add_evidence(column_instances[canonical_id], evidence) if canonical_id in column_instances else entity
        elif evidence.evidence_type == EvidenceType.WORKSHEET:
            name = _required(evidence.source_attributes, "name")
            if not name:
                issues.append(ConstructionIssue(evidence, "missing worksheet identity attribute"))
                continue
            identity = WorksheetIdentity(name)
            canonical_id = registry.register(identity, source_locator=evidence.source_locator)
            entity = Worksheet(canonical_id, identity, name, frozenset({evidence}))
            worksheets[canonical_id] = _add_evidence(worksheets[canonical_id], evidence) if canonical_id in worksheets else entity

    # Hyper/extract datasources may expose physical fields only through
    # metadata-records. Build those fields after all datasource-level column
    # fields have been collected, preserving the legacy field set unchanged.
    for evidence in evidence_items:
        if (evidence.evidence_type != EvidenceType.METADATA_RECORD
                or evidence.source_attributes.get("class") != "column"
                or (_datasource_locator(evidence) or "") not in hyper_datasource_locators):
            continue
        field_name = _required(evidence.source_attributes, "local-name")
        datasource_locator = _datasource_locator(evidence)
        datasource_id = datasource_ids_by_locator.get(datasource_locator or "")
        if not datasource_id or not field_name:
            issues.append(ConstructionIssue(evidence, "missing field identity attribute or datasource context"))
            continue
        identity = FieldIdentity(datasource_id, field_name)
        canonical_id = registry.register(identity, source_locator=evidence.source_locator)
        entity = Field(canonical_id, identity, datasource_id, field_name, frozenset({evidence}))
        fields[canonical_id] = _add_evidence(fields[canonical_id], evidence) if canonical_id in fields else entity

    return CanonicalEntities(
        tuple(datasources.values()), tuple(tables.values()), tuple(columns.values()),
        tuple(fields.values()), tuple(column_instances.values()), tuple(worksheets.values()),
        tuple(issues),
    )
