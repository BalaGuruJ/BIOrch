import pytest
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.result import Result, ResultStatus
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.agent_resolver import AgentResolver
from unittest.mock import MagicMock
import time

class MockAgentExecutor:
    def execute(self, task):
        time.sleep(0.1)
        return Result(task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[], errors=[])

def test_sequential_compatibility():
    # Tasks: t1 -> t2 -> t3, not parallel eligible
    t1 = Task(task_id="t1", objective="o1", agent_id="a1", status=TaskStatus.PENDING, inputs={"operation": "op", "tool_id": "tool1"}, is_parallel_eligible=False)
    t2 = Task(task_id="t2", objective="o2", agent_id="a1", status=TaskStatus.PENDING, inputs={"operation": "op", "tool_id": "tool1"}, is_parallel_eligible=False, dependencies=["t1"])
    t3 = Task(task_id="t3", objective="o3", agent_id="a1", status=TaskStatus.PENDING, inputs={"operation": "op", "tool_id": "tool1"}, is_parallel_eligible=False, dependencies=["t2"])

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[t1, t2, t3], status="pending")
    resolver = AgentResolver({"a1": MockAgentExecutor()})
    orchestrator = DeterministicOrchestrator(resolver)

    result = orchestrator.execute(workflow)
    assert result.provenance['execution_order'] == ['t1', 't2', 't3']

def test_dependency_enforcement():
    # Tasks: t1, t2 depends on t1. t2 should not start until t1 is done.
    # Parallel eligible
    t1 = Task(task_id="t1", objective="o1", agent_id="a1", status=TaskStatus.PENDING, inputs={"operation": "op", "tool_id": "tool1"}, is_parallel_eligible=True)
    t2 = Task(task_id="t2", objective="o2", agent_id="a1", status=TaskStatus.PENDING, inputs={"operation": "op", "tool_id": "tool1"}, is_parallel_eligible=True, dependencies=["t1"])

    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[t1, t2], status="pending")
    resolver = AgentResolver({"a1": MockAgentExecutor()})
    orchestrator = DeterministicOrchestrator(resolver)

    result = orchestrator.execute(workflow)
    # Execution order must respect dependency: t1 then t2
    assert result.provenance['execution_order'].index("t1") < result.provenance['execution_order'].index("t2")
