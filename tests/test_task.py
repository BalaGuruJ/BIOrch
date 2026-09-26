import pytest
from pydantic import ValidationError
from biorch.core.task import Task, TaskStatus

def test_task_construction():
    """
    Test valid Task construction.
    """
    task = Task(task_id="t1", objective="do X", agent_id="a1", status=TaskStatus.PENDING)
    assert task.task_id == "t1"
    assert task.status == TaskStatus.PENDING

def test_task_invalid_status():
    """
    Test Task rejects invalid status values.
    """
    with pytest.raises(ValidationError):
        Task(task_id="t1", objective="do X", agent_id="a1", status="invalid_status")

def test_task_serialization():
    """
    Test Task serialization/deserialization.
    """
    task = Task(task_id="t1", objective="do X", agent_id="a1", status=TaskStatus.COMPLETED)
    assert Task.model_validate_json(task.model_dump_json()) == task
