import json
from .canonical_entities import PowerBICanonicalModel

def serialize(model: PowerBICanonicalModel) -> str:
    def ann_to_dict(anns):
        return [{"name": a.name, "value": a.value} for a in anns]
    
    data = {
        "tables": [{"id": t.id, "name": t.name, "annotations": ann_to_dict(t.annotations)} for t in model.tables],
        "columns": [
            {
                "id": c.id, "name": c.name, "table_id": c.table_id, "data_type": c.data_type,
                "is_calculated": c.is_calculated, "expression": c.expression, "annotations": ann_to_dict(c.annotations)
            } for c in model.columns
        ],
        "measures": [
            {"id": m.id, "name": m.name, "table_id": m.table_id, "expression": m.expression, "annotations": ann_to_dict(m.annotations)}
            for m in model.measures
        ],
        "relationships": [
            {
                "id": r.id, "from_table_id": r.from_table_id, "from_column_id": r.from_column_id,
                "to_table_id": r.to_table_id, "to_column_id": r.to_column_id, "is_active": r.is_active,
                "cardinality": r.cardinality.name, "cross_filter_direction": r.cross_filter_direction.name,
                "annotations": ann_to_dict(r.annotations)
            } for r in model.relationships
        ],
        "partitions": [
            {
                "id": p.id, "name": p.name, "table_id": p.table_id,
                "source_evidence": {"source_type": p.source_evidence.source_type, "expression": p.source_evidence.expression} if p.source_evidence else None,
                "provenance_type": p.provenance_type.name
            } for p in model.partitions
        ],
        "hierarchies": [
            {
                "id": h.id, "name": h.name, "table_id": h.table_id,
                "levels": [{"id": l.id, "hierarchy_id": l.hierarchy_id, "column_id": l.column_id, "ordinal": l.ordinal} for l in h.levels],
                "annotations": ann_to_dict(h.annotations)
            } for h in model.hierarchies
        ],
        "calculation_groups": [
            {
                "id": cg.id, "name": cg.name,
                "items": [{"id": i.id, "name": i.name, "expression": i.expression, "ordinal": i.ordinal} for i in cg.items]
            } for cg in model.calculation_groups
        ]
    }
    return json.dumps(data, indent=2, sort_keys=True)
