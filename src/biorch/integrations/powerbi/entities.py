from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Mapping, Optional, Any

class EvidenceType(Enum):
    SEMANTIC_MODEL = auto()
    TABLE = auto()
    COLUMN = auto()
    MEASURE = auto()
    RELATIONSHIP = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class SourceEvidence:
    source_file: str
    source_structure: str
    source_locator: str
    source_attributes: Mapping[str, Any] = field(default_factory=dict)
    evidence_type: EvidenceType = EvidenceType.UNKNOWN
