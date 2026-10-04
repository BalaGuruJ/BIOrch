from typing import List, Dict, Any, Optional
from biorch.core.workflow import Workflow
from biorch.core.result import Result, ResultStatus
from biorch.core.task import Task, TaskStatus
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.agent_resolver import AgentResolver, AgentNotFoundError
from .result import WorkflowResult, WorkflowResultStatus
from .handoff import HandoffPayload
from .join_gate import DeterministicJoinGate

class DeterministicOrchestrator:
    """
    Deterministic Orchestrator compliant with BIORCH-ORCH-001.
    Coordinates sequential execution of explicitly defined workflows through
    the DeterministicAgentExecutor without directly accessing lower-level gateways or tools.
    """
    def __init__(self, agent_resolver_or_executor, review_policy=None, reviewer=None, max_retries: int = 0):
        if isinstance(agent_resolver_or_executor, AgentResolver):
            self.agent_resolver = agent_resolver_or_executor
        else:
            # Backward compatibility for Phase 04 workflows
            self.agent_resolver = AgentResolver({
                agent_resolver_or_executor.agent_definition.agent_id: agent_resolver_or_executor
            })
            self.agent_executor = agent_resolver_or_executor
        self.collected_artifacts: Dict[str, Any] = {}
        self.review_policy = review_policy
        self.reviewer = reviewer
        self.max_retries = max_retries

    def run_with_handoff(self, workflow: Workflow) -> HandoffPayload:
        """
        Executes the workflow and returns a HandoffPayload via the Join Gate.
        """
        workflow_result = self.execute(workflow)
        return DeterministicJoinGate.evaluate(workflow, workflow_result, self.collected_artifacts)

    def run_with_synthesis(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Executes the workflow, evaluates the join gate, and performs result synthesis.
        """
        from .synthesis import synthesize_result
        handoff = self.run_with_handoff(workflow)
        return synthesize_result(handoff)

    def validate_workflow(self, workflow: Workflow) -> List[str]:
        """
        Validates all applicable workflow properties before execution:
        - workflow structure
        - workflow identifier
        - workflow version
        - step identifiers (non-empty and unique)
        - step ordering and dependency constraints
        - target agent availability
        - required inputs
        - supported operations and permitted tools
        - workflow constraints
        """
        errors: List[str] = []

        if not isinstance(workflow, Workflow):
            return ["Invalid workflow structure: expected Workflow instance"]

        # 1. Workflow identifier
        if not getattr(workflow, "workflow_id", None) or not isinstance(workflow.workflow_id, str) or not workflow.workflow_id.strip():
            errors.append("Workflow identifier must be a non-empty string")

        # 2. Workflow version
        if not getattr(workflow, "version", None) or not isinstance(workflow.version, str) or not workflow.version.strip():
            errors.append("Workflow version must be a non-empty string")

        # 3. Workflow structure (tasks list)
        if not hasattr(workflow, "tasks") or not isinstance(workflow.tasks, list) or len(workflow.tasks) == 0:
            errors.append("Workflow tasks cannot be empty")
            return errors

        seen_task_ids = set()

        for idx, task in enumerate(workflow.tasks):
            # 4. Malformed step validation
            if not isinstance(task, Task):
                errors.append(f"Step at index {idx} is malformed: expected Task instance")
                continue

            # 5. Step identifier
            if not getattr(task, "task_id", None) or not isinstance(task.task_id, str) or not task.task_id.strip():
                errors.append(f"Step at index {idx} has invalid or missing step identifier")
                continue

            if task.task_id in seen_task_ids:
                errors.append(f"Duplicate step identifier: {task.task_id}")
            seen_task_ids.add(task.task_id)

            # 6. Step ordering and dependencies
            if getattr(task, "dependencies", None):
                for dep in task.dependencies:
                    if dep == task.task_id:
                        errors.append(f"Step '{task.task_id}' cannot depend on itself")
                    elif dep not in seen_task_ids:
                        errors.append(
                            f"Step '{task.task_id}' has invalid dependency '{dep}': "
                            "dependencies must precede the step in sequential order"
                        )

            # 7. Target agent availability
            if not getattr(task, "agent_id", None) or not isinstance(task.agent_id, str) or not task.agent_id.strip():
                errors.append(f"Step '{task.task_id}' missing target agent identifier")
            else:
                try:
                    executor = self.agent_resolver.resolve(task.agent_id)
                    agent_def = getattr(executor, "agent_definition", None)
                except AgentNotFoundError:
                    errors.append(f"Target agent '{task.agent_id}' is not available for step '{task.task_id}'")
                    continue

                # 8. Required inputs
                if not hasattr(task, "inputs") or task.inputs is None or not isinstance(task.inputs, dict):
                    errors.append(f"Step '{task.task_id}' is missing required inputs")
                else:
                    op = task.inputs.get("operation")
                    tool_id = task.inputs.get("tool_id")

                    if not op or not isinstance(op, str) or not op.strip():
                        errors.append(f"Step '{task.task_id}' is missing required input: operation")
                    if not tool_id or not isinstance(tool_id, str) or not tool_id.strip():
                        errors.append(f"Step '{task.task_id}' is missing required input: tool_id")

                    # 9. Supported operations and permitted tools (agent boundary)
                    if agent_def:
                        if getattr(agent_def, "supported_operations", None) is not None and isinstance(op, str) and op.strip():
                            if op not in agent_def.supported_operations:
                                errors.append(f"Unsupported operation '{op}' for step '{task.task_id}'")
                        if getattr(agent_def, "allowed_tools", None) is not None and isinstance(tool_id, str) and tool_id.strip():
                            if tool_id not in agent_def.allowed_tools:
                                errors.append(f"Unauthorized tool '{tool_id}' for step '{task.task_id}'")

            # 10. Step constraints
            if getattr(task, "status", None) in ("failed", "cancelled"):
                errors.append(f"Step '{task.task_id}' is in terminal status '{task.status}' and cannot be executed")

        return errors

    def validate(self, workflow: Workflow) -> bool:
        """
        Performs workflow validation, returning True if valid, False otherwise.
        """
        return len(self.validate_workflow(workflow)) == 0

    def _is_rejection(self, result: Result) -> bool:
        """
        Determines whether a step outcome represents an authorization or policy rejection
        rather than a runtime execution failure.
        """
        if result.metadata and result.metadata.get("review", {}).get("final_approved") is False:
            return True
        if hasattr(result, "status") and str(result.status).lower() in ("rejected", "resultstatus.rejected"):
            return True

        rejection_indicators = (
            "unauthorized",
            "unknown tool",
            "incorrect tool version",
            "missing required",
            "validation",
            "rejected",
            "permission denied",
            "access denied",
        )
        for err in (result.errors or []):
            err_lower = err.lower()
            if any(ind in err_lower for ind in rejection_indicators):
                return True
        return False

    def _get_reviewer_and_retries(self, task: Task):
        from biorch.review import Reviewer
        task_review = task.metadata.get("review") if task.metadata else None
        task_policy = task.metadata.get("review_policy") if task.metadata else None

        reviewer = None
        max_retries = self.max_retries

        if task_review and isinstance(task_review, dict):
            if "reviewer" in task_review:
                reviewer = task_review["reviewer"]
            if "max_retries" in task_review:
                max_retries = int(task_review["max_retries"])
        elif task_policy and isinstance(task_policy, dict):
            if "reviewer" in task_policy:
                reviewer = task_policy["reviewer"]
            if "max_retries" in task_policy:
                max_retries = int(task_policy["max_retries"])
        elif task_policy and hasattr(task_policy, "evaluate"):
            reviewer = task_policy

        if not reviewer:
            reviewer = self.reviewer
        if not reviewer and self.review_policy:
            if hasattr(self.review_policy, "evaluate"):
                reviewer = self.review_policy
            elif isinstance(self.review_policy, dict):
                reviewer = self.review_policy.get("reviewer")
                if "max_retries" in self.review_policy:
                    max_retries = int(self.review_policy["max_retries"])

        if isinstance(reviewer, list):
            reviewer = Reviewer(rules=reviewer, max_retries=max_retries)

        if reviewer and hasattr(reviewer, "max_retries") and reviewer.max_retries > 0 and max_retries == 0:
            max_retries = reviewer.max_retries

        return reviewer, max_retries

    def _execute_task_with_review(self, task: Task) -> Result:
        executor = self.agent_resolver.resolve(task.agent_id)
        reviewer, max_retries = self._get_reviewer_and_retries(task)

        if not reviewer:
            return executor.execute(task)

        attempt_number = 1
        attempt_history = []

        while True:
            result = executor.execute(task)

            # Hard execution failure or tool/security failure bypasses review retry
            if result.status != ResultStatus.SUCCESS:
                return result

            review_result = reviewer.evaluate(task, result)

            attempt_record = {
                "attempt_number": attempt_number,
                "reviewer_id": getattr(reviewer, "reviewer_id", "default_reviewer"),
                "rule_results": [r.to_dict() for r in review_result.rule_results],
                "correction_feedback": review_result.correction_feedback
            }
            attempt_history.append(attempt_record)

            if result.metadata is None:
                result.metadata = {}
            result.metadata["review"] = {
                "attempt_history": attempt_history,
                "final_approved": review_result.approved
            }

            if review_result.approved:
                return result

            # Review rejected
            if attempt_number > max_retries:
                result.status = ResultStatus.FAILURE
                if not result.errors:
                    result.errors = []
                if review_result.correction_feedback:
                    result.errors.append(review_result.correction_feedback)
                return result

            # Retries remain: inject correction feedback into task.inputs["correction_feedback"]
            if task.inputs is None:
                task.inputs = {}
            task.inputs["correction_feedback"] = review_result.correction_feedback
            attempt_number += 1

    def execute(self, workflow: Workflow) -> WorkflowResult:
        """
        Executes the workflow, supporting both sequential and parallel execution.
        Fails closed on validation failure before executing any steps.
        Preserves dependency order and fail-fast termination on step failure/rejection.
        """
        validation_errors = self.validate_workflow(workflow)
        workflow_version = getattr(workflow, "version", "1.0") or "1.0"
        workflow_id = getattr(workflow, "workflow_id", "") or ""
        self.collected_artifacts = {}

        # Fail closed before any step executes
        if validation_errors:
            task_ids = (
                [t.task_id for t in workflow.tasks if hasattr(t, "task_id") and isinstance(t.task_id, str)]
                if hasattr(workflow, "tasks") and isinstance(workflow.tasks, list)
                else []
            )
            step_results = {
                tid: {
                    "status": WorkflowResultStatus.NOT_EXECUTED.value,
                    "findings": [],
                    "errors": ["Workflow validation failed before execution"]
                }
                for tid in task_ids
            }
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_version=workflow_version,
                status=WorkflowResultStatus.REJECTED,
                completed_tasks=[],
                failed_task=None,
                not_executed_tasks=task_ids,
                results={},
                step_results=step_results,
                errors=validation_errors,
                provenance={
                    "workflow_id": workflow_id,
                    "workflow_version": workflow_version,
                    "validation_passed": False,
                    "execution_order": [],
                    "completed_steps": [],
                    "failed_step": None,
                    "terminal_status": WorkflowResultStatus.REJECTED.value
                }
            )

        from concurrent.futures import ThreadPoolExecutor

        completed_tasks: List[str] = []
        executed_order: List[str] = []
        results: Dict[str, Any] = {}
        step_results: Dict[str, Any] = {}

        # Track task status
        pending_tasks = {task.task_id: task for task in workflow.tasks}
        in_progress_tasks: Dict[str, Task] = {}

        def execute_task(task: Task) -> Result:
            return self._execute_task_with_review(task)

        # Main execution loop
        with ThreadPoolExecutor() as executor:
            futures: Dict[str, Any] = {} # Map tid -> {"future": Future, "task": Task, "start_time": float}

            while pending_tasks or futures:
                # Identify ready tasks
                ready_tasks = []
                for tid, task in pending_tasks.items():
                    dependencies_met = all(dep in completed_tasks for dep in task.dependencies)
                    if dependencies_met:
                        ready_tasks.append(task)

                # Sort ready tasks deterministically
                ready_tasks.sort(key=lambda t: t.task_id)

                # Check for parallel dispatch opportunities
                if not ready_tasks:
                    if futures:
                        # Wait for at least one future to complete or timeout
                        from concurrent.futures import wait, FIRST_COMPLETED

                        # Calculate wait time based on earliest timeout
                        timeout_val = None
                        now = time.time()

                        min_timeout = None
                        for tid, f_data in futures.items():
                            task = f_data["task"]
                            timeout = task.metadata.get("timeout") if task.metadata else None
                            if timeout:
                                elapsed = now - f_data["start_time"]
                                remaining = timeout - elapsed
                                if min_timeout is None or remaining < min_timeout:
                                    min_timeout = max(0, remaining)

                        wait([f_data["future"] for f_data in futures.values()], timeout=min_timeout, return_when=FIRST_COMPLETED)
                    else:
                        # Workflow completed or stuck
                        if pending_tasks:
                            # Workflow stuck: mark remaining as NOT_EXECUTED
                            for tid in list(pending_tasks.keys()):
                                step_results[tid] = {
                                    "status": WorkflowResultStatus.NOT_EXECUTED.value,
                                    "findings": [],
                                    "errors": ["Workflow stuck: dependencies not met"]
                                }
                        break # Workflow completed or stuck

                # Handle future completions and timeouts
                import time
                now = time.time()

                done = []
                timed_out = []

                for tid, f_data in futures.items():
                    if f_data["future"].done():
                        done.append(tid)
                    else:
                        task = f_data["task"]
                        timeout = task.metadata.get("timeout") if task.metadata else None
                        if timeout:
                            elapsed = now - f_data["start_time"]
                            if elapsed >= float(timeout):
                                timed_out.append(tid)

                # Handle timeouts first
                for tid in timed_out:
                    f_data = futures.pop(tid)
                    task = in_progress_tasks.pop(tid)
                    f_data["future"].cancel() # Best-effort cancellation

                    # Record timeout status
                    step_results[tid] = {
                        "status": TaskStatus.TIMEOUT.value,
                        "findings": [],
                        "errors": ["Task timed out"]
                    }

                    # Handle failure classification
                    if getattr(task, "is_essential", True):
                        return self._create_terminal_failure(
                            workflow_id, workflow_version, WorkflowResultStatus.FAILED,
                            completed_tasks, tid, {**pending_tasks, **in_progress_tasks}, step_results,
                            executed_order, results, ["Task timed out: essential task failure"]
                        )
                    else:
                        # Non-essential failure: record, block dependents, and continue
                        self._block_dependents(tid, pending_tasks, step_results)


                # Handle completions
                for tid in done:
                    f_data = futures.pop(tid)
                    task = in_progress_tasks.pop(tid)

                    try:
                        result = f_data["future"].result()
                    except Exception as e:
                        # Exception as terminal failure
                        if getattr(task, "is_essential", True):
                            failed_task = tid
                            return self._create_terminal_failure(
                                workflow_id, workflow_version, WorkflowResultStatus.FAILED,
                                completed_tasks, failed_task, {**pending_tasks, **in_progress_tasks}, step_results,
                                executed_order, results, [str(e)]
                            )
                        else:
                            step_results[tid] = {
                                "status": WorkflowResultStatus.FAILED.value,
                                "findings": [],
                                "errors": [str(e)]
                            }
                            continue

                    if result.status == ResultStatus.SUCCESS:
                        completed_tasks.append(tid)
                        executed_order.append(tid)
                        results[tid] = result.findings
                        self.collected_artifacts[tid] = result.artifacts
                        step_results[tid] = {
                            "status": WorkflowResultStatus.SUCCESS.value,
                            "findings": result.findings,
                            "errors": []
                        }
                    else:
                        # Failure classification
                        is_essential = getattr(task, "is_essential", True)
                        is_review_rejection = self._is_rejection(result)
                        if is_essential:
                            failed_task = tid
                            return self._create_terminal_failure(
                                workflow_id, workflow_version,
                                WorkflowResultStatus.REJECTED if is_review_rejection else WorkflowResultStatus.FAILED,
                                completed_tasks, failed_task, {**pending_tasks, **in_progress_tasks}, step_results,
                                executed_order, results, result.errors
                            )
                        else:
                            # Non-essential failure: record, block dependents, and continue
                            step_results[tid] = {
                                "status": WorkflowResultStatus.REJECTED.value if is_review_rejection else WorkflowResultStatus.FAILED.value,
                                "findings": [],
                                "errors": result.errors
                            }
                            self._block_dependents(tid, pending_tasks, step_results)

                # Dispatch tasks
                for task in ready_tasks:
                    if task.task_id in futures:
                        continue

                    # Dispatch
                    future = executor.submit(execute_task, task)
                    futures[task.task_id] = {
                        "future": future,
                        "task": task,
                        "start_time": time.time()
                    }
                    in_progress_tasks[task.task_id] = pending_tasks.pop(task.task_id)

                    # If not parallel-eligible, wait for this task to finish before dispatching more
                    if not task.is_parallel_eligible:
                        from concurrent.futures import wait
                        timeout = task.metadata.get("timeout") if task.metadata else None
                        timeout_val = float(timeout) if timeout else None
                        wait([futures[task.task_id]["future"]], timeout=timeout_val)
                        break # Need to re-evaluate ready tasks

        return WorkflowResult(
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            status=WorkflowResultStatus.SUCCESS,
            completed_tasks=completed_tasks,
            failed_task=None,
            not_executed_tasks=[],
            results=results,
            step_results=self._reconcile_terminal_outcomes(workflow, step_results),
            errors=[],
            provenance={
                "workflow_id": workflow_id,
                "workflow_version": workflow_version,
                "validation_passed": True,
                "execution_order": executed_order,
                "completed_steps": completed_tasks,
                "failed_step": None,
                "terminal_status": WorkflowResultStatus.SUCCESS.value
            }
        )

    def _reconcile_terminal_outcomes(self, workflow: Workflow, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies that all dispatched tasks have reached a terminal status.
        Raises RuntimeError if any task is missing or has a non-terminal status.
        """
        terminal_statuses = {
            WorkflowResultStatus.SUCCESS.value,
            WorkflowResultStatus.FAILED.value,
            WorkflowResultStatus.REJECTED.value,
            TaskStatus.TIMEOUT.value,
            WorkflowResultStatus.NOT_EXECUTED.value
        }

        for task in workflow.tasks:
            tid = task.task_id
            if tid not in step_results:
                raise RuntimeError(f"Task '{tid}' is missing from terminal step_results.")

            status = step_results[tid].get("status")
            if status not in terminal_statuses:
                raise RuntimeError(f"Task '{tid}' has non-terminal status: '{status}'.")

        return step_results

    def _create_terminal_failure(
        self, workflow_id, workflow_version, terminal_status,
        completed_tasks, failed_task, pending_tasks, step_results,
        executed_order, results, errors
    ) -> WorkflowResult:

        # Prepare step results for all tasks
        # completed_tasks are already in step_results

        # Add failed task
        existing_status = step_results.get(failed_task, {}).get("status")
        final_status = existing_status if existing_status == TaskStatus.TIMEOUT.value else terminal_status.value

        step_results[failed_task] = {
            "status": final_status,
            "findings": [],
            "errors": errors
        }

        # Mark remaining tasks as NOT_EXECUTED
        not_executed_tasks = []
        for tid, task in pending_tasks.items():
            if tid != failed_task:
                step_results[tid] = {
                    "status": WorkflowResultStatus.NOT_EXECUTED.value,
                    "findings": [],
                    "errors": []
                }
                not_executed_tasks.append(tid)

        return WorkflowResult(
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            status=terminal_status,
            completed_tasks=completed_tasks,
            failed_task=failed_task,
            not_executed_tasks=not_executed_tasks,
            results=results,
            step_results=step_results,
            errors=errors,
            provenance={
                "workflow_id": workflow_id,
                "workflow_version": workflow_version,
                "validation_passed": True,
                "execution_order": executed_order + [failed_task],
                "completed_steps": completed_tasks,
                "failed_step": failed_task,
                "terminal_status": terminal_status.value
            }
        )

    def _block_dependents(self, blocked_tid: str, pending_tasks: Dict[str, Task], step_results: Dict[str, Any]):
        """
        Recursively marks direct and transitive dependents of a blocked task as NOT_EXECUTED.
        """
        dependents = [tid for tid, task in pending_tasks.items() if blocked_tid in task.dependencies]
        for tid in dependents:
            step_results[tid] = {
                "status": WorkflowResultStatus.NOT_EXECUTED.value,
                "findings": [],
                "errors": [f"Dependency '{blocked_tid}' failed or timed out"]
            }
            pending_tasks.pop(tid)
            self._block_dependents(tid, pending_tasks, step_results)
