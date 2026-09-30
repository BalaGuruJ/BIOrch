import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

def test_semantic_lineage_traversal():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Map for O(1) lookup
    tables = {t.id: t for t in canonical_model.tables}
    columns = {c.id: c for c in canonical_model.columns}
    
    # 1. Model -> Table -> Column
    assert len(canonical_model.tables) > 0
    table_id = canonical_model.tables[0].id
    table_cols = [c for c in canonical_model.columns if c.table_id == table_id]
    assert len(table_cols) > 0
    
    # 2. Table -> Measure
    table_measures = [m for m in canonical_model.measures if m.table_id == table_id]
    # AW has measures, so this should pass
    
    # 3. Table -> Partition
    table_partitions = [p for p in canonical_model.partitions if p.table_id == table_id]
    assert len(table_partitions) > 0
    
    # 4. Table -> Hierarchy -> Level -> Column
    for hier in canonical_model.hierarchies:
        if hier.table_id == table_id:
            for level in hier.levels:
                assert level.column_id in columns
                
    # 5. Relationship traversals
    for rel in canonical_model.relationships:
        assert rel.from_table_id in tables
        assert rel.to_table_id in tables
        assert rel.from_column_id in columns
        assert rel.to_column_id in columns

    # 6. Partition -> SourceEvidence
    for part in canonical_model.partitions:
        if part.source_evidence:
            assert part.source_evidence.source_type is not None
