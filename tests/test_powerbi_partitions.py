import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.canonical_entities import ProvenanceType

def test_adventure_works_partitions():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Verify partitions exist
    assert len(canonical_model.partitions) > 0
    
    # Verify a partition structure
    part = canonical_model.partitions[0]
    assert part.id is not None
    assert part.name is not None
    assert part.table_id is not None
    assert isinstance(part.provenance_type, ProvenanceType)
    
    # Ensure referential integrity
    table_ids = {t.id for t in canonical_model.tables}
    assert part.table_id in table_ids
    
    # If source evidence exists, verify properties
    if part.source_evidence:
        assert part.source_evidence.source_type is not None
        assert isinstance(part.source_evidence.expression, (str, type(None)))
    else:
        assert part.provenance_type in [ProvenanceType.UNAVAILABLE, ProvenanceType.UNRESOLVED]
