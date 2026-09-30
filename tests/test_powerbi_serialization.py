import pytest
import json
import jsonschema
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.serializer import serialize

def test_serialization_adventure_works():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Serialize
    json_str = serialize(canonical_model)
    data = json.loads(json_str)
    
    # Validate against schema
    with open("schemas/phase07_metadata.schema.json") as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=data, schema=schema)
    
    # Determinism check (serialize again)
    json_str2 = serialize(canonical_model)
    assert json_str == json_str2

def test_no_dax_m_execution_in_serialization():
    # Structural check only
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    json_str = serialize(canonical_model)
    
    # Verify no unexpected executable content in serialized output
    assert "eval(" not in json_str
    assert "exec(" not in json_str
    assert "subprocess" not in json_str
