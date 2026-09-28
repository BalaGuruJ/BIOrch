# BIOrch Deterministic Agent Contract

**Contract ID:** BIORCH-AGENT-001

**Contract Name:** Deterministic Agent Contract

**Phase:** Phase 03 — One Deterministic Agent

**Status:** DRAFT

**Depends On:** BIORCH-TG-001

**Canonical Tool Gateway Contract:**
`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

---

## 1. Purpose

This contract defines the minimum executable agent abstraction for BIOrch.

The purpose of Phase 03 is to establish one deterministic agent capable of executing a predefined task through the BIOrch Tool Gateway.

The agent MUST provide a controlled execution boundary between a structured task and the Tool Gateway.

The agent MUST NOT introduce orchestration, multi-agent coordination, autonomous planning, or LLM-based task planning.

Phase 03 establishes the foundation for later orchestration and multi-agent phases.

---

## 2. Architectural Principle

The deterministic agent MUST execute approved operations exclusively through the Tool Gateway.

The required execution path is:

    Structured Task
        ↓
    Deterministic Agent
        ↓
    Tool Gateway
        ↓
    Authorized Tool
        ↓
    ToolResult
        ↓
    AgentResult

The agent MUST NOT bypass the Tool Gateway to execute tools or access protected resources directly.

The Tool Gateway remains the authoritative security and execution boundary defined by `BIORCH-TG-001`.

---

## 3. Source of Truth

The canonical requirements for tool execution remain defined by:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

This contract defines the agent boundary and MUST NOT redefine or weaken Tool Gateway security requirements.

The agent implementation MUST use the existing Tool Gateway rather than implementing a parallel authorization or execution mechanism.

If this contract conflicts with the Tool Gateway contract, the Tool Gateway security requirements remain authoritative for tool execution.

---

## 4. Deterministic Agent Definition

A deterministic agent MUST have an explicit definition.

At minimum, an agent definition MUST identify:

- unique agent identifier;
- agent version;
- purpose;
- supported operations;
- explicitly permitted tools;
- input schema;
- output schema;
- execution policy.

The agent MUST NOT dynamically discover arbitrary tools.

The agent MUST NOT invoke tools outside its explicitly permitted tool set.

---

## 5. Structured Task

The agent MUST accept a structured task representation.

A task MUST contain sufficient information to deterministically identify:

- task identifier;
- target agent;
- agent version where required;
- requested operation;
- operation inputs;
- execution context where required;
- applicable execution constraints.

The implementation MAY use an existing task model if one already exists in the repository.

The implementation MUST NOT introduce a second incompatible task abstraction when an existing canonical model is suitable.

Raw natural-language user requests are outside the Phase 03 contract.

Natural-language interpretation and LLM-based planning belong to later phases.

---

## 6. Task Validation

Before execution, the agent MUST validate the received task.

Validation MUST determine at minimum:

- whether the task is structurally valid;
- whether the requested agent exists;
- whether the requested agent version is supported;
- whether the requested operation is supported;
- whether required inputs are present;
- whether inputs satisfy the agent's declared constraints;
- whether the requested operation is permitted for the agent.

Invalid tasks MUST be rejected before tool execution.

The agent MUST NOT silently modify an invalid task to make it executable.

---

## 7. Deterministic Operation Selection

For Phase 03, operation selection MUST be deterministic.

Given the same:

- agent definition;
- operation;
- valid inputs;
- execution configuration;

the agent MUST select the same execution path.

The agent MUST NOT use probabilistic or LLM-based planning to determine the execution path.

The agent MUST NOT dynamically generate arbitrary workflows.

The agent MUST NOT dynamically discover additional tools during execution.

---

## 8. Tool Authorization Boundary

The agent MUST maintain an explicit relationship between supported agent operations and permitted tools.

An agent operation MAY invoke one or more explicitly permitted tools only when that relationship is defined by the agent configuration.

The agent MUST NOT:

- invoke an unregistered tool;
- invoke a tool outside its permitted tool set;
- bypass the Tool Gateway;
- directly call an underlying tool callable;
- directly execute operating-system commands;
- directly access protected resources.

Tool-level authorization remains the responsibility of the Tool Gateway.

---

## 9. Tool Gateway Integration

All tool execution MUST pass through the Tool Gateway defined by:

`BIORCH-TG-001`

The agent MUST submit a valid gateway invocation containing the information required by the Tool Gateway contract.

The agent MUST accept the Tool Gateway's authorization decision.

If the Tool Gateway rejects an invocation, the agent MUST NOT bypass the rejection by:

- changing the resource to an unauthorized resource;
- changing the operation to an unauthorized operation;
- selecting an unapproved tool;
- directly invoking the underlying implementation;
- executing an equivalent operation outside the gateway.

A gateway rejection MUST result in a structured agent failure or rejection.

---

## 10. Execution Boundary

The deterministic agent MUST NOT expose unrestricted execution capabilities.

The agent MUST NOT directly expose or invoke:

- shell execution;
- arbitrary subprocess execution;
- arbitrary Python execution;
- unrestricted filesystem access;
- unrestricted network access;
- unrestricted operating-system operations;
- arbitrary code execution.

Any such capability required by a future agent MUST be exposed as an explicitly registered and authorized Tool Gateway tool.

---

## 11. Agent Result

The agent MUST return a structured result.

The result MUST communicate, where applicable:

- execution status;
- task identifier;
- agent identifier;
- agent version;
- operation;
- output payload;
- structured error information;
- tool execution information;
- provenance.

The agent MUST NOT report successful completion when the underlying Tool Gateway operation or tool execution failed.

---

## 12. Result Status

The implementation MUST distinguish at least the following terminal outcomes:

### SUCCESS

The requested operation completed successfully.

### REJECTED

The requested operation was not permitted or the task failed validation/authorization before successful execution.

### FAILED

The task was valid and execution was attempted, but execution failed.

The exact internal error taxonomy MAY reuse existing repository models where appropriate.

---

## 13. Failure Behavior

The deterministic agent MUST fail closed.

The agent MUST reject execution when required conditions cannot be deterministically satisfied.

Examples include:

- invalid task;
- unknown agent;
- unsupported agent version;
- unsupported operation;
- invalid input;
- unauthorized tool;
- Tool Gateway rejection;
- Tool execution failure;
- invalid execution context;
- internal execution failure.

The agent MUST NOT weaken a security restriction to obtain successful execution.

---

## 14. Retry Behavior

Phase 03 MUST NOT introduce autonomous retry logic that changes the requested operation, resource, authorization scope, or tool selection.

If retry behavior is required by an existing lower-level contract, the agent MUST preserve the security and authorization boundaries of the original request.

No retry mechanism may be used to bypass a Tool Gateway rejection.

Complex retry policies belong to later orchestration/runtime design unless explicitly added to a future contract.

---

## 15. Provenance

The agent MUST preserve sufficient provenance to establish:

- agent identifier;
- agent version;
- task identifier;
- requested operation;
- tool identifier where a tool was invoked;
- tool version where available;
- execution occurrence/time;
- execution status.

Where the Tool Gateway already provides provenance, the agent SHOULD propagate the gateway provenance rather than creating a conflicting provenance model.

Provenance MUST NOT expose:

- credentials;
- secrets;
- authentication tokens;
- unnecessary sensitive input data.

Durable audit-storage architecture is outside Phase 03 unless already provided by the existing repository.

---

## 16. Error Handling

Agent failures MUST be structured and deterministic.

At minimum, the agent MUST distinguish between:

- invalid task;
- unsupported operation;
- unauthorized tool;
- gateway rejection;
- tool execution failure;
- internal agent failure.

Errors MUST NOT expose secrets or unnecessary sensitive implementation details.

The agent MUST preserve the distinction between:

1. task validation failure;
2. authorization/rejection;
3. execution failure.

---

## 17. Security Separation

Security responsibilities MUST remain separated between the agent and Tool Gateway.

### Agent responsibilities

The agent is responsible for:

- task validation;
- operation validation;
- agent-level tool allowlisting;
- deterministic execution selection;
- structured result construction;
- propagation of gateway results.

### Tool Gateway responsibilities

The Tool Gateway remains responsible for:

- tool registration;
- tool version validation;
- tool-level authorization;
- resource authorization;
- operation authorization;
- resource/path security;
- execution boundary enforcement;
- tool execution;
- gateway-level validation;
- gateway-level failure handling.

The agent MUST NOT duplicate or weaken these gateway security controls.

---

## 18. No LLM Planning

LLM-based planning is explicitly outside Phase 03.

The Phase 03 implementation MUST NOT require an LLM to:

- select the execution strategy;
- dynamically select arbitrary tools;
- generate execution plans;
- decompose tasks;
- modify execution policies;
- determine authorization.

Future LLM-based planning belongs to a later phase.

---

## 19. No Orchestration

The deterministic agent MUST NOT implement orchestration.

The agent MUST NOT manage:

- multiple agents;
- agent-to-agent communication;
- agent scheduling;
- parallel agent execution;
- workflow-wide coordination;
- dynamic agent delegation;
- global workflow state.

These capabilities belong to later phases, particularly:

**Phase 04 — Deterministic Orchestrator**

---

## 20. No Multi-Agent Capability

Phase 03 MUST contain exactly one executable agent capability.

The implementation MUST NOT introduce:

- agent registries for multi-agent coordination;
- agent delegation;
- agent-to-agent messaging;
- agent pools;
- agent scheduling;
- multi-agent workflows.

Multiple specialized agents belong to Phase 05.

---

## 21. BI Capability Boundary

Phase 03 MUST NOT implement Tableau or Power BI parsing.

The following remain outside Phase 03:

- Tableau workbook parsing;
- Tableau metadata extraction;
- Power BI semantic-model parsing;
- Power BI report parsing;
- lineage analysis;
- Tableau/Power BI comparison;
- BI-specific agent capabilities.

Future BI capabilities MUST be exposed through the Tool Gateway and agent architecture defined by their respective future phases.

---

## 22. Framework Independence

Phase 03 MUST remain framework-independent unless an existing repository decision explicitly requires otherwise.

The implementation MUST NOT introduce CrewAI, LangChain, AutoGen, or another agent framework merely to satisfy this contract.

Framework evaluation or adoption is outside the mandatory scope of this contract.

The deterministic agent abstraction MUST remain usable independently of a third-party orchestration framework.

---

## 23. Deterministic Execution Model

For a valid task, the agent execution path MUST be deterministic with respect to:

- agent definition;
- agent version;
- operation;
- validated inputs;
- permitted tools;
- execution policy.

The same logical inputs and configuration MUST result in the same agent-level control flow.

External tool results MAY vary when the underlying resource or environment changes.

Determinism therefore applies primarily to agent decision/control flow rather than requiring identical external-world output.

---

## 24. Minimum Phase 03 Vertical Slice

Phase 03 MUST demonstrate at least one complete deterministic execution path:

    Structured Task
        ↓
    Agent Validation
        ↓
    Deterministic Operation Selection
        ↓
    Tool Gateway Invocation
        ↓
    Tool Authorization
        ↓
    Tool Execution
        ↓
    ToolResult
        ↓
    AgentResult

The implementation MUST also demonstrate at least one rejected execution path.

The rejected path MUST demonstrate that the agent cannot bypass the Tool Gateway.

The demonstration capability SHOULD be a small repository-safe operation rather than a Tableau or Power BI parser.

---

## 25. Testing Requirements

The implementation MUST include tests covering at minimum:

### Valid execution

A valid task reaches the permitted Tool Gateway operation and produces a successful AgentResult.

### Invalid task

An invalid task is rejected before unauthorized execution occurs.

### Unsupported operation

An unsupported operation is rejected.

### Unauthorized tool

An agent cannot invoke a tool outside its permitted tool set.

### Gateway rejection

A Tool Gateway rejection is propagated as a structured agent rejection/failure.

### Tool failure

A tool execution failure is represented as an unsuccessful AgentResult.

### No gateway bypass

Tests demonstrate that the agent cannot directly invoke the underlying tool implementation when the gateway rejects the request.

### Deterministic control flow

Equivalent valid inputs produce the same agent-level execution path.

---

## 26. Scope Restrictions

Phase 03 MUST NOT modify or redefine:

- the Tool Gateway security contract;
- future orchestrator contracts;
- future multi-agent contracts;
- Tableau parser contracts;
- Power BI parser contracts;
- LLM planning architecture;
- parallel orchestration architecture.

Only the minimum changes required to establish the deterministic-agent capability are permitted.

---

## 27. Required Architectural Separation

The resulting architecture MUST preserve the following dependency direction:

    Task
      ↓
    Deterministic Agent
      ↓
    Tool Gateway
      ↓
    Registered Tool

The following dependency direction is prohibited:

    Task
      ↓
    Agent
      ↓
    Direct OS / filesystem / subprocess / arbitrary execution

The following is also prohibited in Phase 03:

    Agent
      ↔
    Agent

and:

    Agent
      ↓
    Orchestrator

The orchestrator does not exist as a Phase 03 runtime dependency.

---

## 28. Phase 03 Completion Criteria

Phase 03 may be considered technically complete only when all of the following are true:

1. A canonical deterministic-agent implementation exists.
2. The implementation conforms to this contract.
3. One deterministic agent can execute one predefined operation.
4. Execution occurs exclusively through the Tool Gateway.
5. Invalid tasks are rejected.
6. Unauthorized tools are rejected.
7. Tool Gateway rejection cannot be bypassed.
8. Tool failures are represented correctly.
9. Structured AgentResult output exists.
10. Agent and tool provenance are preserved.
11. Tests cover successful and rejected execution.
12. No arbitrary execution capability has been introduced.
13. No LLM planning has been introduced.
14. No orchestration capability has been introduced.
15. No multi-agent capability has been introduced.
16. No Tableau or Power BI parsing has been introduced.
17. The implementation remains compatible with the existing Phase 02 Tool Gateway architecture.
18. The implementation has been reviewed against this contract.

---

## 29. Explicit Non-Goals

The following are explicitly NOT Phase 03 goals:

- LLM agent planning;
- autonomous agents;
- multiple agents;
- agent orchestration;
- parallel execution;
- agent-to-agent communication;
- dynamic workflow generation;
- dynamic tool discovery;
- Tableau parsing;
- Power BI parsing;
- BI comparison;
- report generation;
- production deployment architecture;
- external agent frameworks;
- durable distributed execution;
- complex retry orchestration.

These capabilities may be introduced through later governed phases.

---

## 30. Relationship to Future Phases

Phase 03 establishes:

**One deterministic agent.**

Phase 04 will establish:

**Deterministic orchestration of known workflows.**

Phase 05 will establish:

**Multiple specialized agents.**

Later phases may establish:

- parallel orchestration;
- review loops;
- LLM-based planning;
- Tableau integration;
- Power BI integration;
- BI comparison;
- analysis-ready outputs.

Phase 03 MUST therefore remain intentionally narrow.

---

## 31. Contract Decision

This contract defines the architectural boundary for:

**Phase 03 — One Deterministic Agent**

The implementation task MUST be derived from this contract.

The implementation task MUST NOT expand the Phase 03 scope beyond the requirements and boundaries defined here without explicit contract revision and approval.

**Contract Status:** DRAFT

**Approval Required:** Yes