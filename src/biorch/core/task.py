from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    NOT_EXECUTED = "not_executed"

class Task(BaseModel):
    """
    Task Contract
    Represents work assigned to an agent.
    """
    task_id: str = Field(..., description="Unique identifier for this task.")
    objective: str = Field(..., description="The goal or instructions for the agent.")
    agent_id: str = Field(..., description="The ID of the agent assigned to this task.")
    inputs: Optional[Dict[str, Any]] = Field(default=None, description="Structured inputs required to perform the task.")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs that must complete before this task can start.")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context or tracking information.")
    status: TaskStatus = Field(..., description="Current execution status of the task.")
    is_parallel_eligible: bool = Field(
        default=False,
        description="Whether the task may participate in parallel dispatch when its dependencies are satisfied and workflow policy permits parallel execution."
    )
    is_essential: bool = Field(
        default=True,
        description="Whether failure or timeout of this task prevents successful workflow completion."
    )
