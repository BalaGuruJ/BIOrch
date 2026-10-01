import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.canonical_entities import ProvenanceType

def test_pbi_lineage_and_provenance():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"

    # Adapter
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)

    # Canonicalize
    canonical_model = canonicalize(parsed_model)

    # Validate lineage_metadata exists independently for entities
    assert len(canonical_model.tables) > 0
    for table in canonical_model.tables:
        assert hasattr(table, 'lineage_metadata')
    for col in canonical_model.columns:
        assert hasattr(col, 'lineage_metadata')
    for measure in canonical_model.measures:
        assert hasattr(measure, 'lineage_metadata')
    for rel in canonical_model.relationships:
        assert hasattr(rel, 'lineage_metadata')

    # Validate source evidence for partitions
    assert len(canonical_model.partitions) > 0
    for part in canonical_model.partitions:
        assert hasattr(part, 'source_evidence')
        assert hasattr(part, 'provenance_type')
        if part.provenance_type == ProvenanceType.SUPPORTED and part.source_evidence:
            assert part.source_evidence.source_type is not None
        elif part.provenance_type == ProvenanceType.UNAVAILABLE:
            assert part.source_evidence is None

    # Verify no fabricated provenance is produced where TOM does not expose it
    for table in canonical_model.tables:
        assert hasattr(table, 'provenance')
        assert table.provenance is None
    for col in canonical_model.columns:
        assert hasattr(col, 'provenance')
        assert col.provenance is None
    for measure in canonical_model.measures:
        assert hasattr(measure, 'provenance')
        assert measure.provenance is None
    for rel in canonical_model.relationships:
        assert hasattr(rel, 'provenance')
        assert rel.provenance is None
