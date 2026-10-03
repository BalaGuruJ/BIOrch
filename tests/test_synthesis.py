import pytest
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.result import Result, ResultStatus
from biorch.core.agent import Agent
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.handoff import HandoffPayload
from biorch.orchestration.result import WorkflowResult, WorkflowResultStatus
from biorch.orchestration.synthesis import synthesize_result

@pytest.fixture
def mock_agent_executor():
    class DummyExecutor:
        def __init__(self, agent_id="agent1"):
            self.agent_definition = Agent(
                agent_id=agent_id,
                name="Test Agent",
                role="Tester",
                allowed_tools=["test_tool"],
                supported_operations=["TEST"]
            )
        def execute(self, task: Task) -> Result:
            return Result(
                task_id=task.task_id,
                status=ResultStatus.SUCCESS,
                findings=[{"metric": f"val_{task.task_id}"}],
                artifacts=[f"art_{task.task_id}.json"],
                errors=[]
            )
    return DummyExecutor()

def test_successful_synthesis(mock_agent_executor):
    task1 = Task(
        task_id="t1",
        objective="Task 1",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=True
    )
    task2 = Task(
        task_id="t2",
        objective="Task 2",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        dependencies=["t1"],
        status=TaskStatus.PENDING,
        is_essential=True
    )
    workflow = Workflow(workflow_id="wf_success", version="1.0", tasks=[task1, task2], status="running")

    orchestrator = DeterministicOrchestrator(mock_agent_executor)
    synth_result = orchestrator.run_with_synthesis(workflow)

    assert synth_result["status"] == "SUCCESS"
    assert synth_result["synthesis_eligible"] is True
    assert synth_result["workflow_id"] == "wf_success"
    assert synth_result["workflow_version"] == "1.0"
    assert len(synth_result["task_attributions"]) == 2
    assert synth_result["task_attributions"][0]["task_id"] == "t1"
    assert synth_result["task_attributions"][0]["status"] == "SUCCESS"
    assert synth_result["task_attributions"][1]["task_id"] == "t2"
    assert synth_result["task_attributions"][1]["status"] == "SUCCESS"
    assert len(synth_result["aggregated_findings"]) == 2
    assert synth_result["aggregated_findings"][0]["task_id"] == "t1"
    assert synth_result["aggregated_findings"][0]["data"]["metric"] == "val_t1"
    assert synth_result["provenance"]["synthesis_contract"] == "BIORCH-SYNTH-001"
    assert synth_result["provenance"]["synthesis_status"] == "SUCCESS"
    assert synth_result["provenance"]["synthesis_task_count"] == 2

def test_fail_closed_synthesis(mock_agent_executor):
    task1 = Task(
        task_id="t1",
        objective="Task 1",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=True
    )
    workflow = Workflow(workflow_id="wf_fail", version="1.0", tasks=[task1], status="running")

    workflow_result = WorkflowResult(
        workflow_id="wf_fail",
        workflow_version="1.0",
        status=WorkflowResultStatus.FAILED,
        completed_tasks=[],
        failed_task="t1",
        step_results={
            "t1": {"status": "FAILED", "findings": [], "errors": ["Task failed"]}
        },
        errors=["Task failed"]
    )
    handoff = HandoffPayload(
        workflow=workflow,
        workflow_result=workflow_result,
        synthesis_eligible=False,
        artifacts={}
    )

    synth_result = synthesize_result(handoff)

    assert synth_result["status"] == "FAILED"
    assert synth_result["synthesis_eligible"] is False
    assert synth_result["aggregated_findings"] == []
    assert synth_result["provenance"]["synthesis_status"] == "FAILED"
    assert len(synth_result["task_attributions"]) == 1
    assert synth_result["task_attributions"][0]["status"] == "FAILED"
    assert synth_result["task_attributions"][0]["findings"] == []

def test_partial_synthesis_non_essential_failure():
    task1 = Task(
        task_id="t1",
        objective="Essential",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=True
    )
    task2 = Task(
        task_id="t2",
        objective="Non-Essential",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=False
    )
    workflow = Workflow(workflow_id="wf_partial", version="1.0", tasks=[task1, task2], status="running")

    workflow_result = WorkflowResult(
        workflow_id="wf_partial",
        workflow_version="1.0",
        status=WorkflowResultStatus.FAILED,
        completed_tasks=["t1"],
        failed_task="t2",
        step_results={
            "t1": {"status": "SUCCESS", "findings": [{"result": "t1_ok"}], "errors": []},
            "t2": {"status": "FAILED", "findings": [], "errors": ["Non-essential failed"]}
        },
        errors=["Non-essential failed"]
    )
    handoff = HandoffPayload(
        workflow=workflow,
        workflow_result=workflow_result,
        synthesis_eligible=True,
        artifacts={"t1": ["art1"]}
    )

    synth_result = synthesize_result(handoff)

    assert synth_result["status"] == "PARTIAL"
    assert synth_result["synthesis_eligible"] is True
    assert len(synth_result["task_attributions"]) == 2
    assert synth_result["task_attributions"][0]["task_id"] == "t1"
    assert synth_result["task_attributions"][0]["status"] == "SUCCESS"
    assert synth_result["task_attributions"][1]["task_id"] == "t2"
    assert synth_result["task_attributions"][1]["status"] == "FAILED"
    assert len(synth_result["aggregated_findings"]) == 1
    assert synth_result["aggregated_findings"][0]["data"]["result"] == "t1_ok"

