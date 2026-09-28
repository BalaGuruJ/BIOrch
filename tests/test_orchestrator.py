import pytest
from unittest.mock import MagicMock
from biorch.core.agent import Agent
from biorch.core.task import Task, TaskStatus
from biorch.core.workflow import Workflow
from biorch.core.result import Result, ResultStatus
from biorch.core.gateway import ToolGateway, ToolRegistry, ToolDefinition, ToolResult, ToolStatus
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
        allowed_tools=["math_tool"],
        supported_operations=["ADD", "SUB"]
    )

@pytest.fixture
def agent_executor(gateway, agent_definition):
    return DeterministicAgentExecutor(gateway, agent_definition)

@pytest.fixture
def orchestrator(agent_executor):
    return DeterministicOrchestrator(agent_executor)


# ==============================================================================
# 1. Validation Tests
# ==============================================================================

def test_validation_empty_workflow(orchestrator, gateway):
    """An empty workflow must be rejected before execution with status REJECTED."""
    workflow = Workflow(workflow_id="w_empty", tasks=[], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert result.completed_tasks == []
    assert result.failed_task is None
    assert result.not_executed_tasks == []
    assert any("empty" in e.lower() for e in result.errors)


def test_validation_empty_workflow_id(orchestrator):
    """Workflow with missing or empty workflow_id must be rejected."""
    task = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="   ", tasks=[task], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("workflow identifier" in e.lower() for e in result.errors)


def test_validation_empty_workflow_version(orchestrator):
    """Workflow with empty version must be rejected."""
    task = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="   ", tasks=[task], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("workflow version" in e.lower() for e in result.errors)


def test_validation_duplicate_step_ids(orchestrator):
    """Duplicate task IDs must be rejected before execution."""
    task1 = Task(
        task_id="dup_id",
        objective="Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="dup_id",
        objective="Step 2",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 5, "b": 3}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_dup", tasks=[task1, task2], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("duplicate" in e.lower() for e in result.errors)
    assert result.completed_tasks == []


def test_validation_malformed_step(orchestrator):
    """Steps missing a task_id or malformed must be rejected."""
    task = Task(
        task_id="   ",
        objective="Malformed step",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_malformed", tasks=[task], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("step identifier" in e.lower() for e in result.errors)


def test_validation_missing_required_inputs(orchestrator):
    """Tasks missing operation or tool_id in inputs must be rejected."""
    task1 = Task(
        task_id="t_no_inputs",
        objective="No inputs",
        agent_id="agent1",
        inputs=None,
        status=TaskStatus.PENDING
    )
    workflow1 = Workflow(workflow_id="w_no_in", tasks=[task1], status="running")
    result1 = orchestrator.execute(workflow1)
    assert result1.status == WorkflowResultStatus.REJECTED
    assert any("missing required inputs" in e.lower() for e in result1.errors)

    task2 = Task(
        task_id="t_missing_op",
        objective="Missing op",
        agent_id="agent1",
        inputs={"tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow2 = Workflow(workflow_id="w_no_op", tasks=[task2], status="running")
    result2 = orchestrator.execute(workflow2)
    assert result2.status == WorkflowResultStatus.REJECTED
    assert any("operation" in e.lower() for e in result2.errors)


def test_validation_unsupported_operation(orchestrator):
    """Tasks requesting operations outside agent's supported operations must be rejected."""
    task = Task(
        task_id="t_unsupported_op",
        objective="Unsupported",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "MULTIPLY", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_unsupported", tasks=[task], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("unsupported operation" in e.lower() for e in result.errors)


def test_validation_invalid_target_agent(orchestrator):
    """Tasks targeting an unavailable agent must be rejected before execution."""
    task = Task(
        task_id="t_wrong_agent",
        objective="Wrong Agent",
        agent_id="unknown_agent",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_wrong_agent", tasks=[task], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("not available" in e.lower() for e in result.errors)


def test_validation_step_ordering_and_dependencies(orchestrator):
    """Step dependency referencing a subsequent or nonexistent task must be rejected."""
    task1 = Task(
        task_id="t1",
        objective="Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        dependencies=["t2"],  # Depends on future step t2
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Step 2",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_dep", tasks=[task1, task2], status="running")
    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert any("dependency" in e.lower() for e in result.errors)


def test_validation_occurs_before_execution_zero_steps_no_gateway(orchestrator, agent_executor, gateway):
    """Validation failure must execute zero steps; Tool Gateway must never be reached."""
    agent_executor.execute = MagicMock(wraps=agent_executor.execute)
    gateway.invoke = MagicMock(wraps=gateway.invoke)

    # Step 1 is valid, but Step 2 targets an invalid agent
    task1 = Task(
        task_id="t1",
        objective="Valid Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Invalid Agent Step 2",
        agent_id="nonexistent_agent",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_fail_val", tasks=[task1, task2], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert result.completed_tasks == []
    assert len(result.not_executed_tasks) == 2
    assert "t1" in result.not_executed_tasks
    assert "t2" in result.not_executed_tasks
    # Neither agent executor nor gateway was invoked
    assert agent_executor.execute.call_count == 0
    assert gateway.invoke.call_count == 0


# ==============================================================================
# 2. Sequential Execution Tests
# ==============================================================================

def test_sequential_execution_declared_order(orchestrator):
    """Valid workflow executes strictly in declared sequential order."""
    task1 = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Sub",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 5, "b": 3}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_seq", tasks=[task1, task2], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.completed_tasks == ["t1", "t2"]
    assert result.provenance["execution_order"] == ["t1", "t2"]
    assert result.failed_task is None
    assert result.not_executed_tasks == []


def test_every_valid_step_executes_exactly_once(orchestrator, agent_executor):
    """Every valid step must execute exactly once during a single execution run."""
    agent_executor.execute = MagicMock(wraps=agent_executor.execute)

    task1 = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Sub",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 5, "b": 3}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_once", tasks=[task1, task2], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.SUCCESS
    assert agent_executor.execute.call_count == 2
    executed_task_ids = [call.args[0].task_id for call in agent_executor.execute.call_args_list]
    assert executed_task_ids == ["t1", "t2"]


def test_repeated_execution_preserves_order(orchestrator):
    """Repeated execution of the same workflow produces the same declared execution order."""
    task1 = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Sub",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 5, "b": 3}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_repeat", tasks=[task1, task2], status="running")

    result1 = orchestrator.execute(workflow)
    result2 = orchestrator.execute(workflow)

    assert result1.completed_tasks == result2.completed_tasks == ["t1", "t2"]
    assert result1.provenance["execution_order"] == result2.provenance["execution_order"] == ["t1", "t2"]


# ==============================================================================
# 3. Fail-Fast Tests
# ==============================================================================

def test_fail_fast_first_step_failure(orchestrator, agent_executor):
    """Failure on step 1 stops execution immediately; later steps are NOT_EXECUTED."""
    # Mock agent_executor to return an execution failure (not a rejection) on step 1
    def mock_exec(task):
        if task.task_id == "t1":
            return Result(task_id="t1", status=ResultStatus.FAILURE, errors=["Tool execution failed: compute error"])
        return Result(task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[{"ok": True}])

    agent_executor.execute = MagicMock(side_effect=mock_exec)

    task1 = Task(
        task_id="t1",
        objective="Fail on step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Step 2",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    task3 = Task(
        task_id="t3",
        objective="Step 3",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/3"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_fail_fast_1", tasks=[task1, task2, task3], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.FAILED
    assert result.completed_tasks == []
    assert result.failed_task == "t1"
    assert result.not_executed_tasks == ["t2", "t3"]
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    assert result.step_results["t3"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    # Exactly one execution attempt occurred
    assert agent_executor.execute.call_count == 1


def test_fail_fast_middle_step_failure(orchestrator, agent_executor):
    """Failure on middle step terminates execution; later steps are NOT_EXECUTED."""
    def mock_exec(task):
        if task.task_id == "t2":
            return Result(task_id="t2", status=ResultStatus.FAILURE, errors=["Tool execution failed: divide by zero"])
        return Result(task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[{"ok": True}])

    agent_executor.execute = MagicMock(side_effect=mock_exec)

    task1 = Task(
        task_id="t1",
        objective="Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Step 2 fails",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    task3 = Task(
        task_id="t3",
        objective="Step 3",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/3"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_fail_fast_2", tasks=[task1, task2, task3], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.FAILED
    assert result.completed_tasks == ["t1"]
    assert result.failed_task == "t2"
    assert result.not_executed_tasks == ["t3"]
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.SUCCESS.value
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.FAILED.value
    assert result.step_results["t3"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    assert agent_executor.execute.call_count == 2


# ==============================================================================
# 4. Rejection Propagation Tests
# ==============================================================================

def test_rejection_agent_level(orchestrator, agent_executor):
    """Agent-level rejection must propagate as REJECTED and halt subsequent steps."""
    task1 = Task(
        task_id="t1",
        objective="Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Agent rejects unauthorized tool",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    task3 = Task(
        task_id="t3",
        objective="Step 3",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/3"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_agent_rej", tasks=[task1, task2, task3], status="running")

    # Simulate agent rejection on step 2
    real_exec = agent_executor.execute
    def mock_exec(task):
        if task.task_id == "t2":
            return Result(task_id="t2", status=ResultStatus.FAILURE, errors=["Unauthorized tool: math_tool"])
        return real_exec(task)

    agent_executor.execute = MagicMock(side_effect=mock_exec)

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert result.completed_tasks == ["t1"]
    assert result.failed_task == "t2"
    assert result.not_executed_tasks == ["t3"]
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.REJECTED.value
    assert result.step_results["t3"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value
    assert agent_executor.execute.call_count == 2


def test_rejection_gateway_level(orchestrator):
    """Tool Gateway authorization rejection must propagate as REJECTED status."""
    task1 = Task(
        task_id="t1",
        objective="Step 1",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Gateway rejects unauthorized resource",
        agent_id="agent1",
        # Resource '/etc/passwd' is outside tool's allowed_resources ['/data/']
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/etc/passwd"},
        status=TaskStatus.PENDING
    )
    task3 = Task(
        task_id="t3",
        objective="Step 3",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 3, "b": 4}, "resource": "/data/3"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_gw_rej", tasks=[task1, task2, task3], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert result.completed_tasks == ["t1"]
    assert result.failed_task == "t2"
    assert result.not_executed_tasks == ["t3"]
    assert any("unauthorized resource" in e.lower() for e in result.errors)
    assert result.step_results["t2"]["status"] == WorkflowResultStatus.REJECTED.value
    assert result.step_results["t3"]["status"] == WorkflowResultStatus.NOT_EXECUTED.value


def test_rejection_cannot_be_bypassed(orchestrator, agent_executor):
    """Rejection cannot be bypassed or converted to success; subsequent steps never execute."""
    agent_executor.execute = MagicMock(wraps=agent_executor.execute)

    task1 = Task(
        task_id="t1",
        objective="Gateway rejection step",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/unauthorized_path/"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Should never run",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_no_bypass", tasks=[task1, task2], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.REJECTED
    assert result.status != WorkflowResultStatus.SUCCESS
    assert result.completed_tasks == []
    assert result.failed_task == "t1"
    assert result.not_executed_tasks == ["t2"]
    assert agent_executor.execute.call_count == 1


# ==============================================================================
# 5. Boundary Enforcement Tests
# ==============================================================================

def test_orchestrator_delegation_boundary(orchestrator, agent_executor):
    """Orchestrator delegates exclusively through DeterministicAgentExecutor."""
    assert hasattr(orchestrator, "agent_executor")
    assert isinstance(orchestrator.agent_executor, DeterministicAgentExecutor)
    # Orchestrator does NOT have direct access to ToolGateway
    assert not hasattr(orchestrator, "gateway")
    assert not hasattr(orchestrator, "tools")
    assert not hasattr(orchestrator, "registry")


def test_no_direct_tool_invocation_in_orchestration_code():
    """Verify that orchestration code does not invoke gateway or tools directly."""
    import inspect
    from biorch.orchestration import orchestrator as orch_mod

    source = inspect.getsource(orch_mod)
    assert "gateway.invoke" not in source
    assert "ToolGateway" not in source
    assert "subprocess" not in source
    assert "os.system" not in source


# ==============================================================================
# 6. Result Correctness & Provenance Tests
# ==============================================================================

def test_result_structure_and_provenance_success(orchestrator):
    """Verify complete WorkflowResult metadata, provenance, and property aliases on SUCCESS."""
    task1 = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 2, "b": 3}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_prov", version="2.0", tasks=[task1], status="running")

    result = orchestrator.execute(workflow)

    assert result.workflow_id == "w_prov"
    assert result.workflow_version == "2.0"
    assert result.status == WorkflowResultStatus.SUCCESS
    assert result.completed_tasks == ["t1"]
    assert result.completed_steps == ["t1"]
    assert result.failed_task is None
    assert result.failed_step is None
    assert result.not_executed_tasks == []
    assert result.not_executed_steps == []
    assert "t1" in result.results
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.SUCCESS.value
    assert result.provenance["workflow_id"] == "w_prov"
    assert result.provenance["workflow_version"] == "2.0"
    assert result.provenance["execution_order"] == ["t1"]
    assert result.provenance["terminal_status"] == WorkflowResultStatus.SUCCESS.value


def test_result_structure_failed_status(orchestrator, agent_executor):
    """Verify FAILED status and metadata on runtime tool execution failure."""
    def mock_exec(task):
        return Result(task_id=task.task_id, status=ResultStatus.FAILURE, errors=["Tool execution failed: timeout"])

    agent_executor.execute = MagicMock(side_effect=mock_exec)

    task1 = Task(
        task_id="t1",
        objective="Compute",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_fail", tasks=[task1], status="running")

    result = orchestrator.execute(workflow)

    assert result.status == WorkflowResultStatus.FAILED
    assert result.failed_task == "t1"
    assert result.failed_step == "t1"
    assert result.step_results["t1"]["status"] == WorkflowResultStatus.FAILED.value
    assert result.provenance["terminal_status"] == WorkflowResultStatus.FAILED.value


# ==============================================================================
# 7. Determinism & Termination Tests
# ==============================================================================

def test_orchestration_determinism(orchestrator):
    """Equivalent workflow executions yield equivalent terminal results and structure."""
    task1 = Task(
        task_id="t1",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 10, "b": 20}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    task2 = Task(
        task_id="t2",
        objective="Sub",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "SUB", "tool_inputs": {"a": 30, "b": 5}, "resource": "/data/2"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w_det", tasks=[task1, task2], status="running")

    run1 = orchestrator.execute(workflow)
    run2 = orchestrator.execute(workflow)

    assert run1.status == run2.status == WorkflowResultStatus.SUCCESS
    assert run1.completed_tasks == run2.completed_tasks == ["t1", "t2"]
    assert run1.provenance["execution_order"] == run2.provenance["execution_order"] == ["t1", "t2"]
    assert run1.step_results == run2.step_results


def test_deterministic_termination_always_reached(orchestrator):
    """Every execution path deterministically reaches a terminal WorkflowResult."""
    # 1. Validation failure termination
    res_val = orchestrator.execute(Workflow(workflow_id="w_t1", tasks=[], status="running"))
    assert res_val.status in (WorkflowResultStatus.SUCCESS, WorkflowResultStatus.REJECTED, WorkflowResultStatus.FAILED)

    # 2. Successful execution termination
    t_ok = Task(
        task_id="t_ok",
        objective="Add",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {"a": 1, "b": 2}, "resource": "/data/1"},
        status=TaskStatus.PENDING
    )
    res_ok = orchestrator.execute(Workflow(workflow_id="w_t2", tasks=[t_ok], status="running"))
    assert res_ok.status == WorkflowResultStatus.SUCCESS

    # 3. Gateway rejection termination
    t_rej = Task(
        task_id="t_rej",
        objective="Reject",
        agent_id="agent1",
        inputs={"tool_id": "math_tool", "operation": "ADD", "tool_inputs": {}, "resource": "/bad/path"},
        status=TaskStatus.PENDING
    )
    res_rej = orchestrator.execute(Workflow(workflow_id="w_t3", tasks=[t_rej], status="running"))
    assert res_rej.status == WorkflowResultStatus.REJECTED
