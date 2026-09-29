import pytest
from biorch.orchestration.agent_resolver import AgentResolver, AgentNotFoundError
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from unittest.mock import MagicMock

@pytest.fixture
def mock_executor():
    return MagicMock(spec=DeterministicAgentExecutor)

def test_resolver_successful_lookup(mock_executor):
    resolver = AgentResolver({"agent1": mock_executor})
    assert resolver.resolve("agent1") == mock_executor

def test_resolver_unknown_agent_raises_error(mock_executor):
    resolver = AgentResolver({"agent1": mock_executor})
    with pytest.raises(AgentNotFoundError):
        resolver.resolve("unknown_agent")

def test_resolver_determinism(mock_executor):
    resolver = AgentResolver({"agent1": mock_executor})
    assert resolver.resolve("agent1") is resolver.resolve("agent1")

def test_resolver_multiple_agents(mock_executor):
    executor2 = MagicMock(spec=DeterministicAgentExecutor)
    resolver = AgentResolver({"agent1": mock_executor, "agent2": executor2})
    assert resolver.resolve("agent1") == mock_executor
    assert resolver.resolve("agent2") == executor2
