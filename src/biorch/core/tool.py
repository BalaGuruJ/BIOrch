from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class Tool(BaseModel):
    """
    Tool Contract
    Represents a capability that an agent may request.
    """
    tool_id: str = Field(..., description="Unique identifier for the tool.")
    name: str = Field(..., description="Human-readable name of the tool.")
    description: str = Field(..., description="Detailed description of what the tool does.")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema defining the expected inputs for this tool.")
    permission_category: str = Field(..., description="High-level categorization of the tool's impact (e.g., read_only, write, network).")
    security_classification: str = Field(..., description="Security policy (e.g., safe, requires_approval, restricted).")
