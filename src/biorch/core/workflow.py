from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .task import Task

class TerminationInfo(BaseModel):
    reason: str
    message: str

class Workflow(BaseModel):
    """
    Workflow Contract
    Represents orchestration state and dependencies.
    """
    workflow_id: str = Field(..., description="Unique identifier for the workflow execution.")
    version: str = Field(default="1.0", description="Version of the workflow definition.")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks in this workflow.")
    status: str = Field(..., description="Overall status of the workflow (e.g., pending, running, completed, failed).")
    current_state: Optional[Dict[str, Any]] = Field(default=None, description="The current state of the workflow context.")
    termination_info: Optional[TerminationInfo] = Field(default=None, description="Information regarding how and why the workflow ended.")
