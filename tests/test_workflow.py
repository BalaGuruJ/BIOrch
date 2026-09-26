import pytest
from pydantic import ValidationError
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus

def test_workflow_construction():
    """
    Test valid Workflow construction.
    """
    task = Task(task_id="t1", objective="do X", agent_id="a1", status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="w1", tasks=[task], status="running")
    assert workflow.workflow_id == "w1"
    assert len(workflow.tasks) == 1

def test_workflow_required_field():
    """
    Test Workflow rejects invalid contract.
    """
    with pytest.raises(ValidationError):
        Workflow(workflow_id="w1") # Missing tasks and status

def test_workflow_serialization():
    """
    Test Workflow serialization/deserialization.
    """
    task = Task(task_id="t1", objective="do X", agent_id="a1", status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="w1", tasks=[task], status="running")
    assert Workflow.model_validate_json(workflow.model_dump_json()) == workflow
