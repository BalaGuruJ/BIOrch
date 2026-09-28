# BIOrch Deterministic Orchestrator Contract

**Contract ID:** BIORCH-ORCH-001

**Contract Name:** Deterministic Orchestrator Contract

**Phase:** Phase 04 — Deterministic Orchestrator

**Status:** DRAFT

**Depends On:**
- BIORCH-TG-001 — Tool Gateway Contract
- BIORCH-AGENT-001 — Deterministic Agent Contract

---

## 1. Purpose

This contract defines the minimum deterministic orchestration boundary for
BIOrch.

Phase 04 introduces the ability to execute a predefined, ordered workflow
consisting of known tasks through the existing Deterministic Agent and Tool
Gateway boundaries.

The orchestrator MUST coordinate execution.

The orchestrator MUST NOT perform the work of the agent or the Tool Gateway
itself.

The required architectural relationship is:

    Structured Workflow
          ↓
    Deterministic Orchestrator
          ↓
    Deterministic Agent
          ↓
    Tool Gateway
          ↓
    Authorized Tool
          ↓
    Agent Result
          ↓
    Orchestrator Result

---

## 2. Architectural Principle

The Phase 04 orchestrator is a coordination component, not an autonomous
planner.

It MUST execute a workflow that has already been explicitly defined.

For a given workflow definition and equivalent execution conditions, the
orchestrator MUST follow the same execution sequence.

The orchestrator MUST NOT dynamically determine what work should be performed.

---

## 3. Source of Truth

The following contracts remain authoritative:

- `contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`
- `contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`

The orchestrator MUST use the existing Deterministic Agent boundary.

The orchestrator MUST NOT bypass the Deterministic Agent to invoke tools
directly.

The orchestrator MUST NOT weaken or redefine Tool Gateway security rules.

---

## 4. Deterministic Workflow

A workflow MUST be explicitly defined as an ordered sequence of known steps.

Each step MUST identify sufficient information to deterministically execute
that step.

At minimum, a workflow step MUST identify:

- step identifier;
- target agent;
- operation;
- required inputs;
- execution order.

Example:

    Step 1 → Agent A / operation X
    Step 2 → Agent A / operation Y
    Step 3 → Agent A / operation Z

The orchestrator MUST execute steps in their declared order.

---

## 5. Sequential Execution

Phase 04 MUST support sequential workflow execution.

Given:

    [Step A, Step B, Step C]

the execution order MUST always be:

    Step A
       ↓
    Step B
       ↓
    Step C

The orchestrator MUST NOT:

- reorder steps;
- execute steps concurrently;
- skip steps without an explicit workflow rule;
- dynamically insert steps;
- dynamically remove steps.

Parallel execution belongs to Phase 08.

---

## 6. Agent Boundary

Every executable workflow step MUST be delegated to an approved
Deterministic Agent.

The orchestrator MUST NOT:

- invoke tools directly;
- bypass the Tool Gateway;
- execute shell commands;
- execute arbitrary Python;
- directly access protected resources;
- implement agent-specific business logic.

The execution path MUST remain:

    Orchestrator
        ↓
    Deterministic Agent
        ↓
    Tool Gateway
        ↓
    Tool

---

## 7. Workflow Validation

A workflow MUST be validated before execution begins.

Validation MUST verify, where applicable:

- workflow structure;
- workflow identifier;
- workflow version;
- step identifiers;
- step ordering;
- target agent availability;
- supported operations;
- required inputs;
- workflow constraints.

If workflow validation fails, execution MUST NOT begin.

The orchestrator MUST fail closed.

---

## 8. Deterministic Execution

The orchestrator MUST NOT use:

- LLM planning;
- probabilistic routing;
- autonomous task decomposition;
- dynamic workflow generation;
- dynamic tool discovery;
- natural-language planning;
- adaptive agent selection.

The orchestrator MUST execute only the workflow that was explicitly
provided or registered.

---

## 9. Step Failure Behavior

The default Phase 04 behavior is fail-fast.

