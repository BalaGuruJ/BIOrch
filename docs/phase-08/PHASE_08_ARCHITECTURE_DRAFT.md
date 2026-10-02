# BIOrch Phase 08 — Parallel Orchestration
# Architecture Draft — Gemini CLI Local Multi-Agent Execution Substrate

**Status:** DRAFT — NOT IMPLEMENTATION-AUTHORITATIVE  
**Phase:** 08 — Parallel Orchestration  
**Predecessor:** Phase 07 — Power BI / PBIParser Integration  
**Primary Objective:** Define and validate a local multi-agent orchestration architecture for BIOrch using Google Gemini CLI as an execution substrate.

---

## 1. Document Status and Authority

This document is an architectural DRAFT for Phase 08.

It is not yet:

- an implementation contract;
- an implementation task;
- a final architecture decision;
- permission to modify Gemini CLI source code;
- permission to modify Phase 07 implementation;
- proof that every described Gemini CLI capability currently exists;
- a commitment to MCP, A2A, Skills, Custom Commands, or native Gemini subagents.

Before implementation begins, all claims marked `CONFIRMED` or otherwise attributed to Gemini CLI MUST be verified against the current official `google-gemini/gemini-cli` repository and official documentation.

The final Phase 08 architecture shall distinguish explicitly between:

1. VERIFIED GEMINI CLI CAPABILITY
2. BIOrch EXISTING CAPABILITY
3. ARCHITECTURAL INFERENCE
4. BIOrch PROPOSAL
5. FUTURE / OPTIONAL CAPABILITY

---

# 2. Phase 08 Context

Phase 07 — Power BI / PBIParser Integration — is formally CLOSED.

Phase 07 established the Power BI integration boundary and associated contracts, provenance, runtime integration, canonicalization, serialization, and verification evidence.

Phase 08 changes the primary concern from individual BI-platform integration toward orchestration across specialized analysis actors.

The initial conceptual use case is:

> Give BIOrch a cross-platform BI question and allow specialized Tableau and Power BI analysis workers to operate independently and in parallel, followed by deterministic BIOrch reconciliation and synthesis.

The intended first demonstration is a question that requires both:

- Tableau metadata analysis;
- Power BI metadata analysis;

followed by a BIOrch-controlled comparison.

---

# 3. Existing BIOrch Architectural Constraints

The existing BIOrch architecture defines the following conceptual layers:

1. User / Experience
2. Orchestration
3. Agents
4. Capabilities / Tools
5. Domain Engines

The existing architecture also establishes:

- framework-neutral internal contracts;
- structured communication;
- narrow agent responsibilities;
- narrow tool permissions;
- deterministic-first orchestration;
- human approval for sensitive operations;
- Tool Gateway as the security boundary;
- domain engines remaining outside BIOrch itself.

Phase 08 MUST preserve these principles.

Gemini CLI therefore MUST NOT become the owner of BIOrch governance.

---

# 4. Core Architectural Boundary

The primary architectural hypothesis is:

> BIOrch remains the authoritative orchestrator and governance layer. Gemini CLI is treated as an execution substrate for LLM-driven agent workers.

Conceptually:

