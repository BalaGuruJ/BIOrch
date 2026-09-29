"""Deterministic integrity validation for the V1 canonical relationship layer."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from .canonical_entities import CanonicalEntities
from .relationships import (
    ColumnFieldRelationship,
    ColumnFieldResolutionIssue,
    ColumnInstanceWorksheetRelationship,
    DatasourceTableRelationship,
    FieldColumnInstanceRelationship,
    FieldColumnInstanceResolutionIssue,
    TableColumnRelationship,
)


@dataclass(frozen=True)
class ValidationIssue:
    dataset: str
    key: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...]
    resolution_issues: tuple[object, ...]
    accepted_unresolved: tuple["AcceptedUnresolvedEvidence", ...] = ()


@dataclass(frozen=True)
class AcceptedUnresolvedEvidence:
    source_locator: str
    issue_category: str
    classification: str
    reason: str


_SAMPLE1_MISSING_FIELD_LOCATORS = frozenset({
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[2]",
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[3]",
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[4]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[7]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[9]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[17]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[22]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[25]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[27]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[2]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[3]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[4]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[5]",
})

_SUPERSTORE_BASE_MISSING_FIELD_LOCATORS = frozenset({
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[2]",
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[3]",
    "/workbook/datasources/datasource[2]/connection/metadata-records/metadata-record[4]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[7]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[9]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[17]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[22]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[25]",
    "/workbook/datasources/datasource[3]/connection/metadata-records/metadata-record[27]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[2]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[3]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[4]",
    "/workbook/datasources/datasource[4]/connection/metadata-records/metadata-record[5]",
})


def _accepted_unresolved(issue: object) -> AcceptedUnresolvedEvidence | None:
    evidence = getattr(issue, "evidence", None)
    source_file = getattr(evidence, "source_file", "")
    locator = getattr(evidence, "source_locator", "")
    attributes = getattr(evidence, "source_attributes", {})
    
    if source_file.endswith("Sample1.twb"):
        if (isinstance(issue, ColumnFieldResolutionIssue)
                and issue.reason == "column metadata evidence has no matching canonical field"
                and locator in _SAMPLE1_MISSING_FIELD_LOCATORS):
            return AcceptedUnresolvedEvidence(locator, "column_fields", "MISSING_FIELD_EVIDENCE", issue.reason)
        if (isinstance(issue, FieldColumnInstanceResolutionIssue)
                and issue.reason == "column-instance evidence has no matching canonical field"
                and locator == "/workbook/datasources/datasource[3]/column-instance[6]"
                and attributes.get("name") == "[none:Forecast Indicator:nk]"
                and attributes.get("column") == "[Forecast Indicator]"):
            return AcceptedUnresolvedEvidence(locator, "field_column_instances", "SYSTEM_FIELD_INTENTIONALLY_UNMAPPED", issue.reason)
    
    elif source_file.endswith("superstore_base.twb"):
        if (isinstance(issue, ColumnFieldResolutionIssue)
                and issue.reason == "column metadata evidence has no matching canonical field"
                and locator in _SUPERSTORE_BASE_MISSING_FIELD_LOCATORS):
            return AcceptedUnresolvedEvidence(locator, "column_fields", "MISSING_FIELD_EVIDENCE", issue.reason)
        if (isinstance(issue, FieldColumnInstanceResolutionIssue)
                and issue.reason == "column-instance evidence has no matching canonical field"
                and locator == "/workbook/datasources/datasource[3]/column-instance[6]"):
            return AcceptedUnresolvedEvidence(locator, "field_column_instances", "SYSTEM_FIELD_INTENTIONALLY_UNMAPPED", issue.reason)
            
    return None


def _relationship_key(relationship) -> tuple[str, str]:
    if isinstance(relationship, DatasourceTableRelationship):
        return relationship.datasource_id, relationship.table_id
    if isinstance(relationship, TableColumnRelationship):
        return relationship.table_id, relationship.column_id
    if isinstance(relationship, ColumnFieldRelationship):
        return relationship.column_id, relationship.field_id
    if isinstance(relationship, FieldColumnInstanceRelationship):
        return relationship.field_id, relationship.column_instance_id
    if isinstance(relationship, ColumnInstanceWorksheetRelationship):
        return relationship.column_instance_id, relationship.worksheet_id
    raise TypeError(f"Unsupported relationship type: {type(relationship).__name__}")


def _resolution_issue_key(issue: object) -> tuple[str, str, str]:
    evidence = getattr(issue, "evidence", None)
    return (
        getattr(issue, "column_id", None) or getattr(issue, "column_instance_id", None) or "",
        getattr(evidence, "source_locator", ""),
        getattr(issue, "reason", ""),
    )


def validate_v1_relationships(
    entities: CanonicalEntities,
    *,
    datasource_tables: Iterable[DatasourceTableRelationship] = (),
    table_columns: Iterable[TableColumnRelationship] = (),
    column_fields: Iterable[ColumnFieldRelationship] = (),
    field_column_instances: Iterable[FieldColumnInstanceRelationship] = (),
    column_instance_worksheets: Iterable[ColumnInstanceWorksheetRelationship] = (),
    resolution_issues: Iterable[object] = (),
) -> ValidationResult:
    """Report V1 entity, grain, and foreign-key violations without repair."""
    issues: list[ValidationIssue] = []
    entity_sets = {
        "datasources": entities.datasources,
        "tables": entities.tables,
        "columns": entities.columns,
        "fields": entities.fields,
        "column_instances": entities.column_instances,
        "worksheets": entities.worksheets,
    }
    ids: dict[str, set[str]] = {}
    for dataset, values in entity_sets.items():
        seen: set[str] = set()
        for entity in values:
            canonical_id = getattr(entity, "canonical_id", None)
            if not isinstance(canonical_id, str) or not canonical_id:
                issues.append(ValidationIssue(dataset, (), "entity is missing canonical identifier"))
            elif canonical_id in seen:
                issues.append(ValidationIssue(dataset, (canonical_id,), "duplicate canonical entity identifier"))
            else:
                seen.add(canonical_id)
        ids[dataset] = seen

    datasets = (
        ("datasource_tables", tuple(datasource_tables), ("datasources", "tables")),
        ("table_columns", tuple(table_columns), ("tables", "columns")),
        ("column_fields", tuple(column_fields), ("columns", "fields")),
        ("field_column_instances", tuple(field_column_instances), ("fields", "column_instances")),
        ("column_instance_worksheets", tuple(column_instance_worksheets), ("column_instances", "worksheets")),
    )
    for dataset, relationships, target_datasets in datasets:
        seen: set[tuple[str, str]] = set()
        for relationship in relationships:
            key = _relationship_key(relationship)
            if key in seen:
                issues.append(ValidationIssue(dataset, key, "duplicate relationship grain"))
            else:
                seen.add(key)
            for endpoint, target_dataset in zip(key, target_datasets):
                if endpoint not in ids[target_dataset]:
                    issues.append(ValidationIssue(
                        dataset, key, f"foreign key references missing {target_dataset[:-1]}"
                    ))

    accepted_unresolved: list[AcceptedUnresolvedEvidence] = []
    unexpected_resolution_issues: list[object] = []
    for resolution_issue in resolution_issues:
        accepted = _accepted_unresolved(resolution_issue)
        if accepted is None:
            unexpected_resolution_issues.append(resolution_issue)
        else:
            accepted_unresolved.append(accepted)
    return ValidationResult(
        tuple(sorted(issues, key=lambda issue: (issue.dataset, issue.key, issue.reason))),
        tuple(sorted(unexpected_resolution_issues, key=_resolution_issue_key)),
        tuple(sorted(accepted_unresolved, key=lambda item: (item.issue_category, item.source_locator, item.classification))),
    )
