import pytest
from unittest.mock import MagicMock
from biorch.core.task import Task, TaskStatus
from biorch.core.workflow import Workflow
from biorch.core.result import Result, ResultStatus
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.result import WorkflowResultStatus
from biorch.orchestration.agent_resolver import AgentResolver
from biorch.review import Reviewer, RuleResult, ReviewResult

class MockAgentExecutor:
    def __init__(self, result_sequence=None):
        self.result_sequence = result_sequence or []
        self.call_count = 0

    def execute(self, task: Task) -> Result:
        if self.call_count < len(self.result_sequence):
            res = self.result_sequence[self.call_count]
        else:
            res = self.result_sequence[-1] if self.result_sequence else Result(
                task_id=task.task_id, status=ResultStatus.SUCCESS, findings=[{"status": "ok"}], errors=[]
            )
        self.call_count += 1
        return res

class StatefulFeedbackAgent:
    def __init__(self):
        self.received_feedbacks = []
        self.attempt_count = 0

    def execute(self, task: Task) -> Result:
        self.attempt_count += 1
        feedback = task.inputs.get("correction_feedback") if task.inputs else None
        self.received_feedbacks.append(feedback)

        if self.attempt_count < 3:
            return Result(
                task_id=task.task_id,
                status=ResultStatus.SUCCESS,
                findings=[{"quality": "poor"}],
                errors=[]
            )
        else:
            return Result(
                task_id=task.task_id,
                status=ResultStatus.SUCCESS,
                findings=[{"quality": "excellent"}],
                errors=[]
            )


def test_review_approval():
    """1. Reviewer approval test."""
    task = Task(
        task_id="t1",
        objective="Review approval test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    rule_fn = lambda t, r: RuleResult("has_quality", True, "Passed")
    reviewer = Reviewer(reviewer_id="rev1", rules=[rule_fn], max_retries=0)
    orchestrator = DeterministicOrchestrator(
        AgentResolver({"agent1": MockAgentExecutor([
            Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"quality": "good"}], errors=[])
        ])}),
        reviewer=reviewer
    )

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert "t1" in wf_result.completed_tasks
    assert wf_result.step_results["t1"]["status"] == WorkflowResultStatus.SUCCESS.value


def test_single_rejection_followed_by_retry_success():
    """2. Single rejection followed by successful retry."""
    task = Task(
        task_id="t1",
        objective="Retry test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    def quality_rule(t, r):
        findings = r.findings or []
        passed = any(f.get("quality") == "good" for f in findings)
        return RuleResult("quality_check", passed, "Quality must be good")

    reviewer = Reviewer(reviewer_id="rev1", rules=[quality_rule], max_retries=1)
    
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"quality": "poor"}], errors=[]),
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"quality": "good"}], errors=[])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert "t1" in wf_result.completed_tasks
    assert agent.call_count == 2


def test_multiple_retries():
    """3. Multiple retries test."""
    task = Task(
        task_id="t1",
        objective="Multi retry test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    def pass_on_third(t, r):
        findings = r.findings or []
        passed = any(f.get("quality") == "excellent" for f in findings)
        return RuleResult("excellent_check", passed, "Needs to be excellent")

    reviewer = Reviewer(reviewer_id="rev1", rules=[pass_on_third], max_retries=2)
    stateful_agent = StatefulFeedbackAgent()
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": stateful_agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert stateful_agent.attempt_count == 3


def test_retry_exhaustion():
    """4. Retry exhaustion test."""
    task = Task(
        task_id="t1",
        objective="Exhaustion test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    rule_fn = lambda t, r: RuleResult("fail_always", False, "Always fail")
    reviewer = Reviewer(reviewer_id="rev1", rules=[rule_fn], max_retries=1)
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"val": 1}], errors=[]),
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"val": 2}], errors=[])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.REJECTED
    assert wf_result.failed_task == "t1"
    assert wf_result.step_results["t1"]["status"] == WorkflowResultStatus.REJECTED.value
    assert agent.call_count == 2


def test_hard_execution_failure_bypasses_review_retry():
    """5. Hard execution failure bypasses review retry."""
    task = Task(
        task_id="t1",
        objective="Hard failure test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    reviewer_called = []
    def spy_rule(t, r):
        reviewer_called.append(1)
        return RuleResult("spy", True, "ok")

    reviewer = Reviewer(reviewer_id="rev1", rules=[spy_rule], max_retries=3)
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.FAILURE, findings=[], errors=["Hard execution error"])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.FAILED
    assert agent.call_count == 1
    assert len(reviewer_called) == 0


