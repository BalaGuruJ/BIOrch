# TASK: Phase 03 — One Deterministic Agent

**Task ID:** PHASE-03-IMPLEMENTATION

**Phase:** 03 — One Deterministic Agent

**Status:** DRAFT

**Contract:** BIORCH-AGENT-001

**Canonical Contract:**
`contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`

**Required Dependency:**
BIORCH-TG-001 — Tool Gateway

**Tool Gateway Contract:**
`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

---

## 1. Objective

Implement the first BIOrch deterministic agent defined by the canonical
`BIORCH-AGENT-001` contract.

The agent MUST provide a deterministic execution boundary between an incoming
agent task and the existing BIOrch Tool Gateway.

The implementation MUST satisfy the mandatory requirements of:

`contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`

The agent MUST use the existing:

`BIORCH-TG-001`

Tool Gateway for all tool execution.

The implementation MUST remain framework-independent and MUST NOT introduce
LLM-based planning, orchestration, multi-agent behavior, or BI-parser
integration.

---

## 2. Source of Truth

The canonical source of requirements for this implementation is:

`contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`

The existing Tool Gateway contract is also authoritative for the gateway
boundary:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

The implementation MUST NOT:

- redefine the agent contract;
- weaken mandatory contract requirements;
- silently reinterpret mandatory requirements;
- bypass the Tool Gateway;
- modify the canonical contracts as part of this task.

If an implementation detail is not explicitly defined by the contract,
inspect the existing repository architecture and select the smallest
implementation consistent with the current project.

Any ambiguity or contract gap MUST be documented rather than resolved by
silently changing the contract.

---

## 3. Prerequisites

Before implementation:

1. Phase 02 Tool Gateway implementation must be present and usable.
2. `BIORCH-TG-001` must remain the only execution path for tools.
3. Existing agent, task, result, gateway, tool, workflow, security, and
   validation abstractions MUST be inspected.
4. Existing tests and test conventions MUST be inspected.
5. Existing package/module architecture MUST be inspected.

The implementation MUST build on existing abstractions where appropriate
rather than unnecessarily introducing duplicate models or infrastructure.

---

## 4. Repository Inspection Before Implementation

Before modifying source code, inspect the repository to determine:

- existing Agent abstractions;
- existing Task models;
- existing Result models;
- existing Tool models;
- existing Tool Gateway interfaces;
- existing validation utilities;
- existing security boundaries;
- existing workflow/orchestration abstractions;
- existing error-handling patterns;
- existing test structure;
- existing package/module conventions.

At minimum, inspect the relevant implementation under:

`src/biorch/`

and the relevant tests under:

`tests/`

Do NOT assume that a new implementation belongs in a particular file or
module until the existing architecture has been inspected.

The implementation MUST reuse compatible existing abstractions where doing so
does not violate the canonical contract.

Document the selected implementation modules in the final response.

---

## 5. Scope

This phase is limited to implementing ONE deterministic agent.

The implementation MUST include the minimum runtime behavior necessary to
satisfy `BIORCH-AGENT-001`.

The agent MUST:

1. Accept a defined agent task/request.
2. Validate the task according to the canonical contract.
3. Determine the permitted operation deterministically.
4. Resolve the requested tool through the Tool Gateway boundary.
5. Invoke the tool ONLY through `BIORCH-TG-001`.
6. Propagate Tool Gateway rejection/failure correctly.
7. Return a structured AgentResult as defined by the contract.
8. Remain deterministic and framework-independent.

---

## 6. Deterministic Task Validation

The agent MUST validate incoming tasks before attempting execution.

Validation MUST be based on explicit contract-defined information and MUST
NOT depend on LLM reasoning.

Where required by the canonical contract, validation MUST cover:

- task structure;
- required task fields;
- task identity;
- requested tool;
- requested tool version;
- requested operation;
- supplied inputs;
- required execution context;
- supported operation;
- authorization requirements;
- any other mandatory contract constraints.

Malformed or incomplete tasks MUST be rejected deterministically.

The agent MUST NOT silently modify an invalid task into a valid task.

The agent MUST NOT infer missing security-sensitive values merely to make
execution succeed.

---

## 7. Deterministic Operation Selection

Operation selection MUST be deterministic.

The agent MUST NOT:

- dynamically invent operations;
- ask an LLM to choose an operation;
- perform autonomous planning;
- select tools based on natural-language reasoning;
- retry using a different tool or operation without an explicit contract-defined
  deterministic rule.

The selected operation MUST be derived from the validated task and the
contract-defined rules.

If the requested operation is unsupported or unauthorized, the agent MUST
reject the task.

---

## 8. Tool Gateway Boundary

All tool execution MUST pass through:

`BIORCH-TG-001`

The agent MUST NOT directly execute registered tool callables.

The agent MUST NOT bypass:

- Tool registration;
- Tool version validation;
- input validation;
- resource authorization;
- operation authorization;
- other Tool Gateway security controls.

The following execution patterns are explicitly prohibited:

- direct invocation of tool implementation functions;
- direct filesystem execution outside the gateway;
- direct shell execution;
- direct subprocess execution;
- arbitrary Python execution;
- arbitrary operating-system command execution;
- equivalent execution paths that bypass the Tool Gateway.

The Tool Gateway remains the authoritative execution/security boundary.

---

## 9. Tool Gateway Rejection Handling

If `BIORCH-TG-001` rejects an invocation, the agent MUST NOT attempt to
circumvent the rejection.

Gateway rejection MUST be represented in the AgentResult according to the
canonical agent contract.

The agent MUST preserve the distinction between:

- invalid/rejected task;
- authorization rejection;
- Tool Gateway rejection;
- underlying tool execution failure;
- successful execution;
- unexpected internal agent failure.

The agent MUST NOT report successful agent execution when the Tool Gateway
reports failure.

---

## 10. Structured AgentResult

The implementation MUST provide the structured result behavior required by
`BIORCH-AGENT-001`.

At minimum, the result behavior MUST correctly represent the contract-defined
success, rejection, and failure outcomes.

Where required by the contract, results SHOULD preserve:

- agent identity;
- agent version;
- task identity;
- tool identity;
- tool version;
- execution outcome;
- result payload;
- structured error information;
- provenance information.

The exact result schema MUST follow the canonical contract and existing
repository models.

Do not create a competing result model if an existing compatible model already
exists.

---

## 11. Error Handling

Agent errors MUST be deterministic and structured according to the canonical
contract.

The implementation MUST correctly distinguish applicable categories such as:

- invalid task;
- validation failure;
- unauthorized operation;
- unauthorized tool;
- Tool Gateway rejection;
- tool execution failure;
- timeout/failure propagated from the gateway;
- internal agent failure.

Errors MUST NOT expose:

- credentials;
- API keys;
- secrets;
- unnecessary sensitive implementation details.

The agent MUST fail closed when required validation or authorization cannot be
satisfied.

---

## 12. Determinism Requirements

The Phase 03 agent MUST be deterministic.

For identical valid task inputs and identical relevant execution conditions,
the agent MUST follow the same execution path.

The implementation MUST NOT introduce:

- LLM calls;
- probabilistic planning;
- autonomous task decomposition;
- dynamic workflow generation;
- autonomous retries;
- dynamic tool discovery;
- multi-agent delegation.

Any behavior not explicitly required by the contract is outside this phase.

---

## 13. Testing Requirements

Implement tests sufficient to demonstrate compliance with the canonical
contract.

At minimum, tests MUST cover:

### 13.1 Successful Execution

Demonstrate that:

- a valid task is accepted;
- the correct operation is selected;
- the Tool Gateway is invoked;
- the resulting AgentResult represents success.

### 13.2 Invalid Task

Demonstrate deterministic rejection of malformed or invalid tasks.

### 13.3 Unsupported Operation

Demonstrate rejection when the requested operation is not supported.

### 13.4 Unauthorized Tool / Operation

Demonstrate that unauthorized execution is rejected.

### 13.5 Tool Gateway Rejection

Demonstrate that a Tool Gateway rejection is correctly propagated into the
agent result.

### 13.6 Tool Gateway Failure

Demonstrate that an execution failure from the gateway/tool does not produce
a false successful AgentResult.

### 13.7 No Gateway Bypass

Demonstrate, where practical, that the agent cannot successfully execute a
tool through a direct execution path that bypasses the Tool Gateway.

### 13.8 Contract Boundary Tests

Implement all additional tests required by the canonical
`BIORCH-AGENT-001` contract.

The implementation MUST NOT weaken or remove mandatory contract tests merely
to make the implementation pass.

---

## 14. Architectural Boundaries

Phase 03 MUST remain strictly separated from future phases.

### Explicitly OUT OF SCOPE

The following MUST NOT be implemented:

- LLM-based planning;
- natural-language task planning;
- deterministic orchestration;
- workflow orchestration;
- multi-agent execution;
- agent-to-agent delegation;
- parallel agent execution;
- review loops;
- adaptive planning;
- Tableau parser integration;
- Power BI parser integration;
- BI comparison;
- report generation;
- analysis-ready output;
- autonomous Git operations;
- new credential-management infrastructure.

These capabilities belong to later phases or separate project boundaries.

---

## 15. Phase 04 Boundary

Phase 03 MUST NOT implement the Deterministic Orchestrator.

The Phase 03 agent is a single executable agent.

It MUST NOT:

- coordinate multiple tasks as a workflow;
- coordinate multiple agents;
- schedule or sequence independent agents;
- create orchestration loops;
- implement workflow planning;
- become an implicit orchestrator.

Phase 04 will define and implement the deterministic orchestrator.

---

## 16. BI Parser Boundary

Do NOT implement Tableau or Power BI parsing logic in Phase 03.

Do NOT integrate:

- Tableau workbook parsing;
- Power BI semantic-model parsing;
- TMDL parsing;
- lineage extraction;
- BI comparison;
- parser-specific business logic.

The agent may establish only the generic execution boundary necessary for
future parser tools to be exposed through `BIORCH-TG-001`.

---

## 17. Framework Independence

The implementation MUST remain independent of external agent/orchestration
frameworks.

Do NOT introduce CrewAI, LangChain, AutoGen, LangGraph, or another agent
framework as part of Phase 03 unless such a dependency is explicitly required
by the canonical contract.

The purpose of this phase is to establish the BIOrch agent contract and
runtime boundary before framework adoption is considered.

---

## 18. Files and Implementation Location

The implementation location MUST be selected after repository inspection.

Expected implementation areas are likely to include:

`src/biorch/agents/`

and:

`tests/`

However, these paths are NOT mandatory if the existing architecture
indicates a more appropriate location.

Do not create duplicate abstractions solely to satisfy an expected filename.

If existing files such as:

- `src/biorch/core/agent.py`
- `src/biorch/core/task.py`
- `src/biorch/core/result.py`
- `src/biorch/core/gateway.py`

already provide compatible abstractions, evaluate and reuse them where
appropriate.

Document all implementation-location decisions in the response.

---

## 19. Canonical Contract Protection

The following file MUST NOT be modified as part of implementation:

`contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`

The Tool Gateway contract MUST also remain unchanged:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

If implementation reveals a genuine contract deficiency, STOP and document the
issue rather than modifying the contract.

Contract changes require a separate governed design/change process.

---

## 20. Scope Discipline

Do not perform unrelated cleanup or refactoring.

Do not modify unrelated commands, skills, documentation, governance artifacts,
or historical evidence.

Do not introduce unrelated dependencies.

Do not modify Phase 04 or later-phase contracts.

Do not implement future-phase capabilities "for convenience."

Only make changes necessary to satisfy `BIORCH-AGENT-001` and its tests.

---

## 21. Validation

Before declaring the implementation complete, perform appropriate validation,
including:

1. Unit tests for the deterministic agent.
2. Existing relevant Tool Gateway tests.
3. Full relevant project test suite where practical.
4. Import/package validation.
5. Contract-boundary validation.
6. Verification that no direct tool execution path bypasses the gateway.
7. Verification that no LLM/planning/orchestration capability was introduced.

Report the exact validation commands executed and their results.

If any validation cannot be performed, explicitly document why.

---

## 22. Deviations and Limitations

Any deviation from the canonical contract MUST be explicitly reported.

For each deviation, report:

- contract requirement;
- implementation behavior;
- reason;
- impact;
- whether the deviation is blocking or deferred.

Do NOT silently defer mandatory requirements.

Known limitations that are outside the current repository's available
infrastructure may be documented only when the canonical contract permits
such deferral.

---

## 23. Completion Criteria

Phase 03 implementation is complete only when all applicable criteria below
are satisfied:

- `BIORCH-AGENT-001` mandatory requirements are implemented.
- Agent task validation is deterministic.
- Operation selection is deterministic.
- Tool execution always passes through `BIORCH-TG-001`.
- Direct tool execution bypasses are not introduced.
- Invalid tasks are rejected.
- Unauthorized tools/operations are rejected.
- Tool Gateway rejections are correctly propagated.
- Tool execution failures are correctly represented.
- Structured AgentResult behavior is implemented.
- Required provenance/result information is preserved where required.
- Required tests pass.
- Existing relevant tests continue to pass.
- No LLM-based planning is introduced.
- No orchestration is introduced.
- No multi-agent behavior is introduced.
- No BI parser integration is introduced.
- Canonical contracts remain unchanged.
- No unrelated refactoring is introduced.
- Any deviations or limitations are explicitly documented.

---

## 24. Expected Implementation Response

After implementation, report:

1. **Files Created**
2. **Files Modified**
3. **Files Deleted**, if any
4. **Implementation Summary**
5. **Architecture / Module Decisions**
6. **Tool Gateway Integration**
7. **Determinism Validation**
8. **Tests / Validation Performed**
9. **Validation Results**
10. **Known Limitations**
11. **Deviations from BIORCH-AGENT-001**
12. **Out-of-Scope Items Confirmed**
13. **Any Follow-up Recommendations**

The response MUST distinguish implemented functionality from proposed future
work.

---

## 25. Final Governance Rule

This task authorizes implementation of ONE deterministic agent only.

It does NOT authorize:

- contract modification;
- orchestration;
- multi-agent behavior;
- LLM planning;
- framework adoption;
- BI parser implementation;
- Git mutation;
- unrelated repository cleanup.

When the implementation cannot satisfy a mandatory contract requirement
without violating these boundaries, STOP and report the conflict rather than
expanding the scope.

---

**Final Task Boundary:**

Implement `BIORCH-AGENT-001` as one deterministic agent using the existing
`BIORCH-TG-001` Tool Gateway, with no LLM planning, no orchestration, no
multi-agent behavior, and no BI-parser integration.