"""Direct XML-backed resolution for the V1 Datasource-to-Table relationship."""

from __future__ import annotations

from dataclasses import dataclass, replace

from collections.abc import Mapping

from .canonical_entities import (
    CanonicalEntities, Column, Datasource, Table, Worksheet,
    TableLogicalRelationship, TableLogicalRelationshipResolutionIssue
)
from .entities import DerivationStatus, EvidenceType, SourceEvidence

# ... (rest of the file content) ...


@dataclass(frozen=True)
class DatasourceTableRelationship:
    """A canonical Datasource → Table edge backed by relation observations."""

    datasource_id: str
    table_id: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class DatasourceTableResolutionIssue:
    """A relation observation that cannot establish one datasource endpoint."""

    table_id: str | None
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class DatasourceTableResolution:
    relationships: tuple[DatasourceTableRelationship, ...]
    issues: tuple[DatasourceTableResolutionIssue, ...]


@dataclass(frozen=True)
class TableColumnRelationship:
    """A canonical Table → Column edge backed by relation column evidence."""

    table_id: str
    column_id: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class TableColumnResolutionIssue:
    """Relation evidence that cannot establish one canonical column endpoint."""

    table_id: str
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class TableColumnResolution:
    relationships: tuple[TableColumnRelationship, ...]
    issues: tuple[TableColumnResolutionIssue, ...]


@dataclass(frozen=True)
class FieldColumnInstanceRelationship:
    """A canonical Field → Column Instance edge backed by XML ``@column``."""

    field_id: str
    column_instance_id: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class FieldColumnInstanceResolutionIssue:
    """Column-instance evidence that cannot establish one canonical field."""

    column_instance_id: str | None
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class FieldColumnInstanceResolution:
    relationships: tuple[FieldColumnInstanceRelationship, ...]
    issues: tuple[FieldColumnInstanceResolutionIssue, ...]


@dataclass(frozen=True)
class ColumnInstanceWorksheetRelationship:
    column_instance_id: str
    worksheet_id: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class ColumnInstanceWorksheetResolutionIssue:
    column_instance_id: str | None
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class ColumnInstanceWorksheetResolution:
    relationships: tuple[ColumnInstanceWorksheetRelationship, ...]
    issues: tuple[ColumnInstanceWorksheetResolutionIssue, ...]


@dataclass(frozen=True)
class ColumnFieldRelationship:
    column_id: str
    field_id: str
    source_evidence: frozenset[SourceEvidence]


@dataclass(frozen=True)
class ColumnFieldResolutionIssue:
    column_id: str | None
    evidence: SourceEvidence
    reason: str


@dataclass(frozen=True)
class ColumnFieldResolution:
    relationships: tuple[ColumnFieldRelationship, ...]
    issues: tuple[ColumnFieldResolutionIssue, ...]


def _enclosing_datasource_ids(
    evidence: SourceEvidence, datasources: tuple[Datasource, ...]
) -> set[str]:
    """Find datasource entities whose XML evidence encloses an observation."""
    return {
        datasource.canonical_id
        for datasource in datasources
        for datasource_evidence in datasource.source_evidence
        if evidence.source_locator.startswith(datasource_evidence.source_locator + "/")
    }


def _add_evidence(
    relationship: DatasourceTableRelationship, evidence: SourceEvidence
) -> DatasourceTableRelationship:
    return replace(
        relationship,
        source_evidence=relationship.source_evidence | frozenset({evidence}),
    )


def _relation_remote_names(evidence: SourceEvidence) -> tuple[str, ...]:
    """Read remote column names preserved beneath one relation observation."""
    columns = evidence.source_attributes.get("columns")
    if not isinstance(columns, Mapping):
        return ()
    column_data = columns.get("column")
    if isinstance(column_data, Mapping):
        column_data = (column_data,)
    if not isinstance(column_data, tuple):
        return ()
    return tuple(
        name
        for column in column_data
        if isinstance(column, Mapping)
        for name in (column.get("name"),)
        if isinstance(name, str) and name
    )


def _add_table_column_evidence(
    relationship: TableColumnRelationship, evidence: SourceEvidence
) -> TableColumnRelationship:
    return replace(
        relationship,
        source_evidence=relationship.source_evidence | frozenset({evidence}),
    )


def _add_field_column_instance_evidence(
    relationship: FieldColumnInstanceRelationship, evidence: SourceEvidence
) -> FieldColumnInstanceRelationship:
    return replace(
        relationship,
        source_evidence=relationship.source_evidence | frozenset({evidence}),
    )


def _is_direct_xml(evidence: SourceEvidence) -> bool:
    return (
        evidence.representation == "xml"
        and evidence.derivation_status == DerivationStatus.DIRECT
    )


def _evidence_order_key(evidence: SourceEvidence) -> tuple[str, str, str, str, str, str]:
    """Order evidence without relying on a set's iteration order."""
    column = evidence.source_attributes.get("column")
    name = evidence.source_attributes.get("name")
    return (
        evidence.source_file,
        evidence.representation,
        evidence.source_structure,
        evidence.source_locator,
        column if isinstance(column, str) else "",
        name if isinstance(name, str) else "",
    )


def _enclosing_worksheet_ids(
    evidence: SourceEvidence, worksheets: tuple[Worksheet, ...]
) -> set[str]:
    return {
        worksheet.canonical_id
        for worksheet in worksheets
        for worksheet_evidence in worksheet.source_evidence
        if evidence.source_locator.startswith(worksheet_evidence.source_locator + "/")
    }


def _add_relationship_evidence(relationship, evidence: SourceEvidence):
    return replace(
        relationship,
        source_evidence=relationship.source_evidence | frozenset({evidence}),
    )


def resolve_datasource_to_table(
    entities: CanonicalEntities,
) -> DatasourceTableResolution:
    """Resolve only direct, XML-contained Datasource → Table relationships.

    A relation observation must be enclosed by exactly one canonical
    datasource's source evidence, and that datasource must equal the table's
    established datasource ID.  No name-based fallback is used.
    """
    relationships: dict[tuple[str, str], DatasourceTableRelationship] = {}
    issues: list[DatasourceTableResolutionIssue] = []

    for table in entities.tables:
        for evidence in table.source_evidence:
            if evidence.evidence_type != EvidenceType.RELATION:
                continue
            datasource_ids = _enclosing_datasource_ids(evidence, entities.datasources)
            if len(datasource_ids) != 1:
                issues.append(
                    DatasourceTableResolutionIssue(
                        table.canonical_id,
                        evidence,
                        "relation evidence has no unique enclosing datasource",
                    )
                )
                continue
            datasource_id = next(iter(datasource_ids))
            if datasource_id != table.datasource_id:
                issues.append(
                    DatasourceTableResolutionIssue(
                        table.canonical_id,
                        evidence,
                        "enclosing datasource conflicts with table identity",
                    )
                )
                continue
            key = (datasource_id, table.canonical_id)
            relationship = DatasourceTableRelationship(
                datasource_id, table.canonical_id, frozenset({evidence})
            )
            relationships[key] = (
                _add_evidence(relationships[key], evidence)
                if key in relationships
                else relationship
            )

    for construction_issue in entities.issues:
        evidence = construction_issue.evidence
        if evidence.evidence_type == EvidenceType.RELATION:
            issues.append(
                DatasourceTableResolutionIssue(
                    None,
                    evidence,
                    f"table was not constructed: {construction_issue.reason}",
                )
            )

    return DatasourceTableResolution(tuple(relationships.values()), tuple(issues))


def resolve_table_to_column(entities: CanonicalEntities) -> TableColumnResolution:
    """Resolve direct physical Table → Column relationships from XML evidence.

    Legacy datasources list remote column names beneath the relation itself.
    Hyper/extract datasources instead expose the same physical-column evidence
    as sibling metadata-records. Both paths require exact datasource, parent-name,
    and remote-name matches; no name-only or heuristic fallback is used.
    """
    relationships: dict[tuple[str, str], TableColumnRelationship] = {}
    issues: list[TableColumnResolutionIssue] = []

    for table in entities.tables:
        expected_parent_name = f"[{table.relation_name}]"
        relation_evidence = tuple(
            evidence for evidence in table.source_evidence
            if evidence.evidence_type == EvidenceType.RELATION
        )

        for evidence in relation_evidence:
            if (
                evidence.source_attributes.get("name") != table.relation_name
                or evidence.source_attributes.get("connection") != table.connection_name
            ):
                issues.append(TableColumnResolutionIssue(
                    table.canonical_id, evidence,
                    "relation evidence conflicts with table identity",
                ))
                continue

            remote_names = _relation_remote_names(evidence)
            if remote_names:
                observations = ((remote_name, evidence) for remote_name in remote_names)
            else:
                # Hyper relations do not carry column observations. Use only
                # metadata-record column evidence whose parent identifies this
                # exact table and whose datasource is the table's datasource.
                metadata_observations = []
                for column in entities.columns:
                    if column.datasource_id != table.datasource_id or column.parent_name != expected_parent_name:
                        continue
                    for column_evidence in column.source_evidence:
                        if (column_evidence.evidence_type == EvidenceType.METADATA_RECORD
                                and column_evidence.source_attributes.get("class") == "column"
                                and column_evidence.source_attributes.get("remote-name") == column.remote_name):
                            metadata_observations.append((column.remote_name, column_evidence))
                if not metadata_observations:
                    issues.append(TableColumnResolutionIssue(
                        table.canonical_id, evidence,
                        "relation evidence contains no supported column observations",
                    ))
                    continue
                observations = tuple(metadata_observations)

            for remote_name, observation_evidence in observations:
                candidates = tuple(
                    column
                    for column in entities.columns
                    if column.datasource_id == table.datasource_id
                    and column.parent_name == expected_parent_name
                    and column.remote_name == remote_name
                )
                if len(candidates) != 1:
                    issues.append(TableColumnResolutionIssue(
                        table.canonical_id, observation_evidence,
                        f"relation column {remote_name!r} has no unique canonical column",
                    ))
                    continue
                column = candidates[0]
                key = (table.canonical_id, column.canonical_id)
                relationship = TableColumnRelationship(
                    table.canonical_id, column.canonical_id, frozenset({observation_evidence})
                )
                relationships[key] = (
                    _add_table_column_evidence(relationships[key], observation_evidence)
                    if key in relationships else relationship
                )

    return TableColumnResolution(
        tuple(relationships[key] for key in sorted(relationships)),
        tuple(sorted(issues, key=lambda issue: (
            issue.table_id, _evidence_order_key(issue.evidence), issue.reason,
        ))),
    )

def resolve_field_to_column_instance(
    entities: CanonicalEntities,
) -> FieldColumnInstanceResolution:
    """Resolve Field → Column Instance only from direct XML ``column-instance/@column``.

    The XML ``@column`` value is matched exactly to a canonical Field's
    ``field_name`` within the datasource that directly encloses the
    column-instance evidence.  No display-name, caption, normalized-name, or
    global fallback is used.
    """
    relationships: dict[tuple[str, str], FieldColumnInstanceRelationship] = {}
    issues: list[FieldColumnInstanceResolutionIssue] = []

    fields_by_datasource_and_name: dict[tuple[str, str], tuple] = {}
    field_groups: dict[tuple[str, str], list] = {}
    for field in entities.fields:
        if any(
            _is_direct_xml(evidence) and evidence.source_structure == "column"
            for evidence in field.source_evidence
        ):
            field_groups.setdefault((field.datasource_id, field.field_name), []).append(field)
    for key, fields in field_groups.items():
        fields_by_datasource_and_name[key] = tuple(
            sorted(fields, key=lambda field: field.canonical_id)
        )

    for column_instance in sorted(entities.column_instances, key=lambda item: item.canonical_id):
        for evidence in sorted(column_instance.source_evidence, key=_evidence_order_key):
            if (
                evidence.evidence_type != EvidenceType.COLUMN_INSTANCE
                or not _is_direct_xml(evidence)
                or (
                    not evidence.source_locator.startswith("/workbook/datasources/")
                    and isinstance(evidence.source_attributes.get("datasource"), str)
                )
            ):
                continue

            datasource_ids = _enclosing_datasource_ids(evidence, entities.datasources)
            if not column_instance.datasource_id or len(datasource_ids) != 1:
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id,
                        evidence,
                        "column-instance evidence has no unique enclosing datasource",
                    )
                )
                continue
            datasource_id = next(iter(datasource_ids))
            if datasource_id != column_instance.datasource_id:
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id,
                        evidence,
                        "enclosing datasource conflicts with column instance identity",
                    )
                )
                continue

            source_column_name = evidence.source_attributes.get("column")
            if not isinstance(source_column_name, str) or not source_column_name:
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id,
                        evidence,
                        "column-instance evidence is missing authoritative column attribute",
                    )
                )
                continue
            source_name = evidence.source_attributes.get("name")
            if not isinstance(source_name, str) or not source_name:
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id,
                        evidence,
                        "column-instance evidence is missing authoritative name attribute",
                    )
                )
                continue
            if source_name != column_instance.column_instance_name:
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id,
                        evidence,
                        "column-instance evidence name conflicts with column instance identity",
                    )
                )
                continue

            candidates = fields_by_datasource_and_name.get(
                (datasource_id, source_column_name), ()
            )
            if len(candidates) != 1:
                reason = (
                    "column-instance evidence has no matching canonical field"
                    if not candidates
                    else "column-instance evidence has multiple matching canonical fields"
                )
                issues.append(
                    FieldColumnInstanceResolutionIssue(
                        column_instance.canonical_id, evidence, reason
                    )
                )
                continue

            field = candidates[0]
            key = (field.canonical_id, column_instance.canonical_id)
            relationship = FieldColumnInstanceRelationship(
                field.canonical_id, column_instance.canonical_id, frozenset({evidence})
            )
            relationships[key] = (
                _add_field_column_instance_evidence(relationships[key], evidence)
                if key in relationships
                else relationship
            )

    ordered_relationships = tuple(
        relationships[key] for key in sorted(relationships)
    )
    ordered_issues = tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.column_instance_id or "",
                _evidence_order_key(issue.evidence),
                issue.reason,
            ),
        )
    )
    return FieldColumnInstanceResolution(ordered_relationships, ordered_issues)


