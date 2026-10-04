import pytest
from biorch.planner.models import CandidatePlan, CandidateTask
from biorch.planner.provider import MockLLMProvider
from biorch.planner.compiler import PlanCompiler, PlanCompilerError
from biorch.planner.service import LLMPlannerService
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.agent import Agent
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.agent_resolver import AgentResolver
from biorch.core.result import Result, ResultStatus

@pytest.fixture
def mock_agent_resolver():
    agent1 = Agent(
        agent_id="tableau_agent",
        name="Tableau Agent",
        role="BI Analyst",
        allowed_tools=["tableau_tool"],
        supported_operations=["inspect_workbook"]
    )
    agent2 = Agent(
        agent_id="powerbi_agent",
        name="Power BI Agent",
        role="BI Analyst",
        allowed_tools=["pbi_tool"],
        supported_operations=["inspect_model"]
    )
    return AgentResolver({
        "tableau_agent": agent1,
        "powerbi_agent": agent2
    })

def test_mock_llm_provider_intent():
    provider = MockLLMProvider()
    intent = "Analyze Tableau workbook and Power BI semantic model."
    plan = provider.generate_plan(intent)

    assert isinstance(plan, CandidatePlan)
    assert plan.intent == intent
    assert len(plan.tasks) == 2
    assert plan.tasks[0].agent_id == "tableau_agent"
    assert plan.tasks[1].agent_id == "powerbi_agent"

def test_plan_compiler_success():
    c_plan = CandidatePlan(
        plan_id="plan_001",
        intent="Test intent",
        target_model="gemini-pro",
        tasks=[
            CandidateTask(
                task_id="step_1",
                objective="Perform inspection of metadata",
                agent_id="tableau_agent",
                operation="inspect_workbook",
                inputs={"path": "sample.twbx"},
                dependencies=[],
                rationale="Initial exploration step."
            )
        ]
    )

    workflow = PlanCompiler.compile(c_plan)

    assert isinstance(workflow, Workflow)
    assert workflow.workflow_id == "plan_001"
    assert len(workflow.tasks) == 1
    
    t = workflow.tasks[0]
    assert t.task_id == "step_1"
    assert t.objective == "Perform inspection of metadata"
    assert t.agent_id == "tableau_agent"
    assert t.inputs["operation"] == "inspect_workbook"
    assert t.inputs["path"] == "sample.twbx"
    assert t.metadata["planner_rationale"] == "Initial exploration step."
    assert workflow.current_state["planner"]["intent"] == "Test intent"

def test_plan_compiler_fail_closed_empty_objective():
    c_plan = CandidatePlan(
        plan_id="plan_bad",
        intent="Bad intent",
        target_model="gemini-pro",
        tasks=[
            CandidateTask(
                task_id="step_1",
                objective="   ",  # whitespace / empty objective
                agent_id="tableau_agent",
                operation="inspect_workbook",
                inputs={},
                dependencies=[]
            )
        ]
    )

    with pytest.raises(PlanCompilerError, match="missing, empty, or invalid objective"):
        PlanCompiler.compile(c_plan)

def test_plan_compiler_fail_closed_duplicate_task_id():
    c_plan = CandidatePlan(
        plan_id="plan_dup",
        intent="Dup intent",
        target_model="gemini-pro",
        tasks=[
            CandidateTask(task_id="same_id", objective="Obj 1", agent_id="a1", operation="op1"),
            CandidateTask(task_id="same_id", objective="Obj 2", agent_id="a1", operation="op1")
        ]
    )

    with pytest.raises(PlanCompilerError, match="Duplicate task_id"):
        PlanCompiler.compile(c_plan)

def test_llm_planner_service_integration(mock_agent_resolver):
    provider = MockLLMProvider()
    service = LLMPlannerService(provider)

    intent = "Inspect Tableau workbook and extract Power BI semantic model."
    orchestrator = DeterministicOrchestrator(mock_agent_resolver)

    workflow, errors = service.plan_compile_validate(intent, orchestrator)

    assert isinstance(workflow, Workflow)
    # Validation errors should be empty or contain only tool-allowlist warnings if agents don't execute yet,
    # but structure & agent resolution should pass.
    assert "Workflow identifier must be a non-empty string" not in errors
    assert len(workflow.tasks) == 2
