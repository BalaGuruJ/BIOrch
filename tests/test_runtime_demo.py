import pytest
import os
import time
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


def test_runtime_demo_evidence_bundle_generation(tmp_path):
    """Verify run_demonstration generates a complete evidence bundle on execution."""
    repo_root = Path(__file__).resolve().parent.parent
    tableau_input = repo_root / "examples/artifacts/tableau/superstore_base.twb"
    if not tableau_input.exists():
        pytest.skip("Tableau sample not found")

    # Run demonstration targeting tmp_path
    run_demonstration(output_base_dir=tmp_path)

    # Verify run directory was created under tmp_path
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]

    expected_files = [
        "run_manifest.json",
        "workflow.json",
        "execution.json",
        "tableau_result.json",
        "powerbi_result.json",
        "provenance.json",
        "synthesis.json",
        "run_summary.md"
    ]

    for fname in expected_files:
        fpath = run_dir / fname
        assert fpath.exists(), f"Expected evidence file {fname} not found in {run_dir}"
        if fname.endswith(".json"):
            import json
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert isinstance(data, (dict, list))
        elif fname.endswith(".md"):
            content = fpath.read_text(encoding="utf-8")
            assert "# BIOrch Demo #1 — Run Summary" in content


def test_runtime_demo_execution_metrics_and_concurrency_proof(tmp_path):
    """Verify execution.json contains per-task execution timestamps, duration, thread ID, and concurrency proof."""
    if not os.environ.get("DOTNET_ROOT") or not os.environ.get("BIORCH_TOM_DLL_PATH"):
        pytest.skip("Power BI environment prerequisites not set")

    repo_root = Path(__file__).resolve().parent.parent
    tableau_input = repo_root / "examples/artifacts/tableau/superstore_base.twb"
    if not tableau_input.exists():
        pytest.skip("Tableau sample not found")

    run_demonstration(output_base_dir=tmp_path)
    run_dir = next(tmp_path.glob("run_*"))
    execution_json_path = run_dir / "execution.json"

    assert execution_json_path.exists()
    import json
    with open(execution_json_path, "r", encoding="utf-8") as f:
        exec_data = json.load(f)

    assert "task_execution_metrics" in exec_data
    assert "concurrency_proof" in exec_data

    metrics = exec_data["task_execution_metrics"]
    assert "tableau_task" in metrics

    t_metrics = metrics["tableau_task"]
    assert "start_timestamp" in t_metrics
    assert "end_timestamp" in t_metrics
    assert "duration_seconds" in t_metrics
    assert "thread_id" in t_metrics
    assert "thread_name" in t_metrics
    assert "status" in t_metrics

    proof = exec_data["concurrency_proof"]
    assert "overlap_detected" in proof
    assert "distinct_threads_used" in proof
    assert "parallel_execution_verified" in proof


def test_timed_agent_executor_concurrency_proof():
    """Directly test TimedAgentExecutor timing collection and concurrent execution metrics."""
    from biorch.runtime_demo import TimedAgentExecutor
    from biorch.core.result import Result, ResultStatus
    metrics = {}

    class MockInnerExecutor:
        def __init__(self, agent_id, delay=0.01):
            self.agent_id = agent_id
            self.agent_definition = Agent(agent_id=agent_id, name=agent_id, role="test", allowed_tools=[], supported_operations=[])
            self.delay = delay

        def execute(self, task: Task) -> Result:
            time.sleep(self.delay)
            return Result(task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[{"summary": {"test": 1}}])

    exec1 = TimedAgentExecutor(MockInnerExecutor("agent1", delay=0.02), metrics)
    exec2 = TimedAgentExecutor(MockInnerExecutor("agent2", delay=0.02), metrics)

    t1 = Task(task_id="task1", objective="o1", agent_id="agent1", inputs={"tool_id": "t", "operation": "EXTRACT"}, status=TaskStatus.PENDING)
    t2 = Task(task_id="task2", objective="o2", agent_id="agent2", inputs={"tool_id": "t", "operation": "EXTRACT"}, status=TaskStatus.PENDING)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(exec1.execute, t1)
        f2 = executor.submit(exec2.execute, t2)
        concurrent.futures.wait([f1, f2])

    assert "task1" in metrics
    assert "task2" in metrics
    assert metrics["task1"]["status"] == "SUCCESS"
    assert metrics["task2"]["status"] == "SUCCESS"
    assert "start_timestamp" in metrics["task1"]
    assert "end_timestamp" in metrics["task1"]
    assert "duration_seconds" in metrics["task1"]
    assert "thread_id" in metrics["task1"]