def resolve_column_instance_to_worksheet(
    entities: CanonicalEntities,
) -> ColumnInstanceWorksheetResolution:
    """Resolve worksheet-contained CI occurrences using direct XML evidence only."""
    relationships: dict[tuple[str, str], ColumnInstanceWorksheetRelationship] = {}
    issues: list[ColumnInstanceWorksheetResolutionIssue] = []
    datasource_ids_by_name = {
        datasource.name: datasource.canonical_id for datasource in entities.datasources
    }

    # Worksheet occurrences are intentionally not canonical Column Instances: their
    # datasource context comes from the worksheet dependency parent, not datasource
    # containment.  Construction retains them as issues, so include that evidence.
    all_evidence = {
        evidence
        for group in (
            entities.datasources, entities.tables, entities.columns, entities.fields,
            entities.column_instances, entities.worksheets,
        )
        for entity in group
        for evidence in entity.source_evidence
    } | {issue.evidence for issue in entities.issues}
    worksheet_ci_evidence = sorted(
        (
            evidence for evidence in all_evidence
            if evidence.evidence_type == EvidenceType.COLUMN_INSTANCE
            and _is_direct_xml(evidence)
            and evidence.source_locator.startswith("/workbook/worksheets/")
        ),
        key=_evidence_order_key,
    )

    for evidence in worksheet_ci_evidence:
        worksheet_ids = _enclosing_worksheet_ids(evidence, entities.worksheets)
        if len(worksheet_ids) != 1:
            issues.append(ColumnInstanceWorksheetResolutionIssue(
                None, evidence, "column-instance evidence has no unique enclosing worksheet"
            ))
            continue
        name = evidence.source_attributes.get("name")
        if not isinstance(name, str) or not name:
            issues.append(ColumnInstanceWorksheetResolutionIssue(
                None, evidence, "column-instance evidence is missing authoritative name attribute"
            ))
            continue
        datasource_name = evidence.source_attributes.get("datasource")
        if not isinstance(datasource_name, str) or not datasource_name:
            issues.append(ColumnInstanceWorksheetResolutionIssue(
                None, evidence, "worksheet column-instance evidence is missing datasource context"
            ))
            continue
        datasource_id = datasource_ids_by_name.get(datasource_name)
        if datasource_id is None:
            issues.append(ColumnInstanceWorksheetResolutionIssue(
                None, evidence, "worksheet column-instance datasource does not resolve canonically"
            ))
            continue
        candidates = tuple(sorted(
            (
                column_instance for column_instance in entities.column_instances
                if column_instance.datasource_id == datasource_id
                and column_instance.column_instance_name == name
            ),
            key=lambda item: item.canonical_id,
        ))
        if len(candidates) != 1:
            issues.append(ColumnInstanceWorksheetResolutionIssue(
                None, evidence,
                "worksheet column-instance has no matching canonical column instance"
                if not candidates else "worksheet column-instance has multiple matching canonical column instances",
            ))
            continue
        column_instance = candidates[0]
        worksheet_id = next(iter(worksheet_ids))
        key = (column_instance.canonical_id, worksheet_id)
        relationship = ColumnInstanceWorksheetRelationship(
            column_instance.canonical_id, worksheet_id, frozenset({evidence})
        )
        relationships[key] = (
            _add_relationship_evidence(relationships[key], evidence)
            if key in relationships else relationship
        )

    return ColumnInstanceWorksheetResolution(
        tuple(relationships[key] for key in sorted(relationships)),
        tuple(sorted(issues, key=lambda issue: (
            issue.column_instance_id or "", _evidence_order_key(issue.evidence), issue.reason,
        ))),
    )


def resolve_column_to_field(entities: CanonicalEntities) -> ColumnFieldResolution:
    """Resolve a Column from metadata ``local-name`` to one scoped Field exactly."""
    relationships: dict[tuple[str, str], ColumnFieldRelationship] = {}
    issues: list[ColumnFieldResolutionIssue] = []
    fields_by_datasource_and_id: dict[tuple[str, str], tuple] = {}
    groups: dict[tuple[str, str], list] = {}
    for field in entities.fields:
        if any(
            _is_direct_xml(e)
            and (e.source_structure == "column"
                 or (e.source_structure == "metadata-record"
                     and e.evidence_type == EvidenceType.METADATA_RECORD
                     and e.source_attributes.get("class") == "column"))
            for e in field.source_evidence
        ):
            groups.setdefault((field.datasource_id, field.field_name), []).append(field)
    for key, fields in groups.items():
        fields_by_datasource_and_id[key] = tuple(sorted(fields, key=lambda item: item.canonical_id))

    for column in sorted(entities.columns, key=lambda item: item.canonical_id):
        for evidence in sorted(column.source_evidence, key=_evidence_order_key):
            if (evidence.evidence_type != EvidenceType.METADATA_RECORD or not _is_direct_xml(evidence)
                    or evidence.source_attributes.get("class") != "column"):
                continue
            field_id = evidence.source_attributes.get("local-name")
            if not isinstance(field_id, str) or not field_id:
                issues.append(ColumnFieldResolutionIssue(
                    column.canonical_id, evidence,
                    "column metadata evidence is missing authoritative local-name field identifier",
                ))
                continue
            candidates = fields_by_datasource_and_id.get((column.datasource_id, field_id), ())
            if len(candidates) != 1:
                issues.append(ColumnFieldResolutionIssue(
                    column.canonical_id, evidence,
                    "column metadata evidence has no matching canonical field"
                    if not candidates else "column metadata evidence has multiple matching canonical fields",
                ))
                continue
            field = candidates[0]
            key = (column.canonical_id, field.canonical_id)
            relationship = ColumnFieldRelationship(
                column.canonical_id, field.canonical_id, frozenset({evidence})
            )
            relationships[key] = (
                _add_relationship_evidence(relationships[key], evidence)
                if key in relationships else relationship
            )
