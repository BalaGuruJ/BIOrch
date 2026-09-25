# Framework Evaluation Criteria

**IMPORTANT: No framework is selected during Phase 1.**

The BIOrch architecture must remain independent of any specific framework choice. The underlying framework will be selected in a later phase based on how well it maps to our framework-neutral contracts (Agent, Task, Result, Tool, Workflow).

## Evaluation Criteria

Any potential orchestration framework must be evaluated against the following requirements:

- **Deterministic Workflows:** Support for rigid, hardcoded sequential pipelines before autonomous execution.
- **Manager/Worker Orchestration:** Ability to support a central orchestrator managing specialized worker agents.
- **Parallel Execution:** Support for executing independent tasks concurrently.
- **Evaluator/Reviewer Loops:** Support for Maker/Checker patterns with defined retry limits (max iterations).
- **Structured Outputs:** Ability to strictly adhere to defined JSON schemas for communication (Task/Result contracts).
- **Typed Tools:** Strong support for validating tool schemas and isolating tool execution.
- **Workflow State:** Transparent management of dependencies, intermediate results, and current execution state.
- **Retries and Error Handling:** Graceful recovery from tool failures or schema validation errors.
- **Human Approval:** Built-in or easily extensible mechanisms for human-in-the-loop approvals (e.g., for Tool Gateway).
- **Provider Independence:** Agnostic to the underlying LLM provider.
- **Gemini & Claude Compatibility:** Out-of-the-box or easily implementable support for Google Gemini and Anthropic Claude.
- **Local/Open-source Model Compatibility:** Ability to route to local models or alternative APIs.
- **Observability:** Clear audit logging and tracing of tasks, tool calls, and state changes.
- **Security/Tool Isolation:** Allows implementing our Tool Gateway pattern without bypassing it.
- **TabUI & PBIParser Integration:** Easily integratable with external Python processes or libraries without forcing them into an incompatible paradigm.

## Potential Candidates

When the time comes to select a framework, candidates may include:

- **CrewAI:** Evaluated for its strong Manager/Worker mental model and task assignment flow.
- **LangGraph:** Evaluated for its precise control over state machines, graphs, and conditional routing.
- **Microsoft Agent Framework / AutoGen:** Evaluated for its official orchestration patterns, especially regarding Maker/Checker loops and multi-agent coordination.
- *Other relevant open-source frameworks.*