```text
                    ┌───────────────────────────────┐
                    │          BIOrch               │
                    │                               │
                    │  Governance                   │
                    │  Contracts                    │
                    │  Task Dispatch                │
                    │  Evidence                     │
                    │  Validation                    │
                    │  Synthesis                     │
                    │  Lifecycle                    │
                    └───────────────┬───────────────┘
                                    │
                         controlled execution
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       Gemini CLI Substrate    │
                    │                               │
                    │  Model interaction            │
                    │  Context handling             │
                    │  Tool execution               │
                    │  Agent/subagent capabilities  │
                    │  Local process execution      │
                    └───────────────────────────────┘
````

BIOrch owns the decision about:

* what task is executed;
* which specialist is invoked;
* what evidence may be consumed;
* what output contract is required;
* whether the returned result is valid;
* how results are reconciled;
* whether the final result may be presented to the user.

Gemini CLI MUST NOT independently become the authoritative source of BIOrch governance state.

---

# 5. Phase 08 Architectural Hypothesis

The initial architecture hypothesis is a process-isolated orchestration model.

```text
                         User Question
                              │
                              ▼
                    ┌─────────────────────┐
                    │ BIOrch Orchestrator │
                    └──────────┬──────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
              Gemini CLI  Gemini CLI  Gemini CLI
              Tableau     Power BI    Governance/
              Specialist  Specialist  Validation
                    │          │          │
                    ▼          ▼          ▼
              Tableau      Power BI    BIOrch
              metadata     metadata    contracts
                    │          │          │
                    └──────────┼──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ BIOrch Validation   │
                    │ & Reconciliation    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ BIOrch Synthesis    │
                    └──────────┬──────────┘
                               ▼
                    Evidence-backed answer
```

This is a hypothesis to be tested, not yet an implementation commitment.

---

# 6. Candidate Gemini CLI Integration Models

Phase 08 shall evaluate at least the following models.

## Option A — Single Gemini CLI Session with Internal Subagents

```text
BIOrch
  │
  ▼
Gemini CLI
  ├── Tableau specialist
  ├── Power BI specialist
  └── Validator
```

Potential advantages:

* fewer external processes;
* potentially simpler interactive operation;
* ability to use Gemini CLI's own agent/subagent mechanisms.

Questions requiring verification:

* current subagent definition mechanism;
* current context isolation behavior;
* current parallel execution behavior;
* current tool restrictions;
* current output/return semantics;
* suitability for external BIOrch control.

---

## Option B — BIOrch Python Process Orchestrator

```text
                         BIOrch
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        Gemini CLI    Gemini CLI    Gemini CLI
          process       process       process
          Tableau       Power BI      Validator
              │            │            │
              └────────────┼────────────┘
                           ▼
                       BIOrch
                    reconciliation
```

This is the initial architectural candidate for the local proof-of-concept because process boundaries provide explicit:

* context isolation;
* stdout/stderr capture;
* exit codes;
* timeout handling;
* independent failure boundaries;
* lifecycle control;
* observability.

This option MUST still be validated experimentally before becoming the Phase 08 implementation contract.

---

## Option C — Hybrid Process + Gemini Subagents

BIOrch launches Gemini CLI workers, with each worker potentially managing additional internal subagents.

This is intentionally deferred until the simpler process model is proven.

---

## Option D — A2A-Based Architecture

Gemini CLI / A2A capabilities could eventually provide a network or RPC-based agent boundary.

This is considered a future scalability option.

A2A MUST NOT be treated as a prerequisite for the Phase 08 local proof-of-concept unless official capability verification and implementation testing demonstrate a concrete need.

---

## Option E — MCP-Centric Single-Agent Architecture

A single Gemini agent accesses Tableau and Power BI capabilities through multiple MCP servers.

This remains a candidate architecture but does not automatically provide the desired domain isolation.

The architecture shall explicitly evaluate whether placing multiple BI domains in one agent context introduces undesirable context/tool interference.

---

# 7. Initial Phase 08 Recommendation Hypothesis

The current working hypothesis is:

> Start with Option B — BIOrch Python Process Orchestrator + independent headless Gemini CLI processes.

Reasoning:

* preserves BIOrch ownership of orchestration;
* gives each specialist an independent process boundary;
* provides explicit failure isolation;
* permits deterministic orchestration around nondeterministic workers;
* is relatively easy to reproduce locally;
* avoids requiring BIOrch to modify Gemini CLI internals;
* allows later evaluation of native Gemini subagents, MCP, Skills, and A2A.

This is a hypothesis and MUST be verified through implementation experiments.

---

# 8. Specialist Agent Model

The initial conceptual specialist set is:

## 8.1 Tableau Specialist

Purpose:

Analyze Tableau metadata exposed by BIOrch.

Potential responsibilities:

* inspect Tableau canonical metadata;
* identify tables, columns, calculations, relationships and worksheet usage;
* analyze Tableau-specific semantic constructs;
* produce structured evidence-backed findings.

The specialist MUST NOT become the owner of Tableau canonicalization or BIOrch governance.

---

## 8.2 Power BI Specialist

Purpose:

Analyze Power BI metadata produced through the existing BIOrch Power BI integration.

Potential responsibilities:

* inspect semantic model metadata;
* analyze tables, columns and measures;
* analyze relationships;
* analyze DAX-related metadata;
* use Phase 07 provenance/evidence information.

The specialist MUST NOT replace or modify the Phase 07 PBIParser domain engine.

---

## 8.3 Governance / Validation Worker

Potential responsibility:

Independently inspect specialist results for:

* contract compliance;
* missing evidence;
* malformed output;
* unsupported claims;
* provenance violations;
* incomplete execution.

However, the architecture shall determine whether this needs to be an LLM agent at all.

Where deterministic Python validation can perform the operation reliably, BIOrch SHOULD prefer deterministic validation instead of delegating the responsibility to another LLM.

---

# 9. Deterministic Governance Boundary

The most important architectural principle for Phase 08 is:

> LLM agents may reason; BIOrch determines whether their output is acceptable.

Therefore:

```text
LLM Result
    │
    ▼