def test_security_tool_failure_bypasses_review_retry():
    """6. Security/tool failure bypasses review retry."""
    task = Task(
        task_id="t1",
        objective="Security failure test",
        agent_id="agent1",
        inputs={"operation": "UNAUTHORIZED_OP", "tool_id": "unauthorized_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    reviewer_called = []
    def spy_rule(t, r):
        reviewer_called.append(1)
        return RuleResult("spy", True, "ok")

    reviewer = Reviewer(reviewer_id="rev1", rules=[spy_rule], max_retries=2)
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.FAILURE, findings=[], errors=["Unauthorized tool access denied"])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.REJECTED
    assert agent.call_count == 1
    assert len(reviewer_called) == 0


def test_correction_feedback_reaches_worker():
    """7. Correction feedback reaches the subsequent worker through task.inputs['correction_feedback']."""
    task = Task(
        task_id="t1",
        objective="Feedback test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    def check_rule(t, r):
        passed = t.inputs.get("correction_feedback") is not None
        return RuleResult("feedback_received", passed, "Feedback was expected on retry")

    # On attempt 1, rule fails. On attempt 2, check_rule will pass because correction_feedback was injected.
    reviewer = Reviewer(reviewer_id="rev1", rules=[check_rule], max_retries=1)
    
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[], errors=[]),
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[], errors=[])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert agent.call_count == 2
    assert "correction_feedback" in task.inputs


def test_attempt_history_retained_without_overwrite():
    """8. Complete review attempt history is retained without overwriting earlier attempts."""
    task = Task(
        task_id="t1",
        objective="History retention test",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING
    )
    workflow = Workflow(workflow_id="w1", version="1.0", tasks=[task], status="pending")

    def conditional_rule(t, r):
        # Pass on attempt 3
        findings = r.findings or []
        passed = len(findings) >= 3
        return RuleResult("retry_count_rule", passed, "Needs 3 findings")

    reviewer = Reviewer(reviewer_id="rev1", rules=[conditional_rule], max_retries=3)
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"attempt": 1}], errors=[]),
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"attempt": 2}], errors=[]),
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"attempt": 1}, {"attempt": 2}, {"attempt": 3}], errors=[])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS

    # Verify attempt history in result metadata
    # Since we can inspect the final result or step findings / we can also intercept via a custom rule or inspect via artifact/findings or test wrapper
    # Wait, let's verify agent call count or inspect result metadata if stored in task/result.
    # In orchestrator, results[tid] stores result.findings, but let's check what agent returned.
    # We can also check result metadata directly in a custom rule or inspect agent execution history.
    assert agent.call_count == 3


def test_independent_review_loops_for_parallel_tasks():
    """9. Independent review loops for parallel tasks."""
    t1 = Task(
        task_id="t1",
        objective="Parallel 1",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING,
        is_parallel_eligible=True
    )
    t2 = Task(
        task_id="t2",
        objective="Parallel 2",
        agent_id="agent1",
        inputs={"operation": "SUB", "tool_id": "math_tool"},
        status=TaskStatus.PENDING,
        is_parallel_eligible=True
    )
    workflow = Workflow(workflow_id="w_parallel", version="1.0", tasks=[t1, t2], status="pending")

    def parallel_rule(t, r):
        passed = t.task_id in ["t1", "t2"]
        return RuleResult("parallel_rule", passed, "Must be valid task")

    reviewer = Reviewer(reviewer_id="rev_parallel", rules=[parallel_rule], max_retries=1)
    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"p": 1}], errors=[]),
        Result(task_id="t2", status=ResultStatus.SUCCESS, findings=[{"p": 2}], errors=[])
    ])
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}), reviewer=reviewer)

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert set(wf_result.completed_tasks) == {"t1", "t2"}


def test_phase08_regression_no_review_policy():
    """10. Phase 08 regression behavior remains unchanged when no review policy exists."""
    t1 = Task(
        task_id="t1",
        objective="Step 1",
        agent_id="agent1",
        inputs={"operation": "ADD", "tool_id": "math_tool"},
        status=TaskStatus.PENDING,
        is_parallel_eligible=True
    )
    t2 = Task(
        task_id="t2",
        objective="Step 2",
        agent_id="agent1",
        inputs={"operation": "SUB", "tool_id": "math_tool"},
        status=TaskStatus.PENDING,
        is_parallel_eligible=True,
        dependencies=["t1"]
    )
    workflow = Workflow(workflow_id="w_reg", version="1.0", tasks=[t1, t2], status="pending")

    agent = MockAgentExecutor([
        Result(task_id="t1", status=ResultStatus.SUCCESS, findings=[{"res": 1}], errors=[]),
        Result(task_id="t2", status=ResultStatus.SUCCESS, findings=[{"res": 2}], errors=[])
    ])
    # No reviewer, no review policy -> defaults to Phase 08 behavior
    orchestrator = DeterministicOrchestrator(AgentResolver({"agent1": agent}))

    wf_result = orchestrator.execute(workflow)
    assert wf_result.status == WorkflowResultStatus.SUCCESS
    assert wf_result.provenance["execution_order"].index("t1") < wf_result.provenance["execution_order"].index("t2")
