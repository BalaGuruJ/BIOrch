from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass(kw_only=True)
class Position:
    line: int
    col: int

@dataclass(kw_only=True)
class Range:
    start: Position
    end: Position

@dataclass(kw_only=True)
class Provenance:
    source_type: str  # 'TMDL' | 'PBIR'
    file: str
    range: Range

@dataclass(kw_only=True)
class BaseEntity:
    id: str  # Stable canonical ID (model-scoped)
    name: str  # Human-readable name
    provenance: Optional[Provenance] = None
    annotations: Dict[str, Any] = field(default_factory=dict)
