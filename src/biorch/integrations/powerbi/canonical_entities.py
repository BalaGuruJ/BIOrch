from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CanonicalTable:
    id: str
    name: str

@dataclass(frozen=True)
class CanonicalColumn:
    id: str
    name: str
    table_id: str
    data_type: str

@dataclass(frozen=True)
class CanonicalMeasure:
    id: str
    name: str
    table_id: str
    expression: str

@dataclass(frozen=True)
class CanonicalRelationship:
    id: str
    from_column_id: str
    to_column_id: str

@dataclass(frozen=True)
class PowerBICanonicalModel:
    tables: tuple[CanonicalTable, ...]
    columns: tuple[CanonicalColumn, ...]
    measures: tuple[CanonicalMeasure, ...]
    relationships: tuple[CanonicalRelationship, ...]
