import pytest
import os
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

def test_adventure_works_integration():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    # Adapter
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    
    # Canonicalize
    canonical_model = canonicalize(parsed_model)
    
    # Validate basics
    assert len(canonical_model.tables) > 0
    assert canonical_model.tables[0].id is not None
    assert canonical_model.tables[0].name is not None
    assert canonical_model.columns[0].table_id is not None
