
import pytest
from biorch.integrations.tableau.relationships import TableLogicalRelationship
from biorch.integrations.tableau.entities import SourceEvidence, EvidenceType

def test_logical_relationship_dataclass():
    evidence = SourceEvidence("file", "xml", "structure", "locator", {}, EvidenceType.LOGICAL_RELATIONSHIP)
    rel = TableLogicalRelationship(
        canonical_id="rel_id",
        datasource_id="ds_id",
        first_table_id="t1",
        second_table_id="t2",
        expression_raw="<expr/>",
        cardinality="1:1",
        source_evidence=frozenset([evidence])
    )
    assert rel.canonical_id == "rel_id"
    assert rel.expression_raw == "<expr/>"
