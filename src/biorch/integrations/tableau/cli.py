"""Command-line orchestration for the V1 Tableau metadata extractor."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile

from .canonical_entities import construct_canonical_entities
from .extraction import extract_evidence
from .loader import load_workbook
from .relationships import (
    resolve_column_instance_to_worksheet, resolve_column_to_field,
    resolve_datasource_to_table, resolve_field_to_column_instance,
    resolve_table_to_column,
)
from .validation import ValidationResult, validate_v1_relationships
from .writer import write_v1_csv, write_v1_json


def run_pipeline(input_path: str | Path, output_directory: str | Path) -> tuple[Path, ...]:
    """Run the existing V1 pipeline and publish CSVs and JSON metadata."""
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"input workbook does not exist: {input_file}")
    if not input_file.is_file():
        raise IsADirectoryError(f"input workbook is not a file: {input_file}")

    destination = Path(output_directory)
    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(f"output path is not a directory: {destination}")
    destination_parent = destination.parent
    destination_parent.mkdir(parents=True, exist_ok=True)

    loaded = load_workbook(input_file)
    evidence = extract_evidence(str(input_file), loaded)
    entities = construct_canonical_entities(evidence)
    datasource_tables = resolve_datasource_to_table(entities)
    table_columns = resolve_table_to_column(entities)
    field_column_instances = resolve_field_to_column_instance(entities)
    column_instance_worksheets = resolve_column_instance_to_worksheet(entities)
    column_fields = resolve_column_to_field(entities)
    resolution_issues = (
        datasource_tables.issues + table_columns.issues + field_column_instances.issues
        + column_instance_worksheets.issues + column_fields.issues
    )
    integrity = validate_v1_relationships(
        entities,
        datasource_tables=datasource_tables.relationships,
        table_columns=table_columns.relationships,
        column_fields=column_fields.relationships,
        field_column_instances=field_column_instances.relationships,
        column_instance_worksheets=column_instance_worksheets.relationships,
        resolution_issues=resolution_issues,
    )

    staging = Path(tempfile.mkdtemp(prefix=".tableau-extractor-", dir=destination_parent))
    try:
        written_csvs = write_v1_csv(
            staging, entities,
            datasource_tables=datasource_tables.relationships,
            table_columns=table_columns.relationships,
            column_fields=column_fields.relationships,
            field_column_instances=field_column_instances.relationships,
            column_instance_worksheets=column_instance_worksheets.relationships,
            validation_result=integrity,
        )
        
        json_path = staging / "metadata.json"
        write_v1_json(
            json_path, entities,
            datasource_tables=datasource_tables.relationships,
            table_columns=table_columns.relationships,
            column_fields=column_fields.relationships,
            field_column_instances=field_column_instances.relationships,
            column_instance_worksheets=column_instance_worksheets.relationships,
            validation_result=integrity,
        )
        written = list(written_csvs) + [json_path]
        
        destination.mkdir(parents=True, exist_ok=True)
        published = []
        for path in written:
            target = destination / path.name
            os.replace(path, target)
            published.append(target)
        return tuple(published)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract V1 Tableau metadata CSV datasets.")
    parser.add_argument("input_twb", help="input Tableau .twb workbook")
    parser.add_argument("output_directory", help="directory for V1 CSV datasets")
    args = parser.parse_args(argv)
    try:
        run_pipeline(args.input_twb, args.output_directory)
    except Exception as error:
        print(f"Extraction failed: {error}", file=sys.stderr)
        return 1
    print(f"Extraction completed: {Path(args.output_directory)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
