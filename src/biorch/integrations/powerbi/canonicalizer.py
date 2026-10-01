import hashlib
from .canonical_entities import (
    PowerBICanonicalModel, CanonicalTable, CanonicalColumn,
    CanonicalMeasure, CanonicalRelationship, CanonicalPartition,
    CanonicalHierarchy, CanonicalHierarchyLevel,
    CanonicalCalculationGroup, CanonicalCalculationItem,
    CanonicalAnnotation, SourceEvidence, ProvenanceType,
    Cardinality, CrossFilteringBehavior
)

def _deterministic_id(parent_id: str, name: str) -> str:
    return hashlib.sha256(f"{parent_id}:{name}".encode()).hexdigest()

def _map_annotations(tom_obj) -> tuple[CanonicalAnnotation, ...]:
    if not hasattr(tom_obj, 'Annotations'):
        return ()
    return tuple(CanonicalAnnotation(name=a.Name, value=a.Value) for a in sorted(tom_obj.Annotations, key=lambda a: a.Name))

def _map_cardinality(tom_card) -> Cardinality:
    s = str(tom_card)
    if "OneToOne" in s: return Cardinality.ONE_TO_ONE
    if "OneToMany" in s: return Cardinality.ONE_TO_MANY
    if "ManyToOne" in s: return Cardinality.MANY_TO_ONE
    if "ManyToMany" in s: return Cardinality.MANY_TO_MANY
    return Cardinality.UNKNOWN

def _map_cross_filter(tom_cf) -> CrossFilteringBehavior:
    s = str(tom_cf)
    if "OneDirection" in s: return CrossFilteringBehavior.ONE_DIRECTION
    if "BothDirections" in s: return CrossFilteringBehavior.BOTH_DIRECTIONS
    return CrossFilteringBehavior.AUTOMATIC

