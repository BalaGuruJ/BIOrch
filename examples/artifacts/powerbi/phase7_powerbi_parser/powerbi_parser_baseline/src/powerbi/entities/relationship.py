from dataclasses import dataclass
from typing import Optional, Literal
from .common import Provenance

@dataclass(kw_only=True)
class Relationship:
    id: str  # Stable canonical ID (model-scoped: 'rel:from_table_id:from_col_id:to_table_id:to_col_id')
    from_table_id: str
    from_column_id: str
    to_table_id: str
    to_column_id: str
    is_active: bool
    cross_filtering_behavior: Literal['singleDirection', 'bothDirections']
    cardinality: Literal['oneToOne', 'oneToMany', 'manyToOne', 'manyToMany']
    lineage_tag: Optional[str] = None
    provenance: Optional[Provenance] = None
