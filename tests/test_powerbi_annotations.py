import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize

def test_adventure_works_annotations():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Check tables for annotations
    for table in canonical_model.tables:
        if table.annotations:
            for ann in table.annotations:
                assert isinstance(ann.name, str)
                assert isinstance(ann.value, (str, type(None)))
    
    # Check columns/measures
    for col in canonical_model.columns:
        if col.annotations:
            for ann in col.annotations:
                assert isinstance(ann.name, str)
                assert isinstance(ann.value, (str, type(None)))
                
    for measure in canonical_model.measures:
        if measure.annotations:
            for ann in measure.annotations:
                assert isinstance(ann.name, str)
                assert isinstance(ann.value, (str, type(None)))
