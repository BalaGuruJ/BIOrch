"""Deterministic serialization of V1 canonical entities and relationships."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from collections.abc import Iterable
from dataclasses import is_dataclass, asdict
from enum import Enum

from .canonical_entities import CanonicalEntities
from .relationships import (
    ColumnFieldRelationship, ColumnInstanceWorksheetRelationship,
    DatasourceTableRelationship, FieldColumnInstanceRelationship,
    TableColumnRelationship,
)
from .validation import ValidationResult, validate_v1_relationships
from .entities import FrozenDict


class InvalidRelationshipGraphError(ValueError):
    """Raised when validation prevents serialization of the supplied graph."""


ENTITY_DATASETS = (
    ("datasources.csv", ("datasource_id", "name", "connection_class", "version"), "datasources",
     lambda item: (item.canonical_id, item.name, item.connection_class, item.version)),
    ("tables.csv", ("table_id", "datasource_id", "relation_name", "connection_name"), "tables",
     lambda item: (item.canonical_id, item.datasource_id, item.relation_name, item.connection_name)),
    ("columns.csv", ("column_id", "datasource_id", "parent_name", "remote_name"), "columns",
     lambda item: (item.canonical_id, item.datasource_id, item.parent_name, item.remote_name)),
    ("fields.csv", ("field_id", "datasource_id", "field_name"), "fields",
     lambda item: (item.canonical_id, item.datasource_id, item.field_name)),
    ("column_instances.csv", ("column_instance_id", "datasource_id", "column_instance_name"), "column_instances",
     lambda item: (item.canonical_id, item.datasource_id, item.column_instance_name)),
    ("worksheets.csv", ("worksheet_id", "worksheet_name"), "worksheets",
     lambda item: (item.canonical_id, item.worksheet_name)),
)

RELATIONSHIP_DATASETS = (
    ("datasource_tables.csv", ("datasource_id", "table_id")),
    ("table_columns.csv", ("table_id", "column_id")),
    ("column_fields.csv", ("column_id", "field_id")),
    ("field_column_instances.csv", ("field_id", "column_instance_id")),
    ("column_instance_worksheets.csv", ("column_instance_id", "worksheet_id")),
)


def _write_rows(path: Path, header: tuple[str, ...], rows: Iterable[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow("" if value is None else value for value in row)


class V1Encoder(json.JSONEncoder):
    """Encodes V1 dataclasses, sets, and enums."""
    def default(self, obj):
        if isinstance(obj, (frozenset, set)):
            return list(obj)
        if isinstance(obj, tuple):
            return list(obj)
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, FrozenDict):
            return dict(obj)
        return super().default(obj)


def write_v1_csv(
    output_directory: str | Path,
    entities: CanonicalEntities,
    *,
    datasource_tables: Iterable[DatasourceTableRelationship] = (),
    table_columns: Iterable[TableColumnRelationship] = (),
    column_fields: Iterable[ColumnFieldRelationship] = (),
    field_column_instances: Iterable[FieldColumnInstanceRelationship] = (),
    column_instance_worksheets: Iterable[ColumnInstanceWorksheetRelationship] = (),
    validation_result: ValidationResult | None = None,
) -> tuple[Path, ...]:
    """Write only a validated V1 graph, without resolution or repair."""
    relationship_values = tuple(tuple(values) for values in (
        datasource_tables, table_columns, column_fields, field_column_instances,
        column_instance_worksheets,
    ))
    calculated_validation = validate_v1_relationships(
        entities,
        datasource_tables=relationship_values[0], table_columns=relationship_values[1],
        column_fields=relationship_values[2], field_column_instances=relationship_values[3],
        column_instance_worksheets=relationship_values[4],
    )
    if validation_result is None:
        validation_result = calculated_validation
    if (calculated_validation.issues or validation_result.issues
            or validation_result.resolution_issues):
        raise InvalidRelationshipGraphError("validation reported unresolved or integrity issues")

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, header, attribute, row_for in ENTITY_DATASETS:
        path = directory / filename
        _write_rows(path, header, sorted((row_for(item) for item in getattr(entities, attribute)), key=lambda row: row[0]))
        written.append(path)
    for (filename, header), relationships in zip(RELATIONSHIP_DATASETS, relationship_values):
        path = directory / filename
        rows = sorted({tuple(getattr(relationship, field) for field in header) for relationship in relationships})
        _write_rows(path, header, rows)
        written.append(path)
    audit_path = directory / "accepted_unresolved.csv"
    _write_rows(
        audit_path,
        ("source_locator", "issue_category", "classification", "reason", "count"),
        ((item.source_locator, item.issue_category, item.classification, item.reason, 1)
         for item in validation_result.accepted_unresolved),
    )
    written.append(audit_path)
    return tuple(written)


def write_v1_json(
    output_path: str | Path,
    entities: CanonicalEntities,
    *,
    datasource_tables: Iterable[DatasourceTableRelationship] = (),
    table_columns: Iterable[TableColumnRelationship] = (),
    column_fields: Iterable[ColumnFieldRelationship] = (),
    field_column_instances: Iterable[FieldColumnInstanceRelationship] = (),
    column_instance_worksheets: Iterable[ColumnInstanceWorksheetRelationship] = (),
    validation_result: ValidationResult | None = None,
) -> Path:
    """Serialize the V1 graph to a single validated JSON file."""
    relationship_values = (
        list(datasource_tables), list(table_columns), list(column_fields),
        list(field_column_instances), list(column_instance_worksheets)
    )
    # Validation logic same as CSV writer
    calculated_validation = validate_v1_relationships(
        entities,
        datasource_tables=relationship_values[0], table_columns=relationship_values[1],
        column_fields=relationship_values[2], field_column_instances=relationship_values[3],
        column_instance_worksheets=relationship_values[4],
    )
    if validation_result is None:
        validation_result = calculated_validation
    if (calculated_validation.issues or validation_result.issues
            or validation_result.resolution_issues):
        raise InvalidRelationshipGraphError("validation reported unresolved or integrity issues")

    output = {
        "schema_version": "1.0",
        "workbook_metadata": {
            "entities": {
                "datasources": list(entities.datasources),
                "tables": list(entities.tables),
                "columns": list(entities.columns),
                "fields": list(entities.fields),
                "column_instances": list(entities.column_instances),
                "worksheets": list(entities.worksheets)
            },
            "relationships": {
                "datasource_tables": relationship_values[0],
                "table_columns": relationship_values[1],
                "column_fields": relationship_values[2],
                "field_column_instances": relationship_values[3],
                "column_instance_worksheets": relationship_values[4]
            },
            "validation": {
                "issues": list(entities.issues),
                "accepted_unresolved": list(validation_result.accepted_unresolved)
            }
        }
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(output, stream, cls=V1Encoder, indent=2, sort_keys=True)
    return path
