from .canonical_entities import PowerBICanonicalModel

def validate(model: PowerBICanonicalModel):
    table_ids = {t.id for t in model.tables}
    
    # Check for duplicate IDs (already enforced by set/dataclass/logic)
    
    # Check for unresolved table references in columns/measures
    for col in model.columns:
        if col.table_id not in table_ids:
            raise ValueError(f"Unresolved table reference: {col.table_id}")
            
    for measure in model.measures:
        if measure.table_id not in table_ids:
            raise ValueError(f"Unresolved table reference: {measure.table_id}")
            
    # Relationships
    col_ids = {c.id for c in model.columns}
    for rel in model.relationships:
        if rel.from_column_id not in col_ids:
            raise ValueError(f"Unresolved from_column reference: {rel.from_column_id}")
        if rel.to_column_id not in col_ids:
            raise ValueError(f"Unresolved to_column reference: {rel.to_column_id}")