If a workflow step fails:

    Step A → SUCCESS
    Step B → FAILURE
    Step C → NOT EXECUTED

the orchestrator MUST terminate the workflow unless an explicitly defined
workflow policy permits continuation.

The orchestrator MUST NOT silently continue after a failed required step.

---

## 10. Retry Behavior

Phase 04 MUST NOT introduce autonomous retry policies.

The orchestrator MUST NOT retry a failed step unless the workflow explicitly
defines a deterministic retry policy.

Any retry policy, if supported, MUST specify:

- maximum retry count;
- same operation;
- same target agent;
- same authorization boundary;
- deterministic retry behavior.

A retry MUST NOT be used to bypass an authorization or Tool Gateway rejection.

Complex adaptive retry policies belong to later orchestration/runtime work.

---

## 11. Workflow Termination

Every workflow MUST have a deterministic termination condition.

A workflow MUST terminate when:

- all required steps complete successfully; or
- a required step fails; or
- an explicitly defined deterministic termination rule is reached.

The orchestrator MUST NOT run indefinitely.

The orchestrator MUST NOT create an autonomous execution loop.

---

## 12. Orchestrator Result

The orchestrator MUST return a structured result representing the workflow
execution.

The result SHOULD communicate:

- workflow identifier;
- workflow version;
- execution status;
- completed steps;
- failed step, where applicable;
- skipped/not-executed steps;
- step results;
- structured errors;
- execution provenance.

The orchestrator MUST NOT report successful workflow completion if a required
workflow step failed.

---

## 13. Workflow Result Status

The orchestrator MUST distinguish at least:

### SUCCESS

All required workflow steps completed successfully.

### REJECTED

The workflow was rejected before execution because validation or authorization
requirements were not satisfied.

### FAILED

Workflow execution started but one or more required steps failed.

### NOT_EXECUTED

A step was not executed because the workflow terminated before reaching it.

---

## 14. Failure and Security Boundaries

The orchestrator MUST fail closed when required conditions cannot be
deterministically satisfied.

Examples include:

- invalid workflow;
- unknown workflow;
- invalid workflow step;
- unknown agent;
- unsupported operation;
- invalid inputs;
- agent rejection;
- Tool Gateway rejection;
- agent execution failure;
- workflow constraint violation.

The orchestrator MUST NOT circumvent a lower-level rejection.

---

## 15. State and Execution History

The orchestrator MUST maintain sufficient execution state to determine:

- current workflow;
- current step;
- completed steps;
- failed step;
- terminal workflow state.

The execution state MUST NOT alter the workflow definition itself.

The orchestrator MUST NOT mutate a workflow dynamically during execution.

---

## 16. Idempotency and Re-Execution

Phase 04 MUST define deterministic behavior for workflow re-execution.

A failed workflow MUST NOT automatically restart from the beginning unless an
explicit deterministic execution policy requests it.

The orchestrator MUST NOT duplicate completed work implicitly.

Advanced durable execution, checkpoint recovery, and distributed workflow
state are outside the minimum Phase 04 scope unless explicitly required by
the implementation contract.

---

## 17. Scope of Phase 04

Phase 04 MUST establish only deterministic sequential orchestration.

IN SCOPE:

- workflow definition;
- workflow validation;
- deterministic step ordering;
- sequential execution;
- delegation to Deterministic Agent;
- step result collection;
- fail-fast behavior;
- deterministic termination;
- structured workflow results;
- execution-state tracking necessary for the above;
- unit tests for orchestration behavior.

---

## 18. Explicitly Out of Scope

The following MUST NOT be implemented in Phase 04:

### Multi-Agent Architecture

- multiple specialized BI agents;
- agent-to-agent collaboration;
- agent delegation networks;
- autonomous agent discovery.

These belong to later phases.

### Parallel Execution

- concurrent agent execution;
- parallel branches;
- task fan-out/fan-in;
- worker pools.

Parallel orchestration belongs to Phase 08.

### Review Loops

- evaluator agents;
- maker/checker loops;
- autonomous review cycles.

These belong to Phase 09.

