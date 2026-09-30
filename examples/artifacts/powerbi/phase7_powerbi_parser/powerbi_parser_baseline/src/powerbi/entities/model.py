from dataclasses import dataclass, field
from typing import List, Optional
from .common import BaseEntity
from .table import Table, Column
from .relationship import Relationship

@dataclass(kw_only=True)
class Model(BaseEntity):
    tables: List[Table] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    culture: Optional[str] = None

    def get_table(self, table_id: str) -> Optional[Table]:
        for table in self.tables:
            if table.id == table_id:
                return table
        return None

    def get_column(self, column_id: str) -> Optional[Column]:
        # IDs are expected to be table_id:column_name
        parts = column_id.split(':')
        if len(parts) < 2:
            return None
        
        table_id = ":".join(parts[:-1]) # Handle IDs that might contain colons themselves
        table = self.get_table(table_id)
        if not table:
            return None
            
        for column in table.columns:
            if column.id == column_id:
                return column
        return None
