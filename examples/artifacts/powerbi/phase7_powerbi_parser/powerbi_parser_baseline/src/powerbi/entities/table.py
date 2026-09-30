from dataclasses import dataclass, field
from typing import List, Optional, Union, Literal
from .common import BaseEntity

@dataclass(kw_only=True)
class Column(BaseEntity):
    data_type: str
    is_hidden: bool
    format_string: Optional[str] = None
    summarize_by: Optional[str] = None
    source_column: Optional[str] = None
    lineage_tag: Optional[str] = None

@dataclass(kw_only=True)
class CalculatedColumn(Column):
    expression: str  # DAX expression

@dataclass(kw_only=True)
class Measure(BaseEntity):
    expression: str  # DAX expression
    format_string: Optional[str] = None
    display_folder: Optional[str] = None
    lineage_tag: Optional[str] = None
    doc_comment: Optional[str] = None

@dataclass(kw_only=True)
class HierarchyLevel(BaseEntity):
    column_id: str # Reference to the source column
    lineage_tag: Optional[str] = None

@dataclass(kw_only=True)
class Hierarchy(BaseEntity):
    levels: List[HierarchyLevel] = field(default_factory=list)
    lineage_tag: Optional[str] = None

@dataclass(kw_only=True)
class MExpression:
    kind: Literal['m']
    expression: str

@dataclass(kw_only=True)
class Partition(BaseEntity):
    source: MExpression

@dataclass(kw_only=True)
class CalculationItem(BaseEntity):
    expression: str  # DAX expression
    format_string_definition: Optional[str] = None

@dataclass(kw_only=True)
class CalculationGroup(BaseEntity):
    precedence: int
    items: List[CalculationItem] = field(default_factory=list)

@dataclass(kw_only=True)
class Table(BaseEntity):
    columns: List[Union[Column, CalculatedColumn]] = field(default_factory=list)
    measures: List[Measure] = field(default_factory=list)
    hierarchies: List[Hierarchy] = field(default_factory=list)
    partitions: List[Partition] = field(default_factory=list)
    calculation_group: Optional[CalculationGroup] = None
    lineage_tag: Optional[str] = None
