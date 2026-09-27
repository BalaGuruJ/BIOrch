import pytest
from biorch.core.gateway import ToolDefinition, ToolRegistry, ToolGateway, ToolStatus

@pytest.fixture
def registry():
    reg = ToolRegistry()
    tool = ToolDefinition(
        tool_id="test_tool",
        name="Test Tool",
        purpose="Testing",
        version="1.0",
        input_schema={"input_key": "str"},
        output_schema={"result": "str"},
        allowed_resources=["/workspace/"],
        permitted_operations=["READ"],
        security_classification="safe"
    )
    reg.register(tool)
    return reg

@pytest.fixture
def gateway(registry):
    return ToolGateway(registry)

def test_registration():
    reg = ToolRegistry()
    tool = ToolDefinition(tool_id="t1", name="N", purpose="P", version="1", input_schema={}, output_schema={}, allowed_resources=[], permitted_operations=[], security_classification="s")
    reg.register(tool)
    assert reg.get_tool("t1") == tool
    with pytest.raises(ValueError):
        reg.register(tool)

def test_valid_invocation(gateway):
    result = gateway.invoke("test_tool", "1.0", "/workspace/file.txt", "READ", {"input_key": "data"})
    assert result.status == ToolStatus.SUCCESS

def test_unknown_tool_rejection(gateway):
    result = gateway.invoke("unknown", "1.0", "/workspace/", "READ", {})
    assert result.status == ToolStatus.FAILURE
    assert "Unknown tool" in result.errors

def test_invalid_version_rejection(gateway):
    result = gateway.invoke("test_tool", "2.0", "/workspace/", "READ", {})
    assert result.status == ToolStatus.FAILURE
    assert "Incorrect tool version" in result.errors

def test_unauthorized_operation_rejection(gateway):
    result = gateway.invoke("test_tool", "1.0", "/workspace/", "WRITE", {})
    assert result.status == ToolStatus.FAILURE
    assert "Unauthorized operation" in result.errors[0]

def test_unauthorized_resource_rejection(gateway):
    result = gateway.invoke("test_tool", "1.0", "/etc/passwd", "READ", {})
    assert result.status == ToolStatus.FAILURE
    assert "Unauthorized resource" in result.errors[0]

def test_input_validation(gateway):
    # Missing input_key in schema
    result = gateway.invoke("test_tool", "1.0", "/workspace/", "READ", {"wrong_key": "data"})
    assert result.status == ToolStatus.FAILURE
