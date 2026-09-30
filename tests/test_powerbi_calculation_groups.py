import pytest
import os
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

# Synthetic fixture generation for Calculation Groups
# NOTE: This relies on the adapter's existing ability to load from a folder.
# A small folder structure with a minimal TMDL definition including a calc group
# is required if one doesn't exist in examples/artifacts.

def test_calculation_group_extraction():
    # As AW doesn't have Calc Groups, we acknowledge the limitation.
    # If the adapter can load a synthetic folder, we test here.
    # Otherwise, this test serves as a structural placeholder.
    
    # Placeholder: Assuming a minimal synthetic fixture exists or is created:
    model_dir = "examples/artifacts/powerbi/SyntheticCalcGroup/SyntheticCalcGroup.SemanticModel"
    
    if not os.path.exists(model_dir):
        pytest.skip("Synthetic CalcGroup fixture not found.")
        
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    assert len(canonical_model.calculation_groups) > 0
    cg = canonical_model.calculation_groups[0]
    assert cg.name is not None
    assert len(cg.items) > 0
    
    item = cg.items[0]
    assert item.expression is not None
    assert isinstance(item.expression, str)
    assert item.calculation_group_id == cg.id
