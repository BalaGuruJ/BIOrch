from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .models import CandidatePlan, CandidateTask

class PlanGenerationError(Exception):
    """Raised when plan generation fails or returns invalid outputs."""
    pass

class ProviderError(Exception):
    """Raised when the LLM provider encounters an error."""
    pass

class LLMProvider(ABC):
    """
    Abstract interface for LLM providers generating candidate plans.
    """
    @abstractmethod
    def generate_plan(self, intent: str, context: Optional[Dict[str, Any]] = None) -> CandidatePlan:
        """Generate a CandidatePlan from a natural language intent."""
        pass

class MockLLMProvider(LLMProvider):
    """
    Deterministic mock LLM provider for testing and evaluation without live API calls.
    """
    def __init__(self, predefined_plans: Optional[Dict[str, CandidatePlan]] = None, default_plan: Optional[CandidatePlan] = None):
        self.predefined_plans = predefined_plans or {}
        self.default_plan = default_plan

    def generate_plan(self, intent: str, context: Optional[Dict[str, Any]] = None) -> CandidatePlan:
        if intent in self.predefined_plans:
            return self.predefined_plans[intent]
        if self.default_plan:
            plan = self.default_plan.copy(deep=True)
            plan.intent = intent
            return plan
        
        # Default fallback mock plan generation based on intent keywords
        if "tableau" in intent.lower() and "power bi" in intent.lower():
            return CandidatePlan(
                plan_id="mock-plan-cross-bi",
                intent=intent,
                target_model="mock-gemini-pro",
                tasks=[
                    CandidateTask(
                        task_id="task_tableau_inspect",
                        objective="Inspect Tableau workbook and extract relationships and schema metadata.",
                        agent_id="tableau_agent",
                        operation="inspect_workbook",
                        inputs={"workbook_path": "examples/artifacts/tableau/sample.twbx"},
                        dependencies=[],
                        rationale="Extract source Tableau metadata first."
                    ),
                    CandidateTask(
                        task_id="task_pbi_inspect",
                        objective="Inspect Power BI semantic model relationships and lineage.",
                        agent_id="powerbi_agent",
                        operation="inspect_model",
                        inputs={"model_path": "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"},
                        dependencies=["task_tableau_inspect"],
                        rationale="Extract Power BI model metadata after Tableau."
                    )
                ],
                metadata={"provider": "MockLLMProvider"}
            )
        
        # Generic single task mock plan
        return CandidatePlan(
            plan_id="mock-plan-generic",
            intent=intent,
            target_model="mock-gemini-pro",
            tasks=[
                CandidateTask(
                    task_id="task_default_1",
                    objective=f"Execute task fulfilling intent: {intent}",
                    agent_id="repository_agent",
                    operation="default_operation",
                    inputs={},
                    dependencies=[],
                    rationale="Default generated task for generic intent."
                )
            ],
            metadata={"provider": "MockLLMProvider"}
        )
