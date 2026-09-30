import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

# Deterministic ID testing
def test_deterministic_identity():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    
    # First run
    parsed_model1 = adapter.load_model(model_dir)
    canonical1 = canonicalize(parsed_model1)
    
    # Second run
    parsed_model2 = adapter.load_model(model_dir)
    canonical2 = canonicalize(parsed_model2)
    
    # Assert identity equality for all tables
    for t1, t2 in zip(canonical1.tables, canonical2.tables):
        assert t1.id == t2.id
        
    # Assert identity equality for all columns
    for c1, c2 in zip(canonical1.columns, canonical2.columns):
        assert c1.id == c2.id
        
# Security: No DAX/M execution check
def test_no_dax_m_execution():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Verify all expressions are strings, not executable objects
    for col in canonical_model.columns:
        if col.expression:
            assert isinstance(col.expression, str)
            assert not callable(col.expression)
            
    for measure in canonical_model.measures:
        assert isinstance(measure.expression, str)
        assert not callable(measure.expression)
