from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Agent(BaseModel):
    """
    Agent Contract
    Represents an entity that performs a specialized responsibility.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent instance.")
    name: str = Field(..., description="Human-readable name of the agent.")
    role: str = Field(..., description="The specific responsibility or domain of the agent.")
    capabilities: List[str] = Field(default_factory=list, description="High-level descriptions of what this agent can do.")
    allowed_tools: List[str] = Field(default_factory=list, description="List of tool IDs this agent is permitted to request via the Tool Gateway.")
    supported_operations: Optional[List[str]] = Field(default=None, description="List of operations supported by this agent.")
    provider_info: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata about the underlying model or provider powering this agent.")
