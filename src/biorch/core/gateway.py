from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, List, Optional
from enum import Enum
import datetime

class ToolStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class ToolDefinition(BaseModel):
    tool_id: str = Field(..., description="Unique identifier for the tool.")
    name: str = Field(..., description="Human-readable name.")
    purpose: str = Field(..., description="Purpose of the tool.")
    version: str = Field(..., description="Version of the tool.")
    input_schema: Dict[str, Any] = Field(..., description="Pydantic model or dict schema for input validation.")
    output_schema: Dict[str, Any] = Field(..., description="Schema for output validation.")
    allowed_resources: List[str] = Field(default_factory=list, description="List of authorized resource roots.")
    permitted_operations: List[str] = Field(default_factory=list, description="List of permitted operations (e.g., READ, WRITE).")
    security_classification: str = Field(..., description="Security level.")

class ToolResult(BaseModel):
    status: ToolStatus
    tool_id: str
    tool_version: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    provenance: Dict[str, Any]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        if tool.tool_id in self._tools:
            raise ValueError(f"Tool {tool.tool_id} already registered.")
        self._tools[tool.tool_id] = tool

    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_id)

class ToolGateway:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def invoke(self, tool_id: str, version: str, resource: str, operation: str, inputs: Dict[str, Any]) -> ToolResult:
        tool = self.registry.get_tool(tool_id)
        
        # 1. Deterministic validation: Fail closed
        if not tool:
            return self._create_error_result(tool_id, version, ["Unknown tool"])
            
        if tool.version != version:
            return self._create_error_result(tool_id, version, ["Incorrect tool version"])
            
        if operation not in tool.permitted_operations:
            return self._create_error_result(tool_id, version, [f"Unauthorized operation: {operation}"])
            
        # 2. Resource authorization (simple root check for now as per contract)
        if not any(resource.startswith(r) for r in tool.allowed_resources):
            return self._create_error_result(tool_id, version, [f"Unauthorized resource: {resource}"])
            
        # 3. Input validation
        try:
            # Basic schema validation (in a real system, we'd use proper JSON schema validation)
            # Here we just assume inputs must match the keys in the input_schema for simplicity
            for key in inputs:
                if key not in tool.input_schema:
                    raise ValueError(f"Invalid input: {key}")
        except Exception as e:
            return self._create_error_result(tool_id, version, [str(e)])

        # 4. Execution
        return ToolResult(
            status=ToolStatus.SUCCESS,
            tool_id=tool_id,
            tool_version=version,
            data={"result": "Execution successful"},
            provenance={"timestamp": datetime.datetime.now().isoformat()}
        )

    def _create_error_result(self, tool_id: str, version: str, errors: List[str]) -> ToolResult:
        return ToolResult(
            status=ToolStatus.FAILURE,
            tool_id=tool_id,
            tool_version=version,
            errors=errors,
            provenance={"timestamp": datetime.datetime.now().isoformat()}
        )
