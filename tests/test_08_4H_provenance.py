import pytest
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.agent import Agent
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.provenance_validator import ProvenanceValidator, ProvenanceValidationError
from biorch.core.result import Result, ResultStatus

@pytest.fixture
def mock_agent_executor():
    class DummyExecutor:
        def __init__(self):
            self.agent_definition = Agent(
                agent_id="agent1",
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

def test_valid_provenance_acceptance(mock_agent_executor):
    task1 = Task(
        task_id="t1",
        objective="Task 1",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=True
    )
    workflow = Workflow(workflow_id="wf_val", version="1.0", tasks=[task1], status="running")
    orchestrator = DeterministicOrchestrator(mock_agent_executor)
    synth_result = orchestrator.run_with_synthesis(workflow)

    validator = ProvenanceValidator(synth_result)
    assert validator.validate() is True

    checksum = validator.compute_audit_checksum()
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA-256 hex length
    assert validator.verify_audit_checksum(checksum) is True

def test_missing_required_provenance_field():
    synth_result = {
        "workflow_id": "wf_1",
        "workflow_version": "1.0",
        "status": "SUCCESS",
        "synthesis_eligible": True,
        "task_attributions": [{"task_id": "t1", "agent_id": "agent1", "status": "SUCCESS", "findings": [], "artifacts": [], "errors": []}],
        "aggregated_findings": [],
        "errors": [],
        "provenance": {
            "workflow_id": "wf_1",
            "workflow_version": "1.0",
            # missing synthesis_contract, synthesis_version, synthesis_status, synthesis_task_count
        }
    }
    validator = ProvenanceValidator(synth_result)
    with pytest.raises(ProvenanceValidationError, match="Missing required provenance field"):
        validator.validate()

def test_attribution_task_count_mismatch():
    synth_result = {
        "workflow_id": "wf_1",
        "workflow_version": "1.0",
        "status": "SUCCESS",
        "synthesis_eligible": True,
        "task_attributions": [{"task_id": "t1", "agent_id": "agent1", "status": "SUCCESS", "findings": [], "artifacts": [], "errors": []}],
        "aggregated_findings": [],
        "errors": [],
        "provenance": {
            "workflow_id": "wf_1",
            "workflow_version": "1.0",
            "synthesis_contract": "BIORCH-SYNTH-001",
            "synthesis_version": "1.0",
            "synthesis_status": "SUCCESS",
            "synthesis_task_count": 2  # Mismatch: only 1 task attribution provided
        }
    }
    validator = ProvenanceValidator(synth_result)
    with pytest.raises(ProvenanceValidationError, match="Task count mismatch"):
        validator.validate()

def test_attribution_missing_fields():
    synth_result = {
        "workflow_id": "wf_1",
        "workflow_version": "1.0",
        "status": "SUCCESS",
        "synthesis_eligible": True,
        "task_attributions": [{"agent_id": "agent1", "status": "SUCCESS", "findings": [], "artifacts": [], "errors": []}], # missing task_id
        "aggregated_findings": [],
        "errors": [],
        "provenance": {
            "workflow_id": "wf_1",
            "workflow_version": "1.0",
            "synthesis_contract": "BIORCH-SYNTH-001",
            "synthesis_version": "1.0",
            "synthesis_status": "SUCCESS",
            "synthesis_task_count": 1
        }
    }
    validator = ProvenanceValidator(synth_result)
    with pytest.raises(ProvenanceValidationError, match="Task attribution missing required 'task_id'"):
        validator.validate()

def test_tamper_detection(mock_agent_executor):
    task1 = Task(
        task_id="t1",
        objective="Task 1",
        agent_id="agent1",
        inputs={"operation": "TEST", "tool_id": "test_tool"},
        status=TaskStatus.PENDING,
        is_essential=True
    )
    workflow = Workflow(workflow_id="wf_tamper", version="1.0", tasks=[task1], status="running")
    orchestrator = DeterministicOrchestrator(mock_agent_executor)
    synth_result = orchestrator.run_with_synthesis(workflow)

    validator = ProvenanceValidator(synth_result)
    checksum = validator.compute_audit_checksum()

    # Tamper with synthesis result
    synth_result["status"] = "FAILED"

    validator_tampered = ProvenanceValidator(synth_result)
    with pytest.raises(ProvenanceValidationError, match="Audit checksum mismatch"):
        validator_tampered.verify_audit_checksum(checksum)
