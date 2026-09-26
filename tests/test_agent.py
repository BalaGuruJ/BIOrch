import pytest
from pydantic import ValidationError
from biorch.core.agent import Agent

def test_agent_construction():
    """
    Test valid Agent construction.
    """
    agent = Agent(agent_id="a1", name="Bot", role="Analyst")
    assert agent.agent_id == "a1"
    assert agent.name == "Bot"

def test_agent_invalid_contract():
    """
    Test Agent rejects invalid contract (missing required field).
    """
    with pytest.raises(ValidationError):
        Agent(agent_id="a1") # Missing name, role

def test_agent_serialization():
    """
    Test Agent serialization/deserialization.
    """
    agent = Agent(agent_id="a1", name="Bot", role="Analyst", capabilities=["math"])
    assert Agent.model_validate_json(agent.model_dump_json()) == agent