Schema Validation
    │
    ▼
Evidence Validation
    │
    ▼
Provenance Validation
    │
    ▼
Business / Contract Rules
    │
    ▼
Accepted / Rejected / Partial
```

No LLM response shall be considered authoritative merely because the model produced valid-looking text.

---

# 10. Structured Agent Result Contract

Phase 08 shall define a structured result contract.

The exact schema is NOT yet final.

The contract should conceptually contain:

```json
{
  "agent_id": "...",
  "platform": "...",
  "status": "SUCCESS",
  "findings": [],
  "source_evidence": [],
  "limitations": [],
  "execution_metadata": {}
}
```

The final schema must align with existing BIOrch contract conventions rather than creating a disconnected second contract system.

The architecture must therefore inspect:

* existing agent contracts;
* orchestrator contracts;
* Tableau contract;
* Power BI contract;
* tool gateway contract;
* existing provenance structures.

No duplicate contract should be introduced where an existing authoritative contract can be extended or reused.

---

# 11. Evidence and Provenance

Every specialist result must remain traceable to its source.

The conceptual relationship is:

```text
Source Metadata
      │
      ▼
Agent Analysis
      │
      ▼
Finding
      │
      ▼
Source Evidence
      │
      ▼
BIOrch Validation
```

The agent MUST NOT invent provenance.

Where a finding cannot be linked to evidence, the result must explicitly identify the limitation rather than silently treating inference as fact.

---

# 12. Context Isolation

Phase 08 shall investigate multiple levels of isolation.

## Level 1 — Workspace / Filesystem Isolation

Specialists should receive only the metadata relevant to their assigned task.

Example:

```text
workspace/
├── tableau/
└── powerbi/
```

This is a proposed organizational mechanism, not yet a security guarantee.

---

## Level 2 — Prompt / Instruction Isolation

Each specialist should have domain-specific instructions.

Tableau instructions MUST NOT implicitly authorize Power BI reasoning.

Power BI instructions MUST NOT implicitly authorize Tableau assumptions.

---

## Level 3 — Tool Permission Isolation

Tools should be explicitly scoped.

An agent should receive only the capabilities required for its task.

Tool Gateway policy remains authoritative.

---

## Level 4 — Process Isolation

Independent Gemini CLI processes provide an additional runtime boundary.

Process isolation is preferred for the initial local experiment because it is observable and independently controllable.

---

# 13. Gemini CLI Capabilities Requiring Official Verification

Before implementation, the following claims MUST be checked against the current official Gemini CLI repository/documentation:

### CLI execution

* headless/non-interactive execution;
* prompt execution;
* structured output modes;
* exit-code behavior;
* stdout/stderr behavior;
* process lifecycle.

### Agents / subagents

* current agent model;
* agent configuration;
* context isolation;
* delegation;
* parallel execution;
* tool restrictions;
* lifecycle semantics.

### Skills

* current Skills specification;
* discovery locations;
* loading semantics;
* precedence;
* activation mechanism;
* command/API syntax.

### Custom Commands

* current TOML format;
* argument substitution;
* shell execution syntax;
* approval behavior;
* project/global scope;
* interaction with Skills.

### MCP

* MCP client capability;
* supported transports;
* configuration format;
* lifecycle;
* tool discovery;
* security/trust configuration.

### A2A

* current A2A implementation status;
* supported transport;
* local feasibility;
* configuration;
* maturity;
* whether it is appropriate for Phase 08.

### SDK / Programmatic Integration

* current SDK availability;
* supported invocation model;
* whether SDK integration is preferable to subprocess execution;
* compatibility with Python BIOrch.

Every capability must be classified as:

```text
VERIFIED
PARTIALLY VERIFIED
NOT VERIFIED
PROPOSED
FUTURE
```

---

# 14. Gemini CLI Must Remain an External Dependency

Phase 08 shall not modify the source code of:

```text
google-gemini/gemini-cli
```

The initial BIOrch integration should treat Gemini CLI as an external runtime dependency.

This creates a clean boundary:

```text
BIOrch Repository
        │
        │ controlled invocation
        ▼