def test_explicit_terminal_states_visibility():
    task1 = Task(task_id="t_succ", objective="Success", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING, is_essential=True)
    task2 = Task(task_id="t_fail", objective="Fail", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING, is_essential=False)
    task3 = Task(task_id="t_time", objective="Timeout", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING, is_essential=False)
    task4 = Task(task_id="t_skip", objective="Not Executed", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING, is_essential=False)
    
    workflow = Workflow(workflow_id="wf_states", version="1.0", tasks=[task1, task2, task3, task4], status="running")

    workflow_result = WorkflowResult(
        workflow_id="wf_states",
        workflow_version="1.0",
        status=WorkflowResultStatus.FAILED,
        completed_tasks=["t_succ"],
        step_results={
            "t_succ": {"status": "SUCCESS", "findings": [{"x": 1}], "errors": []},
            "t_fail": {"status": "FAILED", "findings": [], "errors": ["fail"]},
            "t_time": {"status": "TIMEOUT", "findings": [], "errors": ["timeout"]},
            "t_skip": {"status": "NOT_EXECUTED", "findings": [], "errors": []}
        },
        errors=[]
    )
    handoff = HandoffPayload(
        workflow=workflow,
        workflow_result=workflow_result,
        synthesis_eligible=True,
        artifacts={}
    )

    synth_result = synthesize_result(handoff)

    attrs = {attr["task_id"]: attr for attr in synth_result["task_attributions"]}
    assert attrs["t_succ"]["status"] == "SUCCESS"
    assert attrs["t_fail"]["status"] == "FAILED"
    assert attrs["t_time"]["status"] == "TIMEOUT"
    assert attrs["t_skip"]["status"] == "NOT_EXECUTED"

def test_deterministic_declared_order():
    task1 = Task(task_id="t_b", objective="Task B", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING)
    task2 = Task(task_id="t_a", objective="Task A", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="wf_order", version="1.0", tasks=[task1, task2], status="running")

    workflow_result = WorkflowResult(
        workflow_id="wf_order",
        workflow_version="1.0",
        status=WorkflowResultStatus.SUCCESS,
        completed_tasks=["t_a", "t_b"],
        step_results={
            "t_a": {"status": "SUCCESS", "findings": [{"item": "a"}], "errors": []},
            "t_b": {"status": "SUCCESS", "findings": [{"item": "b"}], "errors": []}
        },
        errors=[]
    )
    handoff = HandoffPayload(
        workflow=workflow,
        workflow_result=workflow_result,
        synthesis_eligible=True,
        artifacts={}
    )

    synth_result = synthesize_result(handoff)

    assert synth_result["task_attributions"][0]["task_id"] == "t_b"
    assert synth_result["task_attributions"][1]["task_id"] == "t_a"
    assert synth_result["aggregated_findings"][0]["task_id"] == "t_b"
    assert synth_result["aggregated_findings"][0]["data"]["item"] == "b"
    assert synth_result["aggregated_findings"][1]["task_id"] == "t_a"
    assert synth_result["aggregated_findings"][1]["data"]["item"] == "a"

def test_provenance_augmentation():
    task1 = Task(task_id="t1", objective="Test", agent_id="a1", inputs={"operation": "TEST", "tool_id": "test_tool"}, status=TaskStatus.PENDING)
    workflow = Workflow(workflow_id="wf_prov", version="1.2", tasks=[task1], status="running")

    workflow_result = WorkflowResult(
        workflow_id="wf_prov",
        workflow_version="1.2",
        status=WorkflowResultStatus.SUCCESS,
        completed_tasks=["t1"],
        step_results={"t1": {"status": "SUCCESS", "findings": [], "errors": []}},
        provenance={"upstream_key": "upstream_value"}
    )
    handoff = HandoffPayload(
        workflow=workflow,
        workflow_result=workflow_result,
        synthesis_eligible=True,
        artifacts={}
    )

    synth_result = synthesize_result(handoff)

    prov = synth_result["provenance"]
    assert prov["upstream_key"] == "upstream_value"
    assert prov["synthesis_contract"] == "BIORCH-SYNTH-001"
    assert prov["synthesis_version"] == "1.0"
    assert prov["synthesis_status"] == "SUCCESS"
    assert prov["synthesis_task_count"] == 1
