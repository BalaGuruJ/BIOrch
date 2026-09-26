import pytest
from pydantic import ValidationError
from biorch.core.tool import Tool

def test_tool_construction():
    """
    Test valid Tool construction.
    """
    tool = Tool(tool_id="math_tool", name="Math", description="Adds numbers", input_schema={}, permission_category="read", security_classification="safe")
    assert tool.tool_id == "math_tool"

def test_tool_invalid_contract():
    """
    Test Tool rejects invalid contract.
    """
    with pytest.raises(ValidationError):
        Tool(tool_id="t1") # Missing other required fields

def test_tool_serialization():
    """
    Test Tool serialization/deserialization.
    """
    tool = Tool(tool_id="math_tool", name="Math", description="Adds", input_schema={}, permission_category="read", security_classification="safe")
    assert Tool.model_validate_json(tool.model_dump_json()) == tool
