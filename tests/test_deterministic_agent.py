import pytest
from biorch.core.agent import Agent
from biorch.core.task import Task, TaskStatus
from biorch.core.result import ResultStatus
from biorch.core.gateway import ToolGateway, ToolRegistry, ToolDefinition
from biorch.agents.deterministic_agent import DeterministicAgentExecutor

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
        permitted_operations=["ADD"],
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

def test_deterministic_agent_success(gateway, agent_definition):
    executor = DeterministicAgentExecutor(gateway, agent_definition)
    task = Task(
        task_id="t1",
        objective="Add numbers",
        agent_id="agent1",
        inputs={
            "tool_id": "math_tool",
            "operation": "ADD",
            "tool_inputs": {"a": 1, "b": 2},
            "resource": "/data/test"
        },
        status=TaskStatus.PENDING
    )
    result = executor.execute(task)
    assert result.status == ResultStatus.SUCCESS
    assert result.task_id == "t1"

def test_deterministic_agent_unauthorized_tool(gateway, agent_definition):
    executor = DeterministicAgentExecutor(gateway, agent_definition)
    task = Task(
        task_id="t2",
        objective="Run unauthorized tool",
        agent_id="agent1",
        inputs={
            "tool_id": "other_tool",
            "operation": "RUN"
        },
        status=TaskStatus.PENDING
    )
    result = executor.execute(task)
    assert result.status == ResultStatus.FAILURE
    assert "Unauthorized tool" in result.errors[0]

def test_deterministic_agent_gateway_failure(gateway, agent_definition):
    executor = DeterministicAgentExecutor(gateway, agent_definition)
    task = Task(
        task_id="t3",
        objective="Run unauthorized op",
        agent_id="agent1",
        inputs={
            "tool_id": "math_tool",
            "operation": "INVALID_OP",
            "resource": "/data/test"
        },
        status=TaskStatus.PENDING
    )
    result = executor.execute(task)
    assert result.status == ResultStatus.FAILURE
    assert "Unauthorized operation" in result.errors[0]
