import pytest
import time
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.result import Result, ResultStatus
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.result import WorkflowResultStatus

# Mock Agent Executor
class MockAgentExecutor:
    def __init__(self, agent_id, delay=0, failing_task_ids=None, should_raise=False):
        self.agent_definition = type("AgentDef", (), {"agent_id": agent_id})
        self.delay = delay
        self.failing_task_ids = failing_task_ids or []
        self.should_raise = should_raise

    def execute(self, task):
        print(f"DEBUG: Executing task {task.task_id}")
        time.sleep(10)
        print(f"DEBUG: Finished executing task {task.task_id}")
        if self.should_raise:
            raise Exception("Execution failed")
        if task.task_id in self.failing_task_ids:
            return Result(task_id=task.task_id, status=ResultStatus.FAILURE, errors=["Task failed"])
        return Result(task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[{"result": "success"}])

def test_essential_task_timeout_terminates_workflow():
    agent_executor = MockAgentExecutor("agent1")
    orchestrator = DeterministicOrchestrator(agent_executor)

    inputs = {"operation": "op", "tool_id": "tool1"}
    task1 = Task(task_id="t1", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=True, metadata={"timeout": 0.5})

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task1], status="pending")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.FAILED
    assert result.step_results["t1"]["status"] == TaskStatus.TIMEOUT.value
    assert result.failed_task == "t1"

def test_non_essential_task_timeout_continues_workflow():
    agent_executor = MockAgentExecutor("agent1")
    orchestrator = DeterministicOrchestrator(agent_executor)

    inputs = {"operation": "op", "tool_id": "tool1"}
    task1 = Task(task_id="t1", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=False, metadata={"timeout": 0.5})
    task2 = Task(task_id="t2", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, dependencies=["t1"], is_essential=True)

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task1, task2], status="pending")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.step_results["t1"]["status"] == TaskStatus.TIMEOUT.value
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value

def test_essential_task_failure_terminates_workflow():
    agent_executor = MockAgentExecutor("agent1", failing_task_ids=["t1"])
    orchestrator = DeterministicOrchestrator(agent_executor)

    inputs = {"operation": "op", "tool_id": "tool1"}
    task1 = Task(task_id="t1", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=True)

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task1], status="pending")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.FAILED
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.FAILED.value
    assert result.failed_task == "t1"

def test_non_essential_task_failure_continues_workflow():
    agent_executor = MockAgentExecutor("agent1", failing_task_ids=["t1"])
    orchestrator = DeterministicOrchestrator(agent_executor)

    inputs = {"operation": "op", "tool_id": "tool1"}
    task1 = Task(task_id="t1", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=False)
    task2 = Task(task_id="t2", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, dependencies=["t1"], is_essential=True)

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task1, task2], status="pending")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.FAILED.value
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value

def test_transitive_dependency_blocking():
    agent_executor = MockAgentExecutor("agent1", failing_task_ids=["t1"])
    orchestrator = DeterministicOrchestrator(agent_executor)

    inputs = {"operation": "op", "tool_id": "tool1"}

    # Setup T1
    task1 = Task(task_id="t1", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=False)

    # Subsequent tasks
    task2 = Task(task_id="t2", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, dependencies=["t1"], is_essential=True)
    task3 = Task(task_id="t3", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, dependencies=["t2"], is_essential=True)
    task4 = Task(task_id="t4", objective="o", agent_id="agent1", inputs=inputs, status=TaskStatus.PENDING, is_essential=True)

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task1, task2, task3, task4], status="pending")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.FAILED.value
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    assert result.step_results["t3"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    assert result.step_results["t4"]["status"] == WorkflowResultStatus.SUCCESS.value
