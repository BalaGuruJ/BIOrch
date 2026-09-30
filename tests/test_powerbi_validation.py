import pytest
from src.biorch.integrations.powerbi.adapter import PowerBIAdapter
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.validator import validate, ValidationError
from src.biorch.integrations.powerbi.canonical_entities import (
    PowerBICanonicalModel, CanonicalTable, CanonicalColumn,
    CanonicalMeasure, CanonicalRelationship, CanonicalPartition,
    CanonicalHierarchy, CanonicalHierarchyLevel,
    ProvenanceType, Cardinality, CrossFilteringBehavior
)

def test_adventure_works_positive_validation():
    model_dir = "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"
    adapter = PowerBIAdapter()
    parsed_model = adapter.load_model(model_dir)
    canonical_model = canonicalize(parsed_model)
    
    # Should not raise any ValidationError
    validate(canonical_model)

def test_validation_duplicate_table_id():
    t1 = CanonicalTable(id="tbl1", name="Table1")
    t2 = CanonicalTable(id="tbl1", name="Table2") # Duplicate ID
    model = PowerBICanonicalModel(
        tables=(t1, t2),
        columns=(),
        measures=(),
        relationships=(),
        partitions=(),
        hierarchies=(),
        calculation_groups=()
    )
    with pytest.raises(ValidationError, match="Duplicate Table ID"):
        validate(model)

def test_validation_dangling_column_table_reference():
    t1 = CanonicalTable(id="tbl1", name="Table1")
    c1 = CanonicalColumn(id="col1", name="Col1", table_id="tbl_missing", data_type="Int64", is_calculated=False, expression=None)
    model = PowerBICanonicalModel(
        tables=(t1,),
        columns=(c1,),
        measures=(),
        relationships=(),
        partitions=(),
        hierarchies=(),
        calculation_groups=()
    )
    with pytest.raises(ValidationError, match="references non-existent table"):
        validate(model)

def test_validation_relationship_parent_inconsistency():
    t1 = CanonicalTable(id="tbl1", name="Table1")
    t2 = CanonicalTable(id="tbl2", name="Table2")
    c1 = CanonicalColumn(id="col1", name="Col1", table_id="tbl1", data_type="Int64", is_calculated=False, expression=None)
    c2 = CanonicalColumn(id="col2", name="Col2", table_id="tbl2", data_type="Int64", is_calculated=False, expression=None)
    
    # Rel says from_table is tbl2, but col1 belongs to tbl1
    rel = CanonicalRelationship(
        id="rel1",
        from_table_id="tbl2", # Mismatch!
        from_column_id="col1",
        to_table_id="tbl2",
        to_column_id="col2",
        is_active=True,
        cardinality=Cardinality.MANY_TO_ONE,
        cross_filter_direction=CrossFilteringBehavior.ONE_DIRECTION
    )
    model = PowerBICanonicalModel(
        tables=(t1, t2),
        columns=(c1, c2),
        measures=(),
        relationships=(rel,),
        partitions=(),
        hierarchies=(),
        calculation_groups=()
    )
    with pytest.raises(ValidationError, match="from_column does not belong to from_table"):
        validate(model)

def test_validation_hierarchy_level_parent_inconsistency():
    t1 = CanonicalTable(id="tbl1", name="Table1")
    t2 = CanonicalTable(id="tbl2", name="Table2")
    c1 = CanonicalColumn(id="col1", name="Col1", table_id="tbl1", data_type="Int64", is_calculated=False, expression=None)
    
    # Level references col1 (tbl1), but Hierarchy belongs to tbl2
    level = CanonicalHierarchyLevel(id="lvl1", hierarchy_id="h1", column_id="col1", ordinal=0)
    hier = CanonicalHierarchy(id="h1", table_id="tbl2", name="Hier1", levels=(level,))
    
    model = PowerBICanonicalModel(
        tables=(t1, t2),
        columns=(c1,),
        measures=(),
        relationships=(),
        partitions=(),
        hierarchies=(hier,),
        calculation_groups=()
    )
    with pytest.raises(ValidationError, match="does not belong to hierarchy table"):
        validate(model)

def test_validation_hierarchy_level_ordinal_mismatch():
    t1 = CanonicalTable(id="tbl1", name="Table1")
    c1 = CanonicalColumn(id="col1", name="Col1", table_id="tbl1", data_type="Int64", is_calculated=False, expression=None)
    
    # Level ordinal is 1, expected 0
    level = CanonicalHierarchyLevel(id="lvl1", hierarchy_id="h1", column_id="col1", ordinal=1)
    hier = CanonicalHierarchy(id="h1", table_id="tbl1", name="Hier1", levels=(level,))
    
    model = PowerBICanonicalModel(
        tables=(t1,),
        columns=(c1,),
        measures=(),
        relationships=(),
        partitions=(),
        hierarchies=(hier,),
        calculation_groups=()
    )
    with pytest.raises(ValidationError, match="non-deterministic ordinal"):
        validate(model)