def canonicalize(parsed_model) -> PowerBICanonicalModel:
    model_id = "model" # Root identity
    tables = []
    columns = []
    measures = []
    relationships = []
    partitions = []
    hierarchies = []
    calculation_groups = []
    
    for table in sorted(parsed_model.Model.Tables, key=lambda t: t.Name):
        table_id = _deterministic_id(model_id, table.Name)
        tables.append(CanonicalTable(
            id=table_id, name=table.Name, 
            annotations=_map_annotations(table),
            lineage_metadata=getattr(table, 'LineageTag', None)
        ))
        
        for col in sorted(table.Columns, key=lambda c: c.Name):
            is_calc = (str(col.Type) == "Calculated")
            columns.append(CanonicalColumn(
                id=_deterministic_id(table_id, col.Name),
                name=col.Name, 
                table_id=table_id,
                data_type=str(col.DataType) if hasattr(col, 'DataType') else "Unknown",
                is_calculated=is_calc,
                expression=col.Expression if is_calc else None,
                annotations=_map_annotations(col),
                lineage_metadata=getattr(col, 'LineageTag', None)
            ))
            
        for measure in sorted(table.Measures, key=lambda m: m.Name):
            measures.append(CanonicalMeasure(
                id=_deterministic_id(table_id, measure.Name),
                name=measure.Name,
                table_id=table_id,
                expression=measure.Expression,
                annotations=_map_annotations(measure),
                lineage_metadata=getattr(measure, 'LineageTag', None)
            ))
            
        for part in sorted(table.Partitions, key=lambda p: p.Name):
            source_evidence = None
            provenance = ProvenanceType.SUPPORTED
            
            if hasattr(part, 'Source') and part.Source:
                try:
                    src_type = str(part.SourceType)
                    src_expr = getattr(part.Source, 'Expression', None)
                    source_evidence = SourceEvidence(
                        source_file="Unknown",
                        source_structure=part.Name,
                        source_locator=src_expr or "N/A",
                        source_attributes={"source_type": src_type},
                        evidence_type=EvidenceType.SEMANTIC_MODEL
                    )
                except Exception:
                    provenance = ProvenanceType.UNRESOLVED
            else:
                provenance = ProvenanceType.UNAVAILABLE
                
            partitions.append(CanonicalPartition(
                id=_deterministic_id(table_id, part.Name),
                name=part.Name,
                table_id=table_id,
                source_evidence=source_evidence,
                provenance_type=provenance
            ))

        for hier in sorted(table.Hierarchies, key=lambda h: h.Name):
            hier_id = _deterministic_id(table_id, hier.Name)
            levels = []
            # Sort levels by Ordinal
            sorted_levels = sorted(hier.Levels, key=lambda l: l.Ordinal)
            for i, level in enumerate(sorted_levels):
                levels.append(CanonicalHierarchyLevel(
                    id=_deterministic_id(hier_id, level.Name),
                    hierarchy_id=hier_id,
                    column_id=_deterministic_id(table_id, level.Column.Name),
                    ordinal=i
                ))
            hierarchies.append(CanonicalHierarchy(
                id=hier_id,
                table_id=table_id,
                name=hier.Name,
                levels=tuple(levels),
                annotations=_map_annotations(hier)
            ))

    raw_calc_groups = []
    for table in sorted(parsed_model.Model.Tables, key=lambda t: t.Name):
        cg = getattr(table, 'CalculationGroup', None)
        if cg is not None:
            cg_name = getattr(cg, 'Name', None) or table.Name
            raw_calc_groups.append((cg_name, cg.CalculationItems))

    if hasattr(parsed_model.Model, 'CalculationGroups'):
        for calc_group in sorted(parsed_model.Model.CalculationGroups, key=lambda cg: cg.Name):
            if not any(cg_name == calc_group.Name for cg_name, _ in raw_calc_groups):
                raw_calc_groups.append((calc_group.Name, calc_group.CalculationItems))

    for cg_name, calc_items in sorted(raw_calc_groups, key=lambda x: x[0]):
        cg_id = _deterministic_id(model_id, cg_name)
        items = []
        # Sort items by Ordinal
        sorted_items = sorted(calc_items, key=lambda ci: ci.Ordinal)
        for i, item in enumerate(sorted_items):
            items.append(CanonicalCalculationItem(
                id=_deterministic_id(cg_id, item.Name),
                calculation_group_id=cg_id,
                name=item.Name,
                expression=item.Expression,
                ordinal=i
            ))
        calculation_groups.append(CanonicalCalculationGroup(
            id=cg_id,
            name=cg_name,
            items=tuple(items)
        ))
    
    for rel in sorted(parsed_model.Model.Relationships, key=lambda r: _deterministic_id(model_id, f"{r.FromTable.Name}:{r.FromColumn.Name}->{r.ToTable.Name}:{r.ToColumn.Name}")):
        from_table = rel.FromTable.Name
        to_table = rel.ToTable.Name
        from_col = rel.FromColumn.Name
        to_col = rel.ToColumn.Name
        
        # ID generation based on from/to table/column names
        rel_id = _deterministic_id(model_id, f"{from_table}:{from_col}->{to_table}:{to_col}")
        
        relationships.append(CanonicalRelationship(
            id=rel_id,
            from_table_id=_deterministic_id(model_id, from_table),
            from_column_id=_deterministic_id(_deterministic_id(model_id, from_table), from_col),
            to_table_id=_deterministic_id(model_id, to_table),
            to_column_id=_deterministic_id(_deterministic_id(model_id, to_table), to_col),
            is_active=rel.IsActive,
            cardinality=_map_cardinality(rel.FromCardinality),
            cross_filter_direction=_map_cross_filter(rel.CrossFilteringBehavior),
            annotations=_map_annotations(rel),
            lineage_metadata=getattr(rel, 'LineageTag', None)
        ))
    
    return PowerBICanonicalModel(
        tables=tuple(tables),
        columns=tuple(columns),
        measures=tuple(measures),
        relationships=tuple(relationships),
        partitions=tuple(partitions),
        hierarchies=tuple(hierarchies),
        calculation_groups=tuple(calculation_groups)
    )
