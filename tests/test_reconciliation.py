import pytest
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.core.task import Task, TaskStatus
from biorch.core.workflow import Workflow
from biorch.orchestration.result import WorkflowResultStatus

from biorch.orchestration.agent_resolver import AgentResolver

def test_reconciliation_completeness_validation():
    # Initialize with a dummy AgentResolver
    orchestrator = DeterministicOrchestrator(AgentResolver({}))
    
    # Create a workflow with 2 tasks
    tasks = [
        Task(task_id="t1", objective="o1", agent_id="a1", status=TaskStatus.PENDING), 
        Task(task_id="t2", objective="o2", agent_id="a2", status=TaskStatus.PENDING)
    ]
    workflow = Workflow(workflow_id="w1", tasks=tasks, status="pending")
    
    # Valid step_results (all terminal)
    valid_step_results = {
        "t1": {"status": WorkflowResultStatus.SUCCESS.value},
        "t2": {"status": WorkflowResultStatus.FAILED.value}
    }
    
    # Should not raise
    orchestrator._reconcile_terminal_outcomes(workflow, valid_step_results)
    
    # Invalid: missing task
    incomplete_step_results = {
        "t1": {"status": WorkflowResultStatus.SUCCESS.value}
    }
    with pytest.raises(RuntimeError, match="Task 't2' is missing"):
        orchestrator._reconcile_terminal_outcomes(workflow, incomplete_step_results)
        
    # Invalid: non-terminal status
    invalid_step_results = {
        "t1": {"status": WorkflowResultStatus.SUCCESS.value},
        "t2": {"status": "IN_PROGRESS"}
    }
    with pytest.raises(RuntimeError, match="non-terminal status: 'IN_PROGRESS'"):
        orchestrator._reconcile_terminal_outcomes(workflow, invalid_step_results)
