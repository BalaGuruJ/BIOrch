import pytest
from biorch.core.agent import Agent
from biorch.core.task import Task, TaskStatus
from biorch.core.workflow import Workflow
from biorch.core.gateway import ToolGateway, ToolRegistry, ToolDefinition
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.result import WorkflowResultStatus

@pytest.fixture
def gateway():
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        tool_id="math_tool",
        name="Math Tool",
        purpose="Simple math",
        version="1.0",
        input_schema={"a": "int", "b": "int"},
        output_schema={"sum": "int"},
        allowed_resources=["/data/"],
        permitted_operations=["ADD", "SUB"],
        security_classification="PUBLIC"
    ))
    return ToolGateway(registry)

@pytest.fixture
def agent_definition():
    return Agent(
        agent_id="agent1",
        name="Calculator",
        role="Math",
        allowed_tools=["math_tool"]
    )

@pytest.fixture
def agent_executor(gateway, agent_definition):
    return DeterministicAgentExecutor(gateway, agent_definition)

@pytest.fixture
def orchestrator(agent_executor):
    return DeterministicOrchestrator(agent_executor)

def test_orchestrator_success(orchestrator):
    task1 = Task(task_id="t1", objective="Add", agent_id="agent1", 
                 inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"}, status=TaskStatus.PENDING)
    task2 = Task(task_id="t2", objective="Sub", agent_id="agent1", 
                 inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 5, "b": 3}, "resource": "/data/2"}, status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="w1", tasks=[task1, task2], status="running")
    
    result = orchestrator.execute(workflow)
    
    assert result.status == WorkflowResultStatus.SUCCESS
    assert len(result.completed_tasks) == 2
    assert "t1" in result.completed_tasks
    assert "t2" in result.completed_tasks

def test_orchestrator_validation_failure(orchestrator):
    # Invalid workflow: empty tasks
    workflow = Workflow(workflow_id="w1", tasks=[], status="running")
    
    result = orchestrator.execute(workflow)
    
    assert result.status == WorkflowResultStatus.REJECTED

def test_orchestrator_step_failure(orchestrator):
    task1 = Task(task_id="t1", objective="Add", agent_id="agent1", 
                 inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"}, status=TaskStatus.PENDING)
    task2 = Task(task_id="t2", objective="Fail", agent_id="agent1", 
                 inputs={"tool_id": "math_tool", "operation": "INVALID", "tool_inputs": {}, "resource": "/data/2"}, status=TaskStatus.PENDING)
    task3 = Task(task_id="t3", objective="Add", agent_id="agent1", 
                 inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 3, "b": 4}, "resource": "/data/3"}, status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="w1", tasks=[task1, task2, task3], status="running")
    
    result = orchestrator.execute(workflow)
    
    assert result.status == WorkflowResultStatus.FAILED
    assert "t1" in result.completed_tasks
    assert result.failed_task == "t2"
    assert "t3" in result.not_executed_tasks
