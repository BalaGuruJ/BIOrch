from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkflowResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    NOT_EXECUTED = "NOT_EXECUTED"

class WorkflowResult(BaseModel):
    """
    Structured result of a workflow execution compliant with BIORCH-ORCH-001.
    """
    workflow_id: str = Field(..., description="Unique identifier for the workflow execution.")
    workflow_version: str = Field(default="1.0", description="Version of the executed workflow.")
    status: WorkflowResultStatus = Field(..., description="Terminal status of the workflow.")
    completed_tasks: List[str] = Field(default_factory=list, description="List of completed task/step identifiers.")
    failed_task: Optional[str] = Field(default=None, description="Identifier of the failed or rejected task/step, if any.")
    not_executed_tasks: List[str] = Field(default_factory=list, description="List of unexecuted task/step identifiers.")
    results: Dict[str, Any] = Field(default_factory=dict, description="Step outputs mapped by task identifier.")
    step_results: Dict[str, Any] = Field(default_factory=dict, description="Structured per-step results and statuses.")
    errors: List[str] = Field(default_factory=list, description="Structured errors encountered during validation or execution.")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Execution provenance metadata.")

    @property
    def completed_steps(self) -> List[str]:
        return self.completed_tasks

    @property
    def failed_step(self) -> Optional[str]:
        return self.failed_task

    @property
    def not_executed_steps(self) -> List[str]:
        return self.not_executed_tasks
