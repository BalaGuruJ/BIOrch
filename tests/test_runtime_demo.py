import pytest
import os
from pathlib import Path
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.agent import Agent
from biorch.core.gateway import ToolGateway, ToolRegistry, ToolDefinition, ToolResult, ToolStatus
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.agent_resolver import AgentResolver
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.synthesis import synthesize_result
from biorch.orchestration.provenance_validator import ProvenanceValidator
from biorch.runtime_demo import RuntimeDemoGateway, run_demonstration


def test_runtime_demo_gateway_tableau_mock(tmp_path):
    """Verify RuntimeDemoGateway successfully executes Tableau pipeline when sample exists."""
    repo_root = Path(__file__).resolve().parent.parent
    tableau_input = repo_root / "examples/artifacts/tableau/superstore_base.twb"
    if not tableau_input.exists():
        pytest.skip("Tableau sample not found")

    registry = ToolRegistry()
    registry.register(ToolDefinition(
        tool_id="tableau_extractor",
        name="Tableau Metadata Extractor",
        purpose="Extract metadata",
        version="1.0",
        input_schema={"input_path": "str", "output_directory": "str"},
        output_schema={"source": "str"},
        allowed_resources=[str(repo_root), "/tmp/"],
        permitted_operations=["EXTRACT"],
        security_classification="INTERNAL"
    ))

    gateway = RuntimeDemoGateway(registry)
    output_dir = tmp_path / "tableau_out"

    res = gateway.invoke(
        tool_id="tableau_extractor",
        version="1.0",
        resource=str(tableau_input),
        operation="EXTRACT",
        inputs={
            "input_path": str(tableau_input),
            "output_directory": str(output_dir)
        }
    )

    assert res.status == ToolStatus.SUCCESS
    assert res.data["source"] == "tableau"
    assert "summary" in res.data
    assert len(res.provenance["artifacts"]) > 0


def test_runtime_demo_workflow_parallel_execution(tmp_path):
    """Verify DeterministicOrchestrator can execute two independent tasks in parallel."""
    repo_root = Path(__file__).resolve().parent.parent
    tableau_input = repo_root / "examples/artifacts/tableau/superstore_base.twb"
    pbi_input = repo_root / "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"

    if not tableau_input.exists() or not pbi_input.exists():
        pytest.skip("Samples not found")

    if not os.environ.get("DOTNET_ROOT") or not os.environ.get("BIORCH_TOM_DLL_PATH"):
        pytest.skip("Power BI environment prerequisites not set")

    registry = ToolRegistry()
    registry.register(ToolDefinition(
        tool_id="tableau_extractor",
        name="Tableau Metadata Extractor",
        purpose="Extract metadata",
        version="1.0",
        input_schema={"input_path": "str", "output_directory": "str"},
        output_schema={"source": "str"},
        allowed_resources=[str(repo_root), "/tmp/"],
        permitted_operations=["EXTRACT"],
        security_classification="INTERNAL"
    ))
    registry.register(ToolDefinition(
        tool_id="powerbi_adapter",
        name="Power BI Model Adapter",
        purpose="Analyze PBI model",
        version="1.0",
        input_schema={"model_folder": "str"},
        output_schema={"source": "str"},
        allowed_resources=[str(repo_root)],
        permitted_operations=["ANALYZE"],
        security_classification="INTERNAL"
    ))

    gateway = RuntimeDemoGateway(registry)

    tableau_agent_def = Agent(
        agent_id="tableau_agent",
        name="Tableau Agent",
        role="Extract",
        allowed_tools=["tableau_extractor"],
        supported_operations=["EXTRACT"]
    )
    pbi_agent_def = Agent(
        agent_id="powerbi_agent",
        name="Power BI Agent",
        role="Analyze",
        allowed_tools=["powerbi_adapter"],
        supported_operations=["ANALYZE"]
    )

    resolver = AgentResolver({
        "tableau_agent": DeterministicAgentExecutor(gateway, tableau_agent_def),
        "powerbi_agent": DeterministicAgentExecutor(gateway, pbi_agent_def)
    })

    t1 = Task(
        task_id="tableau_task",
        objective="Extract Tableau",
        agent_id="tableau_agent",
        dependencies=[],
        inputs={
            "tool_id": "tableau_extractor",
            "version": "1.0",
            "operation": "EXTRACT",
            "resource": str(tableau_input),
            "tool_inputs": {
                "input_path": str(tableau_input),
                "output_directory": str(tmp_path / "tableau")
            }
        },
        status=TaskStatus.PENDING
    )

    t2 = Task(
        task_id="pbi_task",
        objective="Analyze PBI",
        agent_id="powerbi_agent",
        dependencies=[],
        inputs={
            "tool_id": "powerbi_adapter",
            "version": "1.0",
            "operation": "ANALYZE",
            "resource": str(pbi_input),
            "tool_inputs": {
                "model_folder": str(pbi_input)
            }
        },
        status=TaskStatus.PENDING
    )

    workflow = Workflow(
        workflow_id="test_parallel_bi",
        version="1.0",
        tasks=[t1, t2],
        status="running"
    )

    orchestrator = DeterministicOrchestrator(resolver)
    handoff = orchestrator.run_with_handoff(workflow)

    assert handoff.workflow_result.status.value == "SUCCESS"
    assert "tableau_task" in handoff.workflow_result.completed_tasks
    assert "pbi_task" in handoff.workflow_result.completed_tasks

    # Test synthesis
    synthesis_result = synthesize_result(handoff)
    assert synthesis_result["status"] == "SUCCESS"
    assert len(synthesis_result["task_attributions"]) == 2

    # Test provenance validation
    validator = ProvenanceValidator(synthesis_result)
    assert validator.validate() is True
    checksum = validator.compute_audit_checksum()
    assert validator.verify_audit_checksum(checksum) is True


def test_runtime_demo_entrypoint_executes_repository_samples(capsys):
    """Verify the runtime demo authorizes and executes both repository samples."""
    if not os.environ.get("DOTNET_ROOT") or not os.environ.get("BIORCH_TOM_DLL_PATH"):
        pytest.skip("Power BI environment prerequisites not set")

    assert run_demonstration() == 0

    output = capsys.readouterr().out
    assert "Tableau\n" in output
    assert "Power BI\n" in output
    assert output.count("  status: SUCCESS") == 2
    assert "  task count: 2" in output
    assert "  parallel-ready tasks: 2" in output
    assert "  synthesis: SUCCESS" in output
    assert "  provenance: VALID" in output


def test_repeatable_runtime_command_callable():
    """Verify run_demonstration function is callable."""
    assert callable(run_demonstration)
