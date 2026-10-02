from typing import List, Dict, Any
from pydantic import BaseModel, Field
from biorch.core.workflow import Workflow
from biorch.orchestration.result import WorkflowResult

class HandoffPayload(BaseModel):
    """
    Composite handoff payload for Phase 08.4F -> 08.4G.
    """
    workflow: Workflow
    workflow_result: WorkflowResult
    synthesis_eligible: bool = Field(..., description="Determines if synthesis is permitted.")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Collected worker artifacts.")
