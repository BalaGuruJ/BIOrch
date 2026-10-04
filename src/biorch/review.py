from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Optional
from biorch.core.task import Task
from biorch.core.result import Result

@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "passed": self.passed,
            "message": self.message
        }

@dataclass
class ReviewResult:
    approved: bool
    rule_results: List[RuleResult]
    correction_feedback: Optional[str]
    reviewer_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "rule_results": [r.to_dict() for r in self.rule_results],
            "correction_feedback": self.correction_feedback,
            "reviewer_id": self.reviewer_id
        }

class Reviewer:
    """
    Deterministic Reviewer (Maker-Checker evaluation component).
    Evaluates Task and Result against deterministic rules.
    """
    def __init__(
        self,
        reviewer_id: str = "default_reviewer",
        rules: Optional[List[Callable[[Task, Result], RuleResult]]] = None,
        max_retries: int = 0
    ):
        self.reviewer_id = reviewer_id
        self.rules = rules or []
        self.max_retries = max_retries

    def add_rule(self, rule_fn: Callable[[Task, Result], RuleResult]):
        self.rules.append(rule_fn)

    def evaluate(self, task: Task, result: Result) -> ReviewResult:
        rule_results: List[RuleResult] = []
        for rule in self.rules:
            try:
                res = rule(task, result)
                if isinstance(res, RuleResult):
                    rule_results.append(res)
                elif isinstance(res, tuple) and len(res) == 3:
                    rule_results.append(RuleResult(rule_name=res[0], passed=bool(res[1]), message=str(res[2])))
                else:
                    passed = bool(res)
                    rule_results.append(RuleResult(rule_name="generic_rule", passed=passed, message="" if passed else "Rule failed"))
            except Exception as e:
                rule_results.append(RuleResult(rule_name="rule_exception", passed=False, message=str(e)))

        approved = all(r.passed for r in rule_results) if rule_results else True

        correction_feedback = None
        if not approved:
            failed_messages = [f"Rule '{r.rule_name}' failed: {r.message}" for r in rule_results if not r.passed]
            correction_feedback = "; ".join(failed_messages)

        return ReviewResult(
            approved=approved,
            rule_results=rule_results,
            correction_feedback=correction_feedback,
            reviewer_id=self.reviewer_id
        )
