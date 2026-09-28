from typing import List
from biorch.core.workflow import Workflow
from biorch.core.result import ResultStatus
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from .result import WorkflowResult, WorkflowResultStatus

class DeterministicOrchestrator:
    def __init__(self, agent_executor: DeterministicAgentExecutor):
        self.agent_executor = agent_executor

    def validate(self, workflow: Workflow) -> bool:
        """
        Performs basic workflow validation.
        """
        if not workflow.tasks:
            return False
        # Ensure unique task IDs
        task_ids = [task.task_id for task in workflow.tasks]
        if len(set(task_ids)) != len(task_ids):
            return False
        return True

    def execute(self, workflow: Workflow) -> WorkflowResult:
        """
        Executes the workflow sequentially and returns a structured result.
        """
        if not self.validate(workflow):
            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                status=WorkflowResultStatus.REJECTED,
                errors=["Workflow validation failed"]
            )

        completed_tasks = []
        not_executed_tasks = []
        results = {}
        errors = []

        for i, task in enumerate(workflow.tasks):
            # Delegation
            result = self.agent_executor.execute(task)

            if result.status == ResultStatus.SUCCESS:
                completed_tasks.append(task.task_id)
                results[task.task_id] = result.findings
            else:
                # Fail-fast
                failed_task = task.task_id
                # Mark remaining as NOT_EXECUTED
                not_executed_tasks = [t.task_id for t in workflow.tasks[i+1:]]
                return WorkflowResult(
                    workflow_id=workflow.workflow_id,
                    status=WorkflowResultStatus.FAILED,
                    completed_tasks=completed_tasks,
                    failed_task=failed_task,
                    not_executed_tasks=not_executed_tasks,
                    results=results,
                    errors=result.errors
                )

        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=WorkflowResultStatus.SUCCESS,
            completed_tasks=completed_tasks,
            results=results
        )
