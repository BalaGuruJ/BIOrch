
import pytest
import json
from biorch.integrations.comparison.comparison_agent import ComparisonAgent
from biorch.integrations.comparison.models import ComparisonState

def test_comparison_determinism():
    # Setup identical inputs
    tableau_metadata = {"workbook_metadata": {"entities": {"tables": [], "columns": []}, "relationships": {"logical_relationships": []}}}
    powerbi_metadata = {"tables": [], "columns": [], "relationships": []}
    
    agent1 = ComparisonAgent(tableau_metadata, powerbi_metadata)
    agent2 = ComparisonAgent(tableau_metadata, powerbi_metadata)
    
    report1 = agent1.compare()
    report2 = agent2.compare()
    
    # Check that report metadata is different (as expected), but content is identical
    assert report1.table_comparison == report2.table_comparison
    assert report1.column_comparison == report2.column_comparison
    assert report1.relationship_comparison == report2.relationship_comparison

def test_tableau_table_pair_identity():
    # Tableau Table-Pair should be commutative (T1, T2) == (T2, T1)
    tableau_metadata = {
        "workbook_metadata": {
            "entities": {"tables": [], "columns": []},
            "relationships": {
                "logical_relationships": [
                    {"datasource_id": "DS1", "first_table_id": "T1", "second_table_id": "T2", "expression_raw": "E"},
                    {"datasource_id": "DS1", "first_table_id": "T2", "second_table_id": "T1", "expression_raw": "E"}
                ]
            }
        }
    }
    powerbi_metadata = {"tables": [], "columns": [], "relationships": []}
    
    agent = ComparisonAgent(tableau_metadata, powerbi_metadata)
    relationships = agent._get_tableau_relationships()
    
    # Should only have 1 relationship because it's commutative
    assert len(relationships) == 1
    assert "DS1:T1:T2" in relationships

def test_tableau_expression_opacity():
    # expression_raw should be preserved as-is
    tableau_metadata = {
        "workbook_metadata": {
            "entities": {"tables": [], "columns": []},
            "relationships": {
                "logical_relationships": [
                    {"datasource_id": "DS1", "first_table_id": "T1", "second_table_id": "T2", "expression_raw": "complex-expression-123"}
                ]
            }
        }
    }
    powerbi_metadata = {"tables": [], "columns": [], "relationships": []}
    
    agent = ComparisonAgent(tableau_metadata, powerbi_metadata)
    relationships = agent._get_tableau_relationships()
    
    assert relationships["DS1:T1:T2"]["expression_raw"] == "complex-expression-123"

from jsonschema import validate, ValidationError

def test_comparison_report_schema_validation():
    with open('schemas/comparison_report.schema.json', 'r') as f:
        schema = json.load(f)

    # Basic valid structure
    report = {
        "report_metadata": {
            "report_id": "r1",
            "timestamp": "2026-10-06T10:00:00Z",
            "tableau_source": "t1",
            "powerbi_source": "p1"
        },
        "table_comparison": [],
        "column_comparison": [],
        "relationship_comparison": [],
        "summary": {"matched": 0, "different": 0, "tableau_only": 0, "powerbi_only": 0}
    }

    # Helper function
    def validate_report(t_key, p_key, state):
        entry = {"state": state, "tableau_key": t_key, "powerbi_key": p_key}
        report["table_comparison"] = [entry]
        report["column_comparison"] = [entry]
        report["relationship_comparison"] = [entry]
        validate(instance=report, schema=schema)

    # 1. TABLEAU_ONLY
    validate_report("t1", None, "TABLEAU_ONLY")

    # 2. POWERBI_ONLY
    validate_report(None, "p1", "POWERBI_ONLY")

    # 3. MATCHED
    validate_report("t1", "p1", "MATCHED")

    # 4. DIFFERENT
    validate_report("t1", "p2", "DIFFERENT")