@dataclass(frozen=True)
class TableLogicalRelationshipResolution:
    relationships: tuple[TableLogicalRelationship, ...]
    issues: tuple[TableLogicalRelationshipResolutionIssue, ...]


def resolve_table_logical_relationship(
    entities: CanonicalEntities, all_evidence: Iterable[SourceEvidence]
) -> TableLogicalRelationshipResolution:
    """Resolve logical relationships using object-to-relation mapping."""
    relationships: dict[str, TableLogicalRelationship] = {}
    issues: list[TableLogicalRelationshipResolutionIssue] = []

    # 1. Build object mapping: object_id -> relation_locator
    object_map: dict[str, str] = {}
    for evidence in all_evidence:
        if evidence.evidence_type == EvidenceType.OBJECT:
            obj_id = evidence.source_attributes.get("id")
            if isinstance(obj_id, str):
                object_map[obj_id] = evidence.source_locator

    # 2. Resolve relationships
    for evidence in all_evidence:
        if evidence.evidence_type != EvidenceType.LOGICAL_RELATIONSHIP:
            continue
            
        first_end_point = evidence.source_attributes.get("first-end-point")
        second_end_point = evidence.source_attributes.get("second-end-point")
        if isinstance(first_end_point, list): first_end_point = first_end_point[0]
        if isinstance(second_end_point, list): second_end_point = second_end_point[0]
        
        first_obj_id = first_end_point.get("object-id") if isinstance(first_end_point, Mapping) else None
        second_obj_id = second_end_point.get("object-id") if isinstance(second_end_point, Mapping) else None

        if not first_obj_id or not second_obj_id:
            issues.append(TableLogicalRelationshipResolutionIssue(evidence.source_locator, None, "missing object-id", evidence, "first or second end point object-id missing"))
            continue

        # Map to Table
        first_table = next((t for t in entities.tables for e in t.source_evidence if object_map.get(first_obj_id, "").startswith(e.source_locator)), None)
        second_table = next((t for t in entities.tables for e in t.source_evidence if object_map.get(second_obj_id, "").startswith(e.source_locator)), None)
        
        if not first_table or not second_table:
            issues.append(TableLogicalRelationshipResolutionIssue(evidence.source_locator, None, first_obj_id if not first_table else second_obj_id, evidence, "table not found"))
            continue
            
        # Datasource check
        if first_table.datasource_id != second_table.datasource_id:
            issues.append(TableLogicalRelationshipResolutionIssue(evidence.source_locator, first_table.datasource_id, first_obj_id, evidence, "cross-datasource logical relationship"))
            continue
            
        # Commutative Identity
        from .identity import LogicalRelationshipIdentity, canonical_id_for
        identity = LogicalRelationshipIdentity(first_table.datasource_id, first_table.canonical_id, second_table.canonical_id)
        canonical_id = canonical_id_for(identity)
        
        # Expression raw (Simplified for now - needs proper C14N per design)
        expression = evidence.source_attributes.get("expression", {}).get("#text", "")
        
        rel = TableLogicalRelationship(canonical_id, first_table.datasource_id, first_table.canonical_id, second_table.canonical_id, expression, source_evidence=frozenset({evidence}))
        relationships[canonical_id] = rel
        
    return TableLogicalRelationshipResolution(tuple(relationships.values()), tuple(issues))
