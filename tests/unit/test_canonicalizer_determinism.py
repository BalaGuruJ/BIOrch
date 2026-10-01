import pytest
from unittest.mock import MagicMock
from src.biorch.integrations.powerbi.canonicalizer import canonicalize
from src.biorch.integrations.powerbi.canonical_entities import CanonicalHierarchyLevel, CanonicalCalculationItem

# Mocking the complex nested TOM structure
def create_mock_table(name, hierarchies, lineage_tag="test-lineage-tag"):
    table = MagicMock()
    table.Name = name
    table.Hierarchies = hierarchies
    table.Columns = []
    table.Measures = []
    table.Partitions = []
    table.Annotations = []
    table.LineageTag = lineage_tag
    table.CalculationGroup = None
    return table

def create_mock_hierarchy(name, levels):
    hier = MagicMock()
    hier.Name = name
    hier.Levels = levels
    hier.Annotations = []
    return hier

def create_mock_level(name, ordinal, col_name):
    level = MagicMock()
    level.Name = name
    level.Ordinal = ordinal
    column = MagicMock()
    column.Name = col_name
    level.Column = column
    return level

def create_mock_calc_group(name, items):
    cg = MagicMock()
    cg.Name = name
    cg.CalculationItems = items
    return cg

def create_mock_calc_item(name, ordinal, expression):
    item = MagicMock()
    item.Name = name
    item.Ordinal = ordinal
    item.Expression = expression
    return item

def test_hierarchy_determinism():
    # Model A: Ordinal order [1, 0, 2]
    l1_a = create_mock_level("Level1", 1, "Col1")
    l0_a = create_mock_level("Level0", 0, "Col0")
    l2_a = create_mock_level("Level2", 2, "Col2")
    h_a = create_mock_hierarchy("HierA", [l1_a, l0_a, l2_a])
    table_a = create_mock_table("TableA", [h_a])
    model_a = MagicMock()
    model_a.Tables = [table_a]
    model_a.CalculationGroups = []
    model_a.Relationships = []

    # Model B: Ordinal order [2, 0, 1]
    l1_b = create_mock_level("Level1", 1, "Col1")
    l0_b = create_mock_level("Level0", 0, "Col0")
    l2_b = create_mock_level("Level2", 2, "Col2")
    h_b = create_mock_hierarchy("HierA", [l2_b, l0_b, l1_b]) # Same name: HierA
    table_b = create_mock_table("TableA", [h_b]) # Same name: TableA
    model_b = MagicMock()
    model_b.Tables = [table_b]
    model_b.CalculationGroups = []
    model_b.Relationships = []

    parsed_a = MagicMock()
    parsed_a.Model = model_a
    parsed_b = MagicMock()
    parsed_b.Model = model_b

    canonical_a = canonicalize(parsed_a)
    canonical_b = canonicalize(parsed_b)

    # Assert models are identical
    assert canonical_a == canonical_b

    # Additional assertions
    hier = canonical_a.hierarchies[0]
    assert len(hier.levels) == 3
    assert [l.ordinal for l in hier.levels] == [0, 1, 2]

def test_calculation_items_determinism():
    # Model A: Ordinal order [1, 0, 2]
    i1_a = create_mock_calc_item("Item1", 1, "Expr1")
    i0_a = create_mock_calc_item("Item0", 0, "Expr0")
    i2_a = create_mock_calc_item("Item2", 2, "Expr2")
    cg_a = create_mock_calc_group("CGA", [i1_a, i0_a, i2_a])
    model_a = MagicMock()
    model_a.Tables = []
    model_a.CalculationGroups = [cg_a]
    model_a.Relationships = []

    # Model B: Ordinal order [2, 0, 1]
    i1_b = create_mock_calc_item("Item1", 1, "Expr1")
    i0_b = create_mock_calc_item("Item0", 0, "Expr0")
    i2_b = create_mock_calc_item("Item2", 2, "Expr2")
    cg_b = create_mock_calc_group("CGA", [i2_b, i0_b, i1_b]) # Same name: CGA
    model_b = MagicMock()
    model_b.Tables = []
    model_b.CalculationGroups = [cg_b]
    model_b.Relationships = []

    parsed_a = MagicMock()
    parsed_a.Model = model_a
    parsed_b = MagicMock()
    parsed_b.Model = model_b

    canonical_a = canonicalize(parsed_a)
    canonical_b = canonicalize(parsed_b)

    # Assert models are identical
    assert canonical_a == canonical_b

    # Additional assertions
    cg = canonical_a.calculation_groups[0]
    assert len(cg.items) == 3
    assert [i.ordinal for i in cg.items] == [0, 1, 2]
