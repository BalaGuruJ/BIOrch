from typing import Dict
from biorch.agents.deterministic_agent import DeterministicAgentExecutor

class AgentNotFoundError(Exception):
    """Raised when the requested agent_id is not found in the AgentResolver mapping."""
    pass

class AgentResolver:
    """
    A read-only, deterministic mapping of agent_ids to DeterministicAgentExecutor instances.
    """
    def __init__(self, agent_map: Dict[str, DeterministicAgentExecutor]):
        # Store as an immutable dictionary
        self._agent_map = dict(agent_map)

    def resolve(self, agent_id: str) -> DeterministicAgentExecutor:
        """
        Resolves a known agent_id to its executor.
        Raises AgentNotFoundError if unknown.
        """
        if agent_id not in self._agent_map:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in AgentResolver.")
        return self._agent_map[agent_id]
