import pytest
from biorch.core.task import Task, TaskStatus

def test_task_backward_compatibility():
    """1. Existing Task construction continues to work without specifying the new fields."""
    task = Task(
        task_id="t1",
        objective="Test",
        agent_id="agent1",
        status=TaskStatus.PENDING
    )
    assert task.task_id == "t1"
    assert task.is_parallel_eligible is False
    assert task.is_essential is True

def test_task_parallel_eligible_default():
    """2. is_parallel_eligible defaults to False."""
    task = Task(
        task_id="t1",
        objective="Test",
        agent_id="agent1",
        status=TaskStatus.PENDING
    )
    assert task.is_parallel_eligible is False

def test_task_essential_default():
    """3. is_essential defaults to True."""
    task = Task(
        task_id="t1",
        objective="Test",
        agent_id="agent1",
        status=TaskStatus.PENDING
    )
    assert task.is_essential is True

def test_task_new_fields_explicit():
    """4. Explicit True/False values are accepted."""
    task = Task(
        task_id="t1",
        objective="Test",
        agent_id="agent1",
        status=TaskStatus.PENDING,
        is_parallel_eligible=True,
        is_essential=False
    )
    assert task.is_parallel_eligible is True
    assert task.is_essential is False

def test_task_status_enums():
    """5, 6, 7. Validate TaskStatus enums."""
    assert TaskStatus.TIMEOUT == "timeout"
    assert TaskStatus.NOT_EXECUTED == "not_executed"
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.FAILED == "failed"

def test_task_dependencies_unchanged():
    """8. Existing Task.dependencies remains unchanged."""
    task = Task(
        task_id="t2",
        objective="Test",
        agent_id="agent1",
        status=TaskStatus.PENDING,
        dependencies=["t1"]
    )
    assert task.dependencies == ["t1"]

def test_no_workflow_result_status_timeout():
    """9. Verify no WorkflowResultStatus.TIMEOUT exists."""
    from biorch.orchestration.result import WorkflowResultStatus
    with pytest.raises(AttributeError):
        _ = WorkflowResultStatus.TIMEOUT

def test_workflow_result_backward_compatibility():
    """
    Verify WorkflowResult construction remains valid with existing fields.
    """
    from biorch.orchestration.result import WorkflowResult, WorkflowResultStatus

    result = WorkflowResult(
        workflow_id="test_w",
        status=WorkflowResultStatus.SUCCESS,
        completed_tasks=["t1"]
    )

    assert result.workflow_id == "test_w"
    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.completed_tasks == ["t1"]
    # Verify existing construction fields exist
    assert result.workflow_version == "1.0"
    assert result.provenance == {}
