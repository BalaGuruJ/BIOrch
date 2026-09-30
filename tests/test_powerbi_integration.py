import pytest
import os
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.validator import validate
from src.biorch.integrations.powerbi.serializer import serialize

def test_adventure_works_integration():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    # Adapter
    adapter = PowerBIAdapter()
    parsed_model, diagnostics = adapter.parse(model_dir)
    
    # Canonicalize
    canonical_model = canonicalize(parsed_model)
    
    # Validate
    validate(canonical_model)
    
    # Serialize
    json_output = serialize(canonical_model)
    assert json_output is not None
    assert "tables" in json_output
