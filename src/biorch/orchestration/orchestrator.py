from typing import List, Dict, Any, Optional
from biorch.core.workflow import Workflow
from biorch.core.result import Result, ResultStatus
from biorch.core.task import Task
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.agent_resolver import AgentResolver, AgentNotFoundError
from .result import WorkflowResult, WorkflowResultStatus

class DeterministicOrchestrator:
    """
    Deterministic Orchestrator compliant with BIORCH-ORCH-001.
    Coordinates sequential execution of explicitly defined workflows through
    the DeterministicAgentExecutor without directly accessing lower-level gateways or tools.
    """
    def __init__(self, agent_resolver_or_executor):
        if isinstance(agent_resolver_or_executor, AgentResolver):
            self.agent_resolver = agent_resolver_or_executor
        else:
            # Backward compatibility for Phase 04 workflows
            self.agent_resolver = AgentResolver({
                agent_resolver_or_executor.agent_definition.agent_id: agent_resolver_or_executor
            })
            self.agent_executor = agent_resolver_or_executor

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

    def execute(self, workflow: Workflow) -> WorkflowResult:
        """
        Executes the workflow sequentially and returns a structured result.
        Fails closed on validation failure before executing any steps.
        Preserves declared order and fail-fast termination on step failure/rejection.
        """
        validation_errors = self.validate_workflow(workflow)
        workflow_version = getattr(workflow, "version", "1.0") or "1.0"
        workflow_id = getattr(workflow, "workflow_id", "") or ""

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

        completed_tasks: List[str] = []
        executed_order: List[str] = []
        results: Dict[str, Any] = {}
        step_results: Dict[str, Any] = {}

        for i, task in enumerate(workflow.tasks):
            executed_order.append(task.task_id)
            
            try:
                executor = self.agent_resolver.resolve(task.agent_id)
                result = executor.execute(task)
            except AgentNotFoundError:
                # Terminal workflow failure
                failed_task = task.task_id
                terminal_status = WorkflowResultStatus.FAILED
                
                step_results[task.task_id] = {
                    "status": WorkflowResultStatus.FAILED.value,
                    "findings": [],
                    "errors": [f"Agent '{task.agent_id}' not found during execution"]
                }
                
                # Mark remaining tasks as NOT_EXECUTED
                remaining_tasks = workflow.tasks[i + 1:]
                not_executed_tasks = [t.task_id for t in remaining_tasks]
                for t in remaining_tasks:
                    step_results[t.task_id] = {
                        "status": WorkflowResultStatus.NOT_EXECUTED.value,
                        "findings": [],
                        "errors": []
                    }

                return WorkflowResult(
                    workflow_id=workflow_id,
                    workflow_version=workflow_version,
                    status=terminal_status,
                    completed_tasks=completed_tasks,
                    failed_task=failed_task,
                    not_executed_tasks=not_executed_tasks,
                    results=results,
                    step_results=step_results,
                    errors=[f"Agent '{task.agent_id}' not found during execution"],
                    provenance={
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "validation_passed": True,
                        "execution_order": executed_order,
                        "completed_steps": completed_tasks,
                        "failed_step": failed_task,
                        "terminal_status": terminal_status.value
                    }
                )

            if result.status == ResultStatus.SUCCESS:
                completed_tasks.append(task.task_id)
                findings = result.findings or []
                results[task.task_id] = findings
                step_results[task.task_id] = {
                    "status": WorkflowResultStatus.SUCCESS.value,
                    "findings": findings,
                    "errors": []
                }
            else:
                # Fail-fast
                failed_task = task.task_id
                is_rejection = self._is_rejection(result)
                terminal_status = (
                    WorkflowResultStatus.REJECTED if is_rejection else WorkflowResultStatus.FAILED
                )
                step_status = (
                    WorkflowResultStatus.REJECTED.value if is_rejection else WorkflowResultStatus.FAILED.value
                )
                step_results[task.task_id] = {
                    "status": step_status,
                    "findings": [],
                    "errors": result.errors or []
                }

                # Mark remaining tasks as NOT_EXECUTED
                remaining_tasks = workflow.tasks[i + 1:]
                not_executed_tasks = [t.task_id for t in remaining_tasks]
                for t in remaining_tasks:
                    step_results[t.task_id] = {
                        "status": WorkflowResultStatus.NOT_EXECUTED.value,
                        "findings": [],
                        "errors": []
                    }

                return WorkflowResult(
                    workflow_id=workflow_id,
                    workflow_version=workflow_version,
                    status=terminal_status,
                    completed_tasks=completed_tasks,
                    failed_task=failed_task,
                    not_executed_tasks=not_executed_tasks,
                    results=results,
                    step_results=step_results,
                    errors=result.errors or [],
                    provenance={
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "validation_passed": True,
                        "execution_order": executed_order,
                        "completed_steps": completed_tasks,
                        "failed_step": failed_task,
                        "terminal_status": terminal_status.value
                    }
                )

        return WorkflowResult(
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            status=WorkflowResultStatus.SUCCESS,
            completed_tasks=completed_tasks,
            failed_task=None,
            not_executed_tasks=[],
            results=results,
            step_results=step_results,
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
