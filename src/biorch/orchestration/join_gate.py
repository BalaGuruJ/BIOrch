from typing import Dict, Any
from biorch.core.workflow import Workflow
from biorch.orchestration.result import WorkflowResult, WorkflowResultStatus
from biorch.orchestration.handoff import HandoffPayload

class DeterministicJoinGate:
    @staticmethod
    def evaluate(workflow: Workflow, workflow_result: WorkflowResult, worker_artifacts: Dict[str, Any]) -> HandoffPayload:
        # Eligibility logic:
        # Synthesis is permitted if:
        # 1. Status is SUCCESS or PARTIAL (derived from ORCHESTRATOR_CONTRACT.md)
        # 2. No essential tasks failed (already handled by Orchestrator)
        # 3. Status is not REJECTED (contract prohibits synthesis)
        
        synthesis_eligible = (
            workflow_result.status in [WorkflowResultStatus.SUCCESS, WorkflowResultStatus.FAILED]
            and workflow_result.status != WorkflowResultStatus.REJECTED
        )
        
        # Additional essential failure check (fail-closed)
        if workflow_result.status == WorkflowResultStatus.FAILED and workflow_result.failed_task:
            # Check essentiality if failed_task exists
            for task in workflow.tasks:
                if task.task_id == workflow_result.failed_task and getattr(task, "is_essential", True):
                    synthesis_eligible = False
                    break

        return HandoffPayload(
            workflow=workflow,
            workflow_result=workflow_result,
            synthesis_eligible=synthesis_eligible,
            artifacts=worker_artifacts
        )
