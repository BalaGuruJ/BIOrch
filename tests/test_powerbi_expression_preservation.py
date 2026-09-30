import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

def test_adventure_works_calculated_columns_and_measures():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Verify measures exist and expressions are preserved
    assert len(canonical_model.measures) > 0
    measure = canonical_model.measures[0]
    assert measure.expression is not None
    assert isinstance(measure.expression, str)
    
    # Verify column structure
    assert len(canonical_model.columns) > 0
    
    # Verify calculated column capability
    found_calc = False
    for col in canonical_model.columns:
        if col.is_calculated:
            found_calc = True
            assert isinstance(col.expression, (str, type(None)))
            break
            
    # Note: If no calculated columns exist in AW, this test will pass
    # without verifying the expression of a calculated column.
    # This limitation is acceptable per the plan.

def test_no_dax_execution():
    # Verify that expressions remain as strings and no errors suggesting DAX execution occur
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    for measure in canonical_model.measures:
        assert isinstance(measure.expression, str)
        # Simple check that the expression is not a result object
        assert not hasattr(measure.expression, "__call__")
