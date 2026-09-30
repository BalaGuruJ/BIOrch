from .canonical_entities import (
    PowerBICanonicalModel, CanonicalTable, CanonicalColumn,
    CanonicalMeasure, CanonicalRelationship
)

def canonicalize(parsed_model) -> PowerBICanonicalModel:
    tables = []
    columns = []
    measures = []
    
    for table in parsed_model.tables:
        tables.append(CanonicalTable(id=table.id, name=table.name))
        
        for col in table.columns:
            columns.append(CanonicalColumn(
                id=col.id, name=col.name, 
                table_id=table.id, data_type=col.data_type
            ))
            
        for measure in table.measures:
            measures.append(CanonicalMeasure(
                id=measure.id, name=measure.name,
                table_id=table.id, expression=measure.expression
            ))
            
    # Assuming parsed_model.relationships exists (will need to check adapter)
    relationships = []
    
    return PowerBICanonicalModel(
        tables=tuple(tables),
        columns=tuple(columns),
        measures=tuple(measures),
        relationships=tuple(relationships)
    )
