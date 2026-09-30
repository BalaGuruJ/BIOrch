import json
from .canonical_entities import PowerBICanonicalModel

def serialize(model: PowerBICanonicalModel) -> str:
    data = {
        "tables": [{"id": t.id, "name": t.name} for t in model.tables],
        "columns": [{"id": c.id, "name": c.name, "table_id": c.table_id, "data_type": c.data_type} for c in model.columns],
        "measures": [{"id": m.id, "name": m.name, "table_id": m.table_id, "expression": m.expression} for m in model.measures],
        "relationships": [{"id": r.id, "from_column_id": r.from_column_id, "to_column_id": r.to_column_id} for r in model.relationships]
    }
    return json.dumps(data, indent=2, sort_keys=True)
