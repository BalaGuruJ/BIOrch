from dataclasses import dataclass, field
from typing import Mapping, Optional, Any
from enum import Enum, auto
from .entities import EvidenceType, SourceEvidence

class ProvenanceType(Enum):
    SUPPORTED = auto()
    UNSUPPORTED = auto()
    UNRESOLVED = auto()
    UNAVAILABLE = auto()
    INVALID = auto()

class Cardinality(Enum):
    ONE_TO_ONE = auto()
    ONE_TO_MANY = auto()
    MANY_TO_ONE = auto()
    MANY_TO_MANY = auto()
    UNKNOWN = auto()

class CrossFilteringBehavior(Enum):
    ONE_DIRECTION = auto()
    BOTH_DIRECTIONS = auto()
    AUTOMATIC = auto()

@dataclass(frozen=True)
class CanonicalAnnotation:
    name: str
    value: Optional[str]

@dataclass(frozen=True)
class CanonicalTable:
    id: str
    name: str
    annotations: tuple[CanonicalAnnotation, ...] = ()
    provenance: Optional[SourceEvidence] = None
    lineage_metadata: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalColumn:
    id: str
    name: str
    table_id: str
    data_type: str
    is_calculated: bool
    expression: Optional[str]
    annotations: tuple[CanonicalAnnotation, ...] = ()
    provenance: Optional[SourceEvidence] = None
    lineage_metadata: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalMeasure:
    id: str
    name: str
    table_id: str
    expression: str
    annotations: tuple[CanonicalAnnotation, ...] = ()
    provenance: Optional[SourceEvidence] = None
    lineage_metadata: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalPartition:
    id: str
    name: str
    table_id: str
    source_evidence: Optional[SourceEvidence]
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalHierarchyLevel:
    id: str
    hierarchy_id: str
    column_id: str
    ordinal: int
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalHierarchy:
    id: str
    table_id: str
    name: str
    levels: tuple[CanonicalHierarchyLevel, ...]
    annotations: tuple[CanonicalAnnotation, ...] = ()
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalCalculationItem:
    id: str
    calculation_group_id: str
    name: str
    expression: str
    ordinal: int
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalCalculationGroup:
    id: str
    name: str
    items: tuple[CanonicalCalculationItem, ...]
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class CanonicalRelationship:
    id: str
    from_table_id: str
    from_column_id: str
    to_table_id: str
    to_column_id: str
    is_active: bool
    cardinality: Cardinality
    cross_filter_direction: CrossFilteringBehavior
    annotations: tuple[CanonicalAnnotation, ...] = ()
    provenance: Optional[SourceEvidence] = None
    lineage_metadata: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SUPPORTED

@dataclass(frozen=True)
class PowerBICanonicalModel:
    tables: tuple[CanonicalTable, ...]
    columns: tuple[CanonicalColumn, ...]
    measures: tuple[CanonicalMeasure, ...]
    relationships: tuple[CanonicalRelationship, ...]
    partitions: tuple[CanonicalPartition, ...]
    hierarchies: tuple[CanonicalHierarchy, ...]
    calculation_groups: tuple[CanonicalCalculationGroup, ...]
