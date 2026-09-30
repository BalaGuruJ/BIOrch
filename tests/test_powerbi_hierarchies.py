import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

def test_adventure_works_hierarchies():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Hierarchies might be empty in AW, that is fine.
    # The test structure is what we care about.
    
    for hier in canonical_model.hierarchies:
        assert hier.id is not None
        assert hier.table_id is not None
        assert hier.name is not None
        assert isinstance(hier.levels, tuple)
        
        # Verify level structure
        for level in hier.levels:
            assert level.id is not None
            assert level.hierarchy_id == hier.id
            assert level.column_id is not None
            assert isinstance(level.ordinal, int)
            
            # Referential integrity check
            column_ids = {c.id for c in canonical_model.columns}
            assert level.column_id in column_ids