### LLM Planning

- LLM-based workflow generation;
- natural-language planning;
- adaptive routing;
- autonomous task decomposition;
- probabilistic agent selection.

These belong to Phase 10.

### BI Integration

- Tableau parsing;
- Power BI parsing;
- TMDL parsing;
- lineage extraction;
- BI comparison;
- report generation.

These belong to later BI capability phases.

---

## 19. Framework Independence

Phase 04 MUST remain framework-independent.

Do NOT introduce:

- CrewAI;
- LangChain;
- LangGraph;
- AutoGen;
- another agent orchestration framework.

The purpose of Phase 04 is to establish the canonical deterministic
orchestration boundary before framework evaluation or adoption.

---

## 20. Tool Gateway Boundary

The orchestrator MUST NOT invoke tools directly.

The only permitted execution path is:

    Workflow
       ↓
    Orchestrator
       ↓
    Deterministic Agent
       ↓
    Tool Gateway
       ↓
    Authorized Tool

Any implementation that bypasses the Deterministic Agent or Tool Gateway is
non-compliant with this contract.

---

## 21. Testing Requirements

Tests MUST demonstrate at minimum:

### 21.1 Valid Sequential Workflow

Verify that:

- a valid workflow is accepted;
- steps execute in declared order;
- each step delegates to the correct agent;
- the final workflow result represents SUCCESS.

### 21.2 Workflow Validation Failure

Verify that an invalid workflow is rejected before execution.

### 21.3 Step Failure

Verify that a failed required step:

- produces a failed workflow result;
- terminates execution;
- prevents subsequent required steps from executing.

### 21.4 Agent Rejection

Verify that an agent rejection is correctly propagated to the orchestrator.

### 21.5 Tool Gateway Rejection

Verify that a lower-level Tool Gateway rejection cannot be bypassed.

### 21.6 Deterministic Ordering

Verify that repeated execution of the same workflow produces the same
declared step order.

### 21.7 No Parallel Execution

Verify that Phase 04 does not execute independent steps concurrently.

### 21.8 Explicit Termination

Verify that workflows always reach a defined terminal state.

### 21.9 No Direct Tool Access

Verify that the orchestrator delegates through the Deterministic Agent rather
than invoking tools directly.

---

## 22. Architectural Acceptance Criteria

Phase 04 is compliant only when all of the following are true:

1. A workflow can be explicitly defined.
2. The workflow can be validated before execution.
3. Steps execute deterministically in declared order.
4. Every step delegates through the Deterministic Agent.
5. The Deterministic Agent remains responsible for tool execution boundaries.
6. Tool Gateway security remains authoritative.
7. Required-step failure terminates the workflow by default.
8. Workflow execution produces a structured result.
9. Workflow execution always terminates.
10. No LLM planning is introduced.
11. No parallel execution is introduced.
12. No multi-agent architecture is introduced.
13. No review loop is introduced.
14. No BI parser integration is introduced.
15. Tests demonstrate the required orchestration behavior.
16. Existing Phase 03 behavior and contracts remain intact.

---

## 23. Compatibility Requirement

Phase 04 MUST preserve the behavior and contracts established by Phase 03.

The implementation MUST NOT modify the semantics of:

- BIORCH-TG-001;
- BIORCH-AGENT-001.

If a change appears necessary to either contract, it MUST be treated as a
separate architectural decision rather than silently changing the existing
contract.

---

## 24. Phase Boundary

Phase 04 establishes:

    "Known workflow → deterministic sequential execution"

It does NOT establish:

    "Decide what workflow should exist."

Dynamic planning belongs to Phase 10.

It does NOT establish:

    "Execute multiple agents concurrently."

Parallel orchestration belongs to Phase 08.

It does NOT establish:

    "Have agents evaluate or review one another."

Review loops belong to Phase 09.

Therefore the canonical Phase 04 boundary is:

    Explicit Workflow
          ↓
    Deterministic Orchestrator
          ↓
    Deterministic Agent
          ↓
    Tool Gateway
          ↓
    Authorized Tool