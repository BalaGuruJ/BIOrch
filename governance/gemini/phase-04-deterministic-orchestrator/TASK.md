# Phase 04 — Deterministic Orchestrator

## Objective

Implement the first deterministic workflow orchestrator for BIOrch.

The orchestrator shall execute an explicitly defined workflow consisting of
predefined steps in a deterministic sequential order.

The orchestrator must:

1. Accept an explicit workflow definition.
2. Validate the workflow before execution.
3. Execute valid steps strictly in declared order.
4. Delegate each executable step through the existing Phase 03
   `DeterministicAgent`.
5. Ensure all actual tool access remains behind the existing
   `ToolGateway`.
6. Fail closed when workflow validation fails.
7. Fail fast when a required step fails or is rejected.
8. Produce a deterministic, structured workflow result.
9. Preserve all Phase 02 and Phase 03 architectural boundaries.

This phase establishes deterministic orchestration only.

It does NOT introduce planning, autonomy, parallelism, multi-agent collaboration,
LLM reasoning, BI parser integration, or external orchestration frameworks.

---

## Authoritative Contract

The implementation MUST conform to:

`contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`

The existing contracts remain authoritative and MUST NOT be weakened or
modified as part of this phase.

Relevant prior contracts include:

- Phase 02 Tool Gateway contract
- Phase 03 Deterministic Agent contract
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`

If any apparent requirement conflicts with an existing canonical contract,
STOP and report the conflict rather than modifying the contract.

---

## Prerequisites

The following must already exist and remain functional:

- Phase 02 Tool Gateway implementation.
- Phase 03 Deterministic Agent implementation.
- Existing Phase 02 and Phase 03 tests.
- Authorized Tool Gateway tool definitions.
- Valid Python project environment.

Phase 03 is CLOSED and is the dependency boundary for this phase.

---

# Scope

## In Scope

### 1. Workflow Definition

Introduce a framework-independent workflow representation capable of
representing:

- workflow identifier/name
- ordered steps
- step identifier
- step task/input
- any other fields explicitly required by
  `ORCHESTRATOR_CONTRACT.md`

The workflow representation must be deterministic and explicitly declared.

The orchestrator MUST NOT invent, infer, or dynamically generate workflow steps.

---

### 2. Workflow Validation

The orchestrator must validate the complete workflow before executing the
first step.

Validation must reject invalid workflows such as:

- empty workflows, if prohibited by the contract
- duplicate step identifiers
- invalid step definitions
- missing required fields
- unsupported step types
- malformed workflow structures
- any other condition explicitly prohibited by
  `ORCHESTRATOR_CONTRACT.md`

If validation fails:

- no workflow step may execute
- no Tool Gateway call may occur
- the result must indicate rejection
- the failure must be deterministic and structured

---

### 3. Deterministic Sequential Execution

Valid workflows must execute strictly in their declared order.

For example:

```text
Workflow
   |
   +--> Step 1
   |
   +--> Step 2
   |
   +--> Step 3

Execution MUST be:

Step 1 → Step 2 → Step 3

The orchestrator MUST NOT:

reorder steps
execute steps concurrently
execute independent steps in parallel
retry autonomously unless explicitly required by the canonical contract
dynamically insert steps
dynamically remove steps
dynamically decompose a task
4. Deterministic Agent Delegation

The orchestrator is responsible for workflow coordination.

The orchestrator MUST NOT directly execute tools.

The execution boundary MUST remain:

Orchestrator
      |
      v
DeterministicAgent
      |
      v
ToolGateway
      |
      v
Authorized Tool

The orchestrator may invoke the existing DeterministicAgent for each
workflow step.

The orchestrator MUST NOT bypass the Deterministic Agent or Tool Gateway.

5. Fail-Fast Behavior

If a required workflow step:

fails validation,
is rejected by the Deterministic Agent,
is rejected by the Tool Gateway,
or otherwise produces a contract-defined failure,

the orchestrator MUST stop subsequent execution.

Example:

