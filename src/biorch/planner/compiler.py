from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from .models import CandidatePlan, CandidateTask

class PlanCompilerError(Exception):
    """Raised when plan compilation fails validation rules."""
    pass

class PlanCompiler:
    """
    Pure, deterministic compiler translating CandidatePlan -> canonical Workflow and Task instances.
    Enforces 1:1 non-empty objective mapping and provenance injection.
    """
    @staticmethod
    def compile(candidate_plan: CandidatePlan) -> Workflow:
        if not candidate_plan:
            raise PlanCompilerError("Cannot compile null or empty candidate plan.")
        
        if not candidate_plan.tasks:
            raise PlanCompilerError(f"Candidate plan '{candidate_plan.plan_id}' contains no tasks.")

        compiled_tasks: List[Task] = []
        seen_task_ids = set()

        for c_task in candidate_plan.tasks:
            if not c_task.task_id or not isinstance(c_task.task_id, str) or not c_task.task_id.strip():
                raise PlanCompilerError("Candidate task has missing or invalid task_id.")
            
            if c_task.task_id in seen_task_ids:
                raise PlanCompilerError(f"Duplicate task_id in candidate plan: {c_task.task_id}")
            seen_task_ids.add(c_task.task_id)

            # Strict 1:1 objective requirement (fail closed if missing or empty/whitespace)
            if not c_task.objective or not isinstance(c_task.objective, str) or not c_task.objective.strip():
                raise PlanCompilerError(
                    f"Candidate task '{c_task.task_id}' has missing, empty, or invalid objective. "
                    "Objective mapping requires an explicit, non-empty string."
                )

            task_inputs = c_task.inputs or {}
            meta = {}
            if c_task.rationale:
                meta["planner_rationale"] = c_task.rationale

            task = Task(
                task_id=c_task.task_id,
                objective=c_task.objective.strip(),
                agent_id=c_task.agent_id,
                inputs={
                    "operation": c_task.operation,
                    **task_inputs
                } if c_task.operation else task_inputs,
                dependencies=c_task.dependencies or [],
                metadata=meta,
                status=TaskStatus.PENDING,
                is_parallel_eligible=True,
                is_essential=True
            )
            compiled_tasks.append(task)

        workflow_metadata = {
            "planner": {
                "plan_id": candidate_plan.plan_id,
                "intent": candidate_plan.intent,
                "target_model": candidate_plan.target_model,
                "compiled_at": datetime.now(timezone.utc).isoformat(),
                "compiler_version": "1.0.0",
                **(candidate_plan.metadata or {})
            }
        }

        return Workflow(
            workflow_id=candidate_plan.plan_id,
            version="1.0",
            tasks=compiled_tasks,
            status="pending",
            current_state=workflow_metadata
        )
