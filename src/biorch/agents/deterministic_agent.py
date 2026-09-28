from typing import Dict, Any, List
from biorch.core.agent import Agent
from biorch.core.task import Task, TaskStatus
from biorch.core.result import Result, ResultStatus
from biorch.core.gateway import ToolGateway

class DeterministicAgentExecutor:
    def __init__(self, gateway: ToolGateway, agent_definition: Agent):
        self.gateway = gateway
        self.agent_definition = agent_definition

    def execute(self, task: Task) -> Result:
        # 1. Validation
        if task.agent_id != self.agent_definition.agent_id:
            return self._create_failure_result(task.task_id, ["Unauthorized agent"])
            
        if not task.inputs or "operation" not in task.inputs or "tool_id" not in task.inputs:
            return self._create_failure_result(task.task_id, ["Missing required inputs"])
            
        tool_id = task.inputs["tool_id"]
        operation = task.inputs["operation"]
        
        if tool_id not in self.agent_definition.allowed_tools:
            return self._create_failure_result(task.task_id, [f"Unauthorized tool: {tool_id}"])

        # 2. Execution via Gateway
        tool_result = self.gateway.invoke(
            tool_id=tool_id,
            version=task.inputs.get("version", "1.0"),
            resource=task.inputs.get("resource", ""),
            operation=operation,
            inputs=task.inputs.get("tool_inputs", {})
        )
        
        # 3. Structured Result
        if tool_result.status == "success":
            return Result(
                task_id=task.task_id,
                status=ResultStatus.SUCCESS,
                findings=[tool_result.data or {}],
                metadata={"provenance": tool_result.provenance}
            )
        else:
            return Result(
                task_id=task.task_id,
                status=ResultStatus.FAILURE,
                errors=tool_result.errors or ["Tool execution failed"]
            )
            
    def _create_failure_result(self, task_id: str, errors: List[str]) -> Result:
        return Result(
            task_id=task_id,
            status=ResultStatus.FAILURE,
            errors=errors
        )
