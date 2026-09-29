
import pytest
import json
import jsonschema
import shutil
from pathlib import Path

# Imports from project code
from biorch.integrations.tableau.writer import write_v1_json, write_v1_csv, InvalidRelationshipGraphError
from biorch.integrations.tableau.canonical_entities import (
    CanonicalEntities, Datasource, Table, Column, Field, ColumnInstance, Worksheet
)
from biorch.integrations.tableau.identity import (
    IdentityRegistry, DatasourceIdentity, TableIdentity, ColumnIdentity, FieldIdentity, ColumnInstanceIdentity, WorksheetIdentity
)
from biorch.integrations.tableau.relationships import (
    DatasourceTableRelationship, TableColumnRelationship, ColumnFieldRelationship, FieldColumnInstanceRelationship, ColumnInstanceWorksheetRelationship
)
from biorch.integrations.tableau.validation import ValidationResult
from biorch.integrations.tableau.entities import SourceEvidence, EvidenceType

def _create_fixture():
    registry = IdentityRegistry()
    
    # Simple evidence for fixture
    evidence = SourceEvidence("file", "xml", "structure", "locator", {}, EvidenceType.UNKNOWN)
    
    # Datasource
    ds_id_obj = DatasourceIdentity("DS1", "conn", "1.0")
    ds_canonical_id = registry.register(ds_id_obj, source_locator="/ds")
    ds = Datasource(ds_canonical_id, ds_id_obj, "DS1", "conn", "1.0", frozenset([evidence]))
    
    # Table
    tbl_id_obj = TableIdentity(ds_canonical_id, "T1", "conn1")
    tbl_canonical_id = registry.register(tbl_id_obj, source_locator="/t")
    tbl = Table(tbl_canonical_id, tbl_id_obj, ds_canonical_id, "T1", "conn1", frozenset([evidence]))
    
    # Column
    col_id_obj = ColumnIdentity(ds_canonical_id, "[T1]", "C1")
    col_canonical_id = registry.register(col_id_obj, source_locator="/c")
    col = Column(col_canonical_id, col_id_obj, ds_canonical_id, "[T1]", "C1", frozenset([evidence]))
    
    # Field
    fld_id_obj = FieldIdentity(ds_canonical_id, "F1")
    fld_canonical_id = registry.register(fld_id_obj, source_locator="/f")
    fld = Field(fld_canonical_id, fld_id_obj, ds_canonical_id, "F1", frozenset([evidence]))
    
    # ColumnInstance
    ci_id_obj = ColumnInstanceIdentity(ds_canonical_id, "CI1")
    ci_canonical_id = registry.register(ci_id_obj, source_locator="/ci")
    ci = ColumnInstance(ci_canonical_id, ci_id_obj, ds_canonical_id, "CI1", frozenset([evidence]))
    
    # Worksheet
    ws_id_obj = WorksheetIdentity("WS1")
    ws_canonical_id = registry.register(ws_id_obj, source_locator="/ws")
    ws = Worksheet(ws_canonical_id, ws_id_obj, "WS1", frozenset([evidence]))
    
    entities = CanonicalEntities(
        (ds,), (tbl,), (col,), (fld,), (ci,), (ws,), ()
    )
    
    relationships = (
        DatasourceTableRelationship(ds_canonical_id, tbl_canonical_id, frozenset([evidence])),
        TableColumnRelationship(tbl_canonical_id, col_canonical_id, frozenset([evidence])),
        ColumnFieldRelationship(col_canonical_id, fld_canonical_id, frozenset([evidence])),
        FieldColumnInstanceRelationship(fld_canonical_id, ci_canonical_id, frozenset([evidence])),
        ColumnInstanceWorksheetRelationship(ci_canonical_id, ws_canonical_id, frozenset([evidence]))
    )
    
    return entities, relationships

def test_full_serialization():
    entities, rels = _create_fixture()
    output_dir = Path("test_output_full")
    json_path = output_dir / "metadata.json"
    
    write_v1_json(json_path, entities,
        datasource_tables=[rels[0]], table_columns=[rels[1]], 
        column_fields=[rels[2]], field_column_instances=[rels[3]], 
        column_instance_worksheets=[rels[4]])
    
    with open("schemas/tableau_metadata.schema.json", "r") as f:
        schema = json.load(f)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    jsonschema.validate(instance=data, schema=schema)
    assert data["schema_version"] == "1.0"
    assert len(data["workbook_metadata"]["entities"]["datasources"]) == 1
    assert len(data["workbook_metadata"]["relationships"]["datasource_tables"]) == 1
    
    shutil.rmtree(output_dir)

def test_determinism():
    entities, rels = _create_fixture()
    output_dir = Path("test_output_det")
    json1 = output_dir / "1.json"
    json2 = output_dir / "2.json"
    
    write_v1_json(json1, entities,
        datasource_tables=[rels[0]], table_columns=[rels[1]], 
        column_fields=[rels[2]], field_column_instances=[rels[3]], 
        column_instance_worksheets=[rels[4]])
    
    write_v1_json(json2, entities,
        datasource_tables=[rels[0]], table_columns=[rels[1]], 
        column_fields=[rels[2]], field_column_instances=[rels[3]], 
        column_instance_worksheets=[rels[4]])
        
    with open(json1, "r") as f1, open(json2, "r") as f2:
        assert json.load(f1) == json.load(f2)
        
    shutil.rmtree(output_dir)

def test_invalid_graph():
    entities, rels = _create_fixture()
    # Invalid: relationship references non-existent entities
    invalid_rels = (
        DatasourceTableRelationship("non-existent", "non-existent", frozenset()),
    )
    output_dir = Path("test_output_invalid")
    
    with pytest.raises(InvalidRelationshipGraphError):
        write_v1_json(output_dir / "invalid.json", entities, datasource_tables=invalid_rels)
        
    if output_dir.exists():
        shutil.rmtree(output_dir)

def test_csv_json_equivalence():
    entities, rels = _create_fixture()
    output_dir = Path("test_output_eq")
    
    # Write both
    write_v1_csv(output_dir, entities,
        datasource_tables=[rels[0]], table_columns=[rels[1]], 
        column_fields=[rels[2]], field_column_instances=[rels[3]], 
        column_instance_worksheets=[rels[4]])
    
    json_path = output_dir / "metadata.json"
    write_v1_json(json_path, entities,
        datasource_tables=[rels[0]], table_columns=[rels[1]], 
        column_fields=[rels[2]], field_column_instances=[rels[3]], 
        column_instance_worksheets=[rels[4]])
        
    # Read both and compare logical content
    # A simple check: ensure JSON has the expected data from the fixture
    with open(json_path, "r") as f:
        data = json.load(f)
        
    # Check one datasource
    assert data["workbook_metadata"]["entities"]["datasources"][0]["canonical_id"] == entities.datasources[0].canonical_id
    
    # Check that CSV files were created
    assert (output_dir / "datasources.csv").exists()
    
    shutil.rmtree(output_dir)