Gemini CLI installation
        │
        ▼
Gemini model/runtime
```

The architecture should not fork or embed Gemini CLI internals merely to prove the local orchestration concept.

---

# 15. MCP Position

MCP is a potential tool integration mechanism.

A future conceptual structure may be:

```text
Gemini CLI
    │
    ▼
MCP Client
    │
    ├── BIOrch Tableau Tools
    ├── BIOrch Power BI Tools
    └── BIOrch Governance Tools
```

However:

> MCP is not automatically a requirement for the first Phase 08 proof-of-concept.

The first experiment should determine whether direct read-only access to prepared canonical metadata is sufficient.

MCP should be introduced when there is a demonstrated need for tool-mediated access.

---

# 16. Skills Position

Gemini CLI Skills may provide domain-specific procedural knowledge.

Potential future examples:

```text
tableau-analysis
powerbi-analysis
biorch-governance
biorch-evidence-analysis
```

However, Skills are not equivalent to:

* agents;
* orchestration;
* contracts;
* tools;
* governance.

They should be treated as instruction/context packaging mechanisms unless official Gemini CLI verification demonstrates additional capabilities.

---

# 17. Custom Commands Position

Gemini CLI custom commands may be useful for developer/operator workflows.

Potential examples:

```text
/biorch-status
/biorch-next
/biorch-roadmap
/biorch-analyze
```

The existing repository already contains BIOrch-oriented custom command definitions.

Phase 08 must not conflate these developer workflow commands with the runtime orchestration architecture.

A command that launches an orchestration workflow is an entry mechanism, not the orchestration engine itself.

---

# 18. Synthesis Architecture

The initial synthesis boundary should remain inside BIOrch.

```text
Tableau Result
      │
      ├──────────────┐
      │              │
      ▼              ▼
                 BIOrch
      ▲          Reconciliation
      │              │
      │              ▼
Power BI Result   Validated Result
                     │
                     ▼
                 Synthesis
                     │
                     ▼
               User Response
```

The synthesis layer must distinguish:

* direct evidence;
* deterministic reconciliation;
* model interpretation;
* unresolved discrepancies;
* unsupported assumptions.

---

# 19. Failure Model

Each specialist execution must have an explicit lifecycle.

Conceptually:

```text
DISPATCH
   │
   ▼