Step 1 → SUCCESS
Step 2 → FAILED
Step 3 → NOT_EXECUTED
Step 4 → NOT_EXECUTED

The orchestrator MUST NOT continue executing later steps after a required
step failure.

6. Structured Workflow Results

The orchestrator must return a structured result representing the final
workflow state.

The result MUST support the states defined by the canonical contract:

SUCCESS
REJECTED
FAILED
NOT_EXECUTED

The result should contain sufficient deterministic information to identify:

workflow identity
final workflow status
step results
execution order
failure/rejection information where applicable

Do not introduce additional result states unless explicitly required by
ORCHESTRATOR_CONTRACT.md.

Architectural Boundary

The Phase 04 architecture is:

                    USER / CALLER
                         |
                         v
                +-------------------+
                |   Orchestrator    |
                |                   |
                | validate workflow |
                | control sequence  |
                | stop on failure  |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Deterministic     |
                | Agent             |
                |   (Phase 03)      |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Tool Gateway      |
                |   (Phase 02)      |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Authorized Tool   |
                +-------------------+

Responsibilities MUST remain separated:

Orchestrator

Responsible for:

workflow validation
workflow sequencing
invoking steps in order
stopping after failure
aggregating workflow results
Deterministic Agent

Responsible for:

validating and executing an individual deterministic task
enforcing its Phase 03 contract
Tool Gateway

Responsible for:

authorization
controlled tool execution
enforcing the Phase 02 boundary

The orchestrator MUST NOT absorb responsibilities belonging to either the
Deterministic Agent or Tool Gateway.

Expected Implementation Areas

Expected new implementation area:

src/biorch/orchestration/

Expected tests:

tests/

The implementation may introduce the minimum necessary modules/classes,
for example:

src/biorch/orchestration/
    __init__.py
    orchestrator.py
    workflow.py
    result.py

These filenames are illustrative, not mandatory.

Gemini MUST inspect the existing project structure and
ORCHESTRATOR_CONTRACT.md before deciding the exact implementation layout.

Do not create unnecessary abstractions.

Testing Requirements

All existing tests MUST continue to pass.

New Phase 04 tests MUST cover at minimum:

Valid execution
valid workflow executes successfully
steps execute in declared order
all expected steps execute exactly once
Validation rejection
malformed workflow is rejected
invalid workflow executes zero steps
Tool Gateway is not reached after workflow validation failure
Fail-fast behavior
first-step failure stops execution
middle-step failure stops later steps
later steps are marked/noted as NOT_EXECUTED where required by the
contract
Boundary enforcement
orchestrator delegates through Deterministic Agent
orchestrator does not directly invoke tools
Tool Gateway rejection propagates correctly
Result correctness
successful workflow produces SUCCESS
invalid workflow produces REJECTED
execution failure produces FAILED
skipped subsequent steps are represented as NOT_EXECUTED
Determinism

Repeated execution of the same explicit workflow with equivalent inputs must
produce the same execution ordering and equivalent result structure.

Acceptance Criteria

Phase 04 is complete only when ALL of the following are satisfied:

ORCHESTRATOR_CONTRACT.md has been read and implemented faithfully.
A framework-independent deterministic orchestrator exists.
Explicit workflows can be represented and validated.
Workflow validation occurs before execution.
Valid workflows execute strictly sequentially.
Steps execute in declared order.
Each step is delegated through the Phase 03 Deterministic Agent.
The orchestrator never directly invokes tools.
Tool access remains exclusively behind the Tool Gateway.
Invalid workflows execute zero steps.
Required step failures terminate the workflow immediately.
Subsequent steps do not execute after failure.
Workflow results expose the required states:
SUCCESS
REJECTED
FAILED
NOT_EXECUTED
Existing Phase 02 tests remain passing.
Existing Phase 03 tests remain passing.
New Phase 04 tests pass.
No LLM is used.
No autonomous planning is introduced.
No dynamic task decomposition is introduced.
No parallel execution is introduced.
No multi-agent collaboration is introduced.
No review loop is introduced.
No Tableau integration is introduced.
No Power BI/PBIParser integration is introduced.
No external orchestration framework is introduced.
Existing Phase 02 and Phase 03 contracts remain unchanged.
The implementation remains framework-independent.
Explicit Non-Goals

