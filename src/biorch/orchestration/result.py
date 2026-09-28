from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkflowResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    NOT_EXECUTED = "NOT_EXECUTED"

class WorkflowResult(BaseModel):
    workflow_id: str
    status: WorkflowResultStatus
    completed_tasks: List[str] = Field(default_factory=list)
    failed_task: Optional[str] = None
    not_executed_tasks: List[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