RUNNING
   │
   ├── SUCCESS
   │
   ├── TIMEOUT
   │
   ├── PROCESS_FAILURE
   │
   ├── INVALID_OUTPUT
   │
   └── CONTRACT_VIOLATION
```

BIOrch should retain enough execution metadata to determine:

* which worker ran;
* when it started;
* when it ended;
* exit status;
* timeout state;
* output validation status;
* evidence validation status.

Retry behavior should not be hard-coded into this architecture draft.

Retry policy shall be defined only after failure behavior is experimentally verified.

---

# 20. Security Boundary

Phase 08 must preserve the existing Tool Gateway security boundary.

The architecture must avoid giving an LLM unrestricted authority over:

* arbitrary filesystem writes;
* arbitrary shell execution;
* network access;
* production BI systems;
* credentials;
* repository mutation.

The initial prototype should favor:

* read-only metadata;
* controlled working directories;
* explicit tool allowlists;
* deterministic validation;
* no production write-back.

---

# 21. Initial Proof-of-Concept

The first implementation experiment should be intentionally small.

### Input

A cross-platform BI question such as:

```text
Compare a specific semantic concept between the Tableau
and Power BI metadata available to BIOrch.
```

### Execution

```text
Python BIOrch controller
        │
        ├── Gemini CLI → Tableau specialist
        │
        └── Gemini CLI → Power BI specialist
```

### Result

Each worker returns a structured result.

### Validation

BIOrch validates each result.

### Synthesis

BIOrch combines the validated results.

### Demonstration

The system produces:

```text
Question
   ↓
Parallel specialist analysis
   ↓
Independent structured results
   ↓
BIOrch validation
   ↓
Cross-platform reconciliation
   ↓
Evidence-backed answer
```

This is the minimum successful Phase 08 demonstration.

---

# 22. Phase 08 Implementation Boundary

## In Scope

Initially:

1. Gemini CLI capability verification.
2. Phase 08 architecture validation.
3. Agent/result contract definition.
4. Local process orchestration experiment.
5. Tableau specialist prototype.
6. Power BI specialist prototype.
7. Deterministic result validation.
8. Cross-platform synthesis prototype.
9. Execution tracing.
10. Failure isolation testing.

## Explicitly Out of Scope Initially

1. Kubernetes orchestration.
2. Cloud distributed agents.
3. Production deployment.
4. Autonomous BI-platform write-back.
5. Modification of Gemini CLI source code.
6. Mandatory A2A adoption.
7. Mandatory MCP adoption.
8. Mandatory native Gemini subagent adoption.
9. Replacing Phase 07 PBIParser implementation.
10. Replacing existing BIOrch contracts without evidence.

---

# 23. Architecture Verification Gate

Before implementation begins, a dedicated verification task shall answer:

### Gemini CLI

* What is officially supported today?
* What is experimental?
* What has changed from the architecture artifact?
* Which claims from the initial research are incorrect or overstated?

### BIOrch

* Which existing contracts already cover Phase 08?
* Which existing agent abstractions can be reused?
* What orchestration code already exists?
* What Tool Gateway interfaces already exist?
* What Phase 07 outputs can be consumed directly?
* What existing Skills and Custom Commands already exist?

### Integration

* Is subprocess execution sufficient?
* Is SDK integration preferable?
* Are internal Gemini subagents necessary?
* Is MCP necessary?
* Is A2A necessary?
* Where should context boundaries exist?
* Where should validation occur?

No implementation decision should be finalized until these questions are answered.

---

# 24. Architecture Decision Criteria

The eventual Phase 08 architecture should be evaluated against:

| Criterion            | Requirement                                 |
| -------------------- | ------------------------------------------- |
| Governance ownership | BIOrch remains authoritative                |
| Context isolation    | Specialist domains remain isolated          |
| Process isolation    | Worker failures are independently contained |
| Determinism          | Structural validation remains deterministic |
| Provenance           | Findings remain evidence-backed             |
| Observability        | Worker execution can be audited             |
| Security             | Tool access is explicitly controlled        |
| Extensibility        | Additional BI agents can be added           |
| Framework neutrality | Gemini CLI remains replaceable              |
| Local feasibility    | Works in Google Cloud Shell / Linux         |
| Testability          | Each component can be independently tested  |
| Failure handling     | Timeouts and malformed results are explicit |

---

# 25. Framework-Neutrality Requirement

Gemini CLI is an implementation substrate, not the BIOrch architecture itself.

The conceptual dependency should remain:

```text
BIOrch Contracts
      │
      ▼
