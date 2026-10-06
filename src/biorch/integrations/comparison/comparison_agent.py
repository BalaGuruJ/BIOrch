import json
import jsonschema
from datetime import datetime, timezone
import uuid
from enum import Enum
from typing import List, Dict, Set
from biorch.integrations.comparison.models import ComparisonState, ComparisonResult, ComparisonReport, ReportMetadata
from dataclasses import asdict

class ComparisonAgent:
    def __init__(self, tableau_metadata: dict, powerbi_metadata: dict, schema_path: str = "schemas/comparison_report.schema.json"):
        self.tableau_metadata = tableau_metadata
        self.powerbi_metadata = powerbi_metadata
        self.schema_path = schema_path
        self.tableau_tables = self._get_tableau_tables()
        self.pbi_tables = self._get_pbi_tables()
        self.tableau_columns = self._get_tableau_columns()
        self.pbi_columns = self._get_pbi_columns()
        self.tableau_relationships = self._get_tableau_relationships()
        self.pbi_relationships = self._get_pbi_relationships()
        
    def _validate(self, report: ComparisonReport):
        with open(self.schema_path, "r") as f:
            schema = json.load(f)
        
        # Need to convert dataclasses to dict for jsonschema validation
        def dataclass_to_dict(obj):
            if isinstance(obj, (list, tuple)):
                return [dataclass_to_dict(i) for i in obj]
            if isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            if hasattr(obj, "__dataclass_fields__"):
                return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
            if isinstance(obj, Enum):
                return obj.value
            return obj
            
        data = dataclass_to_dict(report)
        jsonschema.validate(instance=data, schema=schema)

    def _get_tableau_tables(self) -> Dict[str, dict]:
        return {t["relation_name"] + ":" + t["connection_name"]: t 
                for t in self.tableau_metadata.get("workbook_metadata", {}).get("entities", {}).get("tables", [])}

    def _get_pbi_tables(self) -> Dict[str, dict]:
        return {t["name"]: t for t in self.powerbi_metadata.get("tables", [])}

    def _get_tableau_columns(self) -> Dict[str, dict]:
        return {c["parent_name"] + ":" + c["remote_name"]: c 
                for c in self.tableau_metadata.get("workbook_metadata", {}).get("entities", {}).get("columns", [])}

    def _get_pbi_columns(self) -> Dict[str, dict]:
        table_map = {t["id"]: t["name"] for t in self.powerbi_metadata.get("tables", [])}
        return {table_map.get(c["table_id"], "unknown") + ":" + c["name"]: c for c in self.powerbi_metadata.get("columns", [])}

    def _get_tableau_relationships(self) -> Dict[str, dict]:
        # Tableau relationships: Table-Pair grain, commutative, expression_raw opaque.
        relationships = {}
        workbook_metadata = self.tableau_metadata.get("workbook_metadata", {})
        relationships_data = workbook_metadata.get("relationships", {})
        logical_relationships = relationships_data.get("logical_relationships", [])
        
        for r in logical_relationships:
            # Deterministic, commutative Table-Pair key
            t1 = r["first_table_id"]
            t2 = r["second_table_id"]
            if t1 > t2:
                t1, t2 = t2, t1
            key = f"{r['datasource_id']}:{t1}:{t2}"
            relationships[key] = r
        return relationships

    def _get_pbi_relationships(self) -> Dict[str, dict]:
        table_map = {t["id"]: t["name"] for t in self.powerbi_metadata.get("tables", [])}
        col_map = {c["id"]: c["name"] for c in self.powerbi_metadata.get("columns", [])}
        
        relationships = {}
        for r in self.powerbi_metadata.get("relationships", []):
            key = f"{table_map.get(r['from_table_id'], 'unknown')}:{col_map.get(r['from_column_id'], 'unknown')}->{table_map.get(r['to_table_id'], 'unknown')}:{col_map.get(r['to_column_id'], 'unknown')}"
            relationships[key] = r
        return relationships

    def compare(self) -> ComparisonReport:
        # 1. Compare Tables
        table_keys_t = set(self.tableau_tables.keys())
        table_keys_p = set(self.pbi_tables.keys())
        
        table_results = []
        for k in sorted(table_keys_t.union(table_keys_p)):
            if k in table_keys_t and k in table_keys_p:
                state = ComparisonState.MATCHED
            elif k in table_keys_t:
                state = ComparisonState.TABLEAU_ONLY
            else:
                state = ComparisonState.POWERBI_ONLY
            table_results.append(ComparisonResult(state, k if k in table_keys_t else None, k if k in table_keys_p else None))

        # 2. Compare Columns
        col_keys_t = set(self.tableau_columns.keys())
        col_keys_p = set(self.pbi_columns.keys())
        
        col_results = []
        for k in sorted(col_keys_t.union(col_keys_p)):
            if k in col_keys_t and k in col_keys_p:
                state = ComparisonState.MATCHED
            elif k in col_keys_t:
                state = ComparisonState.TABLEAU_ONLY
            else:
                state = ComparisonState.POWERBI_ONLY
            col_results.append(ComparisonResult(state, k if k in col_keys_t else None, k if k in col_keys_p else None))

        # 3. Compare Relationships
        rel_keys_t = set(self.tableau_relationships.keys())
        rel_keys_p = set(self.pbi_relationships.keys())
        
        rel_results = []
        for k in sorted(rel_keys_t.union(rel_keys_p)):
            if k in rel_keys_t and k in rel_keys_p:
                state = ComparisonState.MATCHED
            elif k in rel_keys_t:
                state = ComparisonState.TABLEAU_ONLY
            else:
                state = ComparisonState.POWERBI_ONLY
            rel_results.append(ComparisonResult(state, k if k in rel_keys_t else None, k if k in rel_keys_p else None))

        # 4. Summary and Non-comparable
        summary = {
            "matched": len([r for r in table_results + col_results + rel_results if r.state == ComparisonState.MATCHED]),
            "different": len([r for r in table_results + col_results + rel_results if r.state == ComparisonState.DIFFERENT]),
            "tableau_only": len([r for r in table_results + col_results + rel_results if r.state == ComparisonState.TABLEAU_ONLY]),
            "powerbi_only": len([r for r in table_results + col_results + rel_results if r.state == ComparisonState.POWERBI_ONLY])
        }
        
        report = ComparisonReport(
            report_metadata=ReportMetadata(
                report_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                tableau_source="superstore",
                powerbi_source="adventureworks",
            ),
            table_comparison=table_results,
            column_comparison=col_results,
            relationship_comparison=rel_results,
            summary=summary,
            non_comparable={"tableau": ["CalculatedFields", "Worksheets"], "powerbi": ["DAX", "Measures"]}
        )
        
        # Validation
        self._validate(report)
        return report