The following are explicitly deferred to later phases.

NOT Phase 04
LLM-based planning
adaptive planning
autonomous task decomposition
autonomous tool selection
multi-agent orchestration
specialist agents
parallel execution
asynchronous orchestration
review agents
reviewer loops
retry policies beyond the canonical contract
Tableau parser integration
Power BI parser integration
Tableau/Power BI comparison
CrewAI
LangChain
LangGraph
other external orchestration frameworks

These capabilities MUST NOT be introduced merely because they may be useful
for future phases.

Implementation Discipline

Before modifying source code:

Read contracts/orchestrator/ORCHESTRATOR_CONTRACT.md.
Read the Phase 02 Tool Gateway implementation and contract.
Read the Phase 03 Deterministic Agent implementation and contract.
Inspect existing tests.
Identify reusable interfaces/components.
Confirm the implementation boundary.

If the canonical contract is ambiguous or contradictory:

STOP
DO NOT GUESS
DO NOT MODIFY THE CONTRACT
REPORT THE CONFLICT

Implement the smallest architecture that satisfies the contract and this task.

Do not introduce speculative abstractions for future phases.

Required Response Artifact

Implementation work MUST eventually produce:

governance/gemini/phase-04-deterministic-orchestrator/RESPONSE.md

The response MUST document:

Files created.
Files modified.
Implementation summary.
Workflow model introduced.
Validation behavior.
Sequential execution behavior.
Deterministic Agent integration.
Tool Gateway boundary enforcement.
Fail-fast behavior.
Workflow result behavior.
Tests executed.
Test results.
Contract compliance.
Confirmation that prohibited Phase 04 capabilities were not introduced.
Known limitations, if any.
Any deviations from this task.
Review Requirements

After implementation, /biorch-review MUST verify:

Compliance with ORCHESTRATOR_CONTRACT.md.
Compliance with this TASK.md.
Preservation of Phase 02 boundaries.
Preservation of Phase 03 boundaries.
Deterministic sequential execution.
Workflow validation before execution.
Fail-fast behavior.
Structured result correctness.
Absence of prohibited capabilities.
Test coverage and results.

Review findings MUST be persisted to:

governance/gemini/phase-04-deterministic-orchestrator/REVIEW.md

No transition to READY_FOR_CLOSURE should occur without explicit human
approval through the governed review process.

Closure Requirements

Phase 04 may transition to CLOSED only after:

Implementation is complete.
Tests pass.
/biorch-review has completed.
Review findings are persisted.
Human approval is obtained.
Required closure evidence is generated.
The authoritative PHASE_INDEX.md is updated through the governed
lifecycle mechanism.

Closure MUST NOT modify or weaken canonical contracts.

Expected Final Response

Gemini should eventually report:

Files created.
Files modified.
Implementation summary.
Workflow structure introduced.
Validation behavior.
Sequential execution behavior.
Deterministic Agent integration.
Tool Gateway integration.
Fail-fast behavior.
Structured result behavior.
Tests/validation performed.
Test results.
Compliance with ORCHESTRATOR_CONTRACT.md.
Confirmation that Phase 04 non-goals were not introduced.
Known limitations.
Any deviations from this task.
Final implementation status.

### One important point

I would **not start coding immediately after replacing this file**.

Your current state is actually good:

```text
Phase 03  CLOSED
     │
     ▼
Phase 04  IN_PROGRESS
     │
     ▼
TASK.md   ← we're defining this now
     │
     ▼
implementation
     │
     ▼
RESPONSE.md
     │
     ▼
/biorch-review
     │
     ▼
human approval
     │
     ▼
READY_FOR_CLOSURE
     │
     ▼
/biorch-close
     │
     ▼
CLOSED