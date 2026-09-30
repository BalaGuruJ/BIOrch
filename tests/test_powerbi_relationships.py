import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.canonical_entities import Cardinality, CrossFilteringBehavior

def test_adventure_works_relationships():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Verify relationships exist
    assert len(canonical_model.relationships) > 0
    
    # Verify a known relationship structure
    rel = canonical_model.relationships[0]
    assert rel.id is not None
    assert rel.from_table_id is not None
    assert rel.to_table_id is not None
    assert rel.from_column_id is not None
    assert rel.to_column_id is not None
    assert isinstance(rel.is_active, bool)
    assert isinstance(rel.cardinality, Cardinality)
    assert isinstance(rel.cross_filter_direction, CrossFilteringBehavior)
    
    # Ensure referential integrity
    table_ids = {t.id for t in canonical_model.tables}
    column_ids = {c.id for c in canonical_model.columns}
    
    assert rel.from_table_id in table_ids
    assert rel.to_table_id in table_ids
    assert rel.from_column_id in column_ids
    assert rel.to_column_id in column_ids
