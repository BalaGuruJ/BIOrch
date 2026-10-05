from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ComparisonState(Enum):
    MATCHED = "MATCHED"
    TABLEAU_ONLY = "TABLEAU_ONLY"
    POWERBI_ONLY = "POWERBI_ONLY"
    DIFFERENT = "DIFFERENT"

@dataclass
class ComparisonResult:
    state: ComparisonState
    tableau_key: Optional[str]
    powerbi_key: Optional[str]

@dataclass
class ComparisonReport:
    report_id: str
    timestamp: str
    tableau_source: str
    powerbi_source: str
    table_comparison: List[ComparisonResult]
    column_comparison: List[ComparisonResult]
    relationship_comparison: List[ComparisonResult]
    summary: dict
    non_comparable: dict
