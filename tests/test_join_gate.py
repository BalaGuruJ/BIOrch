import pytest
from biorch.core.workflow import Workflow
from biorch.orchestration.result import WorkflowResult, WorkflowResultStatus
from biorch.orchestration.handoff import HandoffPayload
from biorch.orchestration.join_gate import DeterministicJoinGate
from biorch.core.task import Task, TaskStatus

def test_join_gate_success():
    workflow = Workflow(workflow_id="wf1", tasks=[Task(task_id="t1", agent_id="a1", objective="o", status=TaskStatus.PENDING)], status="pending")
    result = WorkflowResult(
        workflow_id="wf1",
        workflow_version="1.0",
        status=WorkflowResultStatus.SUCCESS,
        completed_tasks=["t1"]
    )
    artifacts = {"t1": ["art1"]}
    
    handoff = DeterministicJoinGate.evaluate(workflow, result, artifacts)
    
    assert handoff.synthesis_eligible is True
    assert handoff.artifacts == artifacts
    assert handoff.workflow_result.status == WorkflowResultStatus.SUCCESS

def test_join_gate_essential_failure():
    # Define an essential task
    task = Task(task_id="t1", agent_id="a1", objective="o", status=TaskStatus.FAILED, is_essential=True)
    workflow = Workflow(workflow_id="wf1", tasks=[task], status="pending")
    
    result = WorkflowResult(
        workflow_id="wf1",
        workflow_version="1.0",
        status=WorkflowResultStatus.FAILED,
        completed_tasks=[],
        failed_task="t1"
    )
    artifacts = {}
    
    handoff = DeterministicJoinGate.evaluate(workflow, result, artifacts)
    
    assert handoff.synthesis_eligible is False

def test_join_gate_non_essential_failure():
    # Define a non-essential task
    task = Task(task_id="t1", agent_id="a1", objective="o", status=TaskStatus.FAILED, is_essential=False)
    workflow = Workflow(workflow_id="wf1", tasks=[task], status="pending")
    
    result = WorkflowResult(
        workflow_id="wf1",
        workflow_version="1.0",
        status=WorkflowResultStatus.FAILED,
        completed_tasks=[],
        failed_task="t1"
    )
    artifacts = {}
    
    handoff = DeterministicJoinGate.evaluate(workflow, result, artifacts)
    
    assert handoff.synthesis_eligible is True
