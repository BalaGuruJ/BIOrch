from .canonical_entities import (
    PowerBICanonicalModel, ProvenanceType, Cardinality, CrossFilteringBehavior
)

class ValidationError(ValueError):
    pass

def validate(model: PowerBICanonicalModel):
    # 1. Identity validation & Duplicate Detection
    def check_duplicates(entities, entity_name):
        seen_ids = set()
        for e in entities:
            if not e.id or not isinstance(e.id, str):
                raise ValidationError(f"{entity_name} has invalid or empty ID: {e.id}")
            if e.id in seen_ids:
                raise ValidationError(f"Duplicate {entity_name} ID detected: {e.id}")
            seen_ids.add(e.id)
        return seen_ids

    table_ids = check_duplicates(model.tables, "Table")
    col_map = {}
    for c in model.columns:
        if not c.id or not isinstance(c.id, str):
            raise ValidationError(f"Column has invalid or empty ID: {c.id}")
        if c.id in col_map:
            raise ValidationError(f"Duplicate Column ID detected: {c.id}")
        col_map[c.id] = c

    measure_ids = check_duplicates(model.measures, "Measure")
    part_ids = check_duplicates(model.partitions, "Partition")
    hier_map = {}
    for h in model.hierarchies:
        if not h.id or not isinstance(h.id, str):
            raise ValidationError(f"Hierarchy has invalid or empty ID: {h.id}")
        if h.id in hier_map:
            raise ValidationError(f"Duplicate Hierarchy ID detected: {h.id}")
        hier_map[h.id] = h

    rel_ids = check_duplicates(model.relationships, "Relationship")
    cg_map = {}
    for cg in model.calculation_groups:
        if not cg.id or not isinstance(cg.id, str):
            raise ValidationError(f"CalculationGroup has invalid or empty ID: {cg.id}")
        if cg.id in cg_map:
            raise ValidationError(f"Duplicate CalculationGroup ID detected: {cg.id}")
        cg_map[cg.id] = cg

    # 2. Referential integrity & Parent Consistency: Columns
    for col in model.columns:
        if col.table_id not in table_ids:
            raise ValidationError(f"Column {col.id} references non-existent table: {col.table_id}")
        if not isinstance(col.provenance_type, ProvenanceType):
            raise ValidationError(f"Column {col.id} has invalid provenance_type")
        if col.is_calculated and col.expression is not None and not isinstance(col.expression, str):
            raise ValidationError(f"Column {col.id} expression must be a string")

    # 3. Referential integrity: Measures
    for measure in model.measures:
        if measure.table_id not in table_ids:
            raise ValidationError(f"Measure {measure.id} references non-existent table: {measure.table_id}")
        if not isinstance(measure.expression, str):
            raise ValidationError(f"Measure {measure.id} expression must be a string")
        if not isinstance(measure.provenance_type, ProvenanceType):
            raise ValidationError(f"Measure {measure.id} has invalid provenance_type")

    # 4. Referential integrity: Partitions
    for part in model.partitions:
        if part.table_id not in table_ids:
            raise ValidationError(f"Partition {part.id} references non-existent table: {part.table_id}")
        if not isinstance(part.provenance_type, ProvenanceType):
            raise ValidationError(f"Partition {part.id} has invalid provenance_type")
        if part.provenance_type == ProvenanceType.UNAVAILABLE and part.source_evidence is not None:
            raise ValidationError(f"Partition {part.id} marked UNAVAILABLE but has source evidence")
        if part.source_evidence and part.source_evidence.expression is not None:
            if not isinstance(part.source_evidence.expression, str):
                raise ValidationError(f"Partition {part.id} source expression must be a string")

    # 5. Hierarchies & Levels
    for hier in model.hierarchies:
        if hier.table_id not in table_ids:
            raise ValidationError(f"Hierarchy {hier.id} references non-existent table: {hier.table_id}")
        level_ids = set()
        for idx, level in enumerate(hier.levels):
            if not level.id or not isinstance(level.id, str):
                raise ValidationError(f"HierarchyLevel has invalid or empty ID: {level.id}")
            if level.id in level_ids:
                raise ValidationError(f"Duplicate HierarchyLevel ID in hierarchy {hier.id}: {level.id}")
            level_ids.add(level.id)
            if level.hierarchy_id != hier.id:
                raise ValidationError(f"HierarchyLevel {level.id} hierarchy_id does not match parent")
            if level.column_id not in col_map:
                raise ValidationError(f"HierarchyLevel {level.id} references non-existent column: {level.column_id}")
            # Parent consistency: column must belong to hierarchy's table
            referenced_col = col_map[level.column_id]
            if referenced_col.table_id != hier.table_id:
                raise ValidationError(f"HierarchyLevel {level.id} column {referenced_col.id} does not belong to hierarchy table {hier.table_id}")
            if level.ordinal != idx:
                raise ValidationError(f"HierarchyLevel {level.id} has non-deterministic ordinal: {level.ordinal} (expected {idx})")

    # 6. Relationships
    for rel in model.relationships:
        if rel.from_table_id not in table_ids:
            raise ValidationError(f"Relationship {rel.id} from_table_id not found: {rel.from_table_id}")
        if rel.to_table_id not in table_ids:
            raise ValidationError(f"Relationship {rel.id} to_table_id not found: {rel.to_table_id}")
        if rel.from_column_id not in col_map:
            raise ValidationError(f"Relationship {rel.id} from_column_id not found: {rel.from_column_id}")
        if rel.to_column_id not in col_map:
            raise ValidationError(f"Relationship {rel.id} to_column_id not found: {rel.to_column_id}")
        
        # Parent consistency
        from_col = col_map[rel.from_column_id]
        if from_col.table_id != rel.from_table_id:
            raise ValidationError(f"Relationship {rel.id} from_column does not belong to from_table")
        to_col = col_map[rel.to_column_id]
        if to_col.table_id != rel.to_table_id:
            raise ValidationError(f"Relationship {rel.id} to_column does not belong to to_table")
            
        if not isinstance(rel.is_active, bool):
            raise ValidationError(f"Relationship {rel.id} is_active must be boolean")
        if not isinstance(rel.cardinality, Cardinality):
            raise ValidationError(f"Relationship {rel.id} has invalid cardinality")
        if not isinstance(rel.cross_filter_direction, CrossFilteringBehavior):
            raise ValidationError(f"Relationship {rel.id} has invalid cross_filter_direction")

    # 7. Calculation Groups
    for cg in model.calculation_groups:
        item_ids = set()
        for idx, item in enumerate(cg.items):
            if not item.id or not isinstance(item.id, str):
                raise ValidationError(f"CalculationItem has invalid or empty ID: {item.id}")
            if item.id in item_ids:
                raise ValidationError(f"Duplicate CalculationItem ID in group {cg.id}: {item.id}")
            item_ids.add(item.id)
            if item.calculation_group_id != cg.id:
                raise ValidationError(f"CalculationItem {item.id} calculation_group_id does not match parent")
            if not isinstance(item.expression, str):
                raise ValidationError(f"CalculationItem {item.id} expression must be a string")
            if item.ordinal != idx:
                raise ValidationError(f"CalculationItem {item.id} has non-deterministic ordinal: {item.ordinal}")
