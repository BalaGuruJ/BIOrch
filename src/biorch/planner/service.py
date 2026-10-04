from typing import List, Dict, Any, Optional, Tuple
from biorch.core.workflow import Workflow
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from .models import CandidatePlan
from .provider import LLMProvider
from .compiler import PlanCompiler, PlanCompilerError

class LLMPlannerService:
    """
    High-level coordination service for LLM-based planning, compilation, and validation.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def plan(self, intent: str, context: Optional[Dict[str, Any]] = None) -> CandidatePlan:
        """Generate a candidate plan from intent using the configured LLM provider."""
        return self.provider.generate_plan(intent, context)

    def compile(self, candidate_plan: CandidatePlan) -> Workflow:
        """Compile a candidate plan into a canonical workflow."""
        return PlanCompiler.compile(candidate_plan)

    def plan_and_compile(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Workflow:
        """Generate a candidate plan and compile it into a workflow in one step."""
        c_plan = self.plan(intent, context)
        return self.compile(c_plan)

    def validate(self, workflow: Workflow, orchestrator: DeterministicOrchestrator) -> List[str]:
        """Validate the compiled workflow using the DeterministicOrchestrator validation rules."""
        return orchestrator.validate_workflow(workflow)

    def plan_compile_validate(
        self,
        intent: str,
        orchestrator: DeterministicOrchestrator,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Workflow, List[str]]:
        """Plan, compile, and validate a workflow against an orchestrator."""
        workflow = self.plan_and_compile(intent, context)
        errors = self.validate(workflow, orchestrator)
        return workflow, errors