Orchestration Adapter
      │
      ├── Gemini CLI Adapter
      ├── Future Framework Adapter
      └── Future Local Model Adapter
```

This preserves the existing BIOrch framework-neutral architecture.

The internal contracts should not become Gemini-specific merely because Gemini CLI is the first execution substrate.

---

# 26. Proposed Phase 08 Lifecycle

```text
Phase 08.0
Architecture Draft
      │
      ▼
Phase 08.0A
Official Gemini CLI Verification
      │
      ▼
Phase 08.1
BIOrch Contract / Boundary Review
      │
      ▼
Phase 08.2
Minimal Local Gemini CLI Worker
      │
      ▼
Phase 08.3
Parallel Tableau + Power BI Workers
      │
      ▼
Phase 08.4
Validation + Provenance Gate
      │
      ▼
Phase 08.5
Cross-Platform Synthesis
      │
      ▼
Phase 08.6
Failure / Security / Observability Verification
      │
      ▼
Phase 08.7
End-to-End Verification
      │
      ▼
Phase 08 Closure
```

These phase numbers are provisional and must not be treated as the final implementation plan until the architecture verification gate is complete.

---

# 27. Current Architectural Decision

### Decision Status

**PENDING VERIFICATION**

### Current Hypothesis

Use Gemini CLI as an externally installed execution substrate and initially invoke independent headless Gemini CLI processes from a Python BIOrch orchestrator.

### Why

This provides a relatively simple experiment with:

* explicit process boundaries;
* independent worker lifecycle;
* observable execution;
* straightforward failure handling;
* preservation of BIOrch governance ownership;
* no dependency on Gemini CLI internal implementation details.

### What remains unresolved

* exact Gemini CLI headless invocation contract;
* current structured-output behavior;
* current Skills behavior;
* current Custom Command behavior;
* current subagent behavior;
* current parallel scheduler behavior;
* MCP requirements;
* A2A requirements;
* SDK viability;
* security model for automated execution;
* best context-isolation mechanism.

---

# 28. Required Next Artifact

The next artifact after this draft should be:

```text
inspection/PHASE_08_GEMINI_CLI_CAPABILITY_VERIFICATION.md
```

It shall independently verify the claims made in this architecture draft against:

1. the current official `google-gemini/gemini-cli` repository;
2. official Gemini CLI documentation;
3. the current BIOrch repository state.

The verification artifact must classify every significant capability as:

* VERIFIED
* PARTIALLY VERIFIED
* NOT VERIFIED
* INFERRED
* PROPOSED
* DEFERRED

The verification must explicitly identify any claims from earlier research that should be removed or corrected.

Only after this verification should the Phase 08 architecture become implementation-authoritative.

---

# 29. Final Principle

Phase 08 must demonstrate:

> **BIOrch orchestrates. Gemini CLI executes. Domain engines provide BI truth. Contracts and deterministic gates decide what is accepted.**

No individual LLM agent, Gemini CLI session, Skill, MCP server, or framework component becomes the authoritative source of BIOrch governance or evidence.

**Document Status: DRAFT — AWAITING OFFICIAL GEMINI CLI CAPABILITY VERIFICATION**