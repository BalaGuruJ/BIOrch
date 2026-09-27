# BIOrch Tool Gateway Contract

**Contract ID:** BIORCH-TG-001  
**Version:** 1.0  
**Status:** DEFINED  
**Lifecycle Phase:** Phase 2 — Tool Gateway  
**Contract Type:** Runtime Architecture Contract  
**Implementation Status:** NOT YET IMPLEMENTED  

---

## 1.1. Status

This contract is currently a placeholder defining the intended architectural requirements for the BIOrch Tool Gateway. A functional runtime implementation is not yet available, and the requirements defined herein are subject to validation during the implementation phase.


The BIOrch Tool Gateway is the controlled boundary between BIOrch agents/orchestration logic and tools that can access repositories, files, parsers, metadata, or other external capabilities.

The Tool Gateway exists to ensure that agents do not receive unrestricted access to the underlying execution environment.

The gateway defines:

- which tools are available;
- what inputs those tools accept;
- what operations they are permitted to perform;
- what resources they may access;
- how requests are validated;
- how execution results are returned;
- how failures are represented;
- and what security and provenance guarantees apply.

The Tool Gateway is therefore a **runtime security and execution boundary**, not an agent itself.

---

## 2. Scope

This contract governs the runtime Tool Gateway used by BIOrch agents and orchestration components.

The contract applies to tool operations involving:

- repository inspection;
- filesystem access;
- BI workbook/project parsing;
- metadata extraction;
- deterministic analysis;
- future Tableau tooling;
- future Power BI tooling;
- and other explicitly registered BIOrch capabilities.

The contract does not define the internal implementation technology.

The implementation may use Python libraries, custom code, an agent framework, an MCP-based mechanism, or another technology provided that the implementation satisfies this contract.

---

## 3. Non-Goals

The Tool Gateway MUST NOT become responsible for:

- deciding which business question the user should ask;
- independently planning multi-agent workflows;
- selecting the final BI analysis strategy;
- implementing Tableau or Power BI parsing logic;
- replacing the Repository Agent;
- replacing the Deterministic Orchestrator;
- performing unrestricted operating-system access;
- or becoming a general-purpose shell execution interface.

Agent reasoning and orchestration remain separate responsibilities.

---

## 4. Architectural Position

The intended runtime relationship is:

```text
User Request
     |
     v
Orchestrator
     |
     +----------------------+
     |                      |
     v                      v
Repository Agent       BI Agents
     |                /          \
     |               /            \
     +--------------+--------------+
                    |
                    v
              Tool Gateway
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
   Repository    Parsers     Approved
    Tools         Tools       Tools
````

Agents and orchestration components MUST interact with protected runtime capabilities through the Tool Gateway where those capabilities are governed by this contract.

---

## 5. Core Principles

The implementation MUST follow these principles.

### 5.1 Explicit Tool Registration

A tool MUST be explicitly registered before it can be invoked through the gateway.

Unknown or unregistered tools MUST NOT be executable.

### 5.2 Least Privilege

Each registered tool MUST expose only the minimum capabilities required for its purpose.

### 5.3 Explicit Resource Boundaries

A tool MUST operate only on resources that it is authorized to access.

### 5.4 Deterministic Validation

Tool requests MUST be validated before execution.

Validation MUST NOT depend solely on an LLM deciding that an operation is safe.

### 5.5 No Arbitrary Execution

The gateway MUST NOT provide unrestricted shell, Python, operating-system, or equivalent execution to agents.

If an operational capability is required, it MUST be exposed as a specifically registered and constrained tool.

### 5.6 Fail Closed

When a request cannot be validated safely, the gateway MUST reject the request rather than execute it with relaxed restrictions.

---

## 6. Tool Registration Contract

Every tool exposed by the gateway MUST have a registered definition containing, at minimum:

* unique tool identifier;
* human-readable name;
* purpose;
* version;
* input schema;
* output schema;
* allowed resources;
* permitted operations;
* security classification;
* failure behavior;
* and ownership information.

A conceptual registration MUST resemble:

```text
Tool
├── id
├── name
├── version
├── purpose
├── input_schema
├── output_schema
├── resource_policy
├── operation_policy
├── security_classification
├── failure_policy
└── owner
```

The exact implementation representation is intentionally left to the implementation phase.

---

## 7. Tool Invocation Contract

A tool invocation MUST contain sufficient information for the gateway to determine:

1. which tool is being requested;
2. which version is requested;
3. what inputs are supplied;
4. which resource is being accessed;
5. what operation is requested;
6. and the execution context necessary for authorization.

The gateway MUST validate the invocation before execution.

Conceptually:

```text
Agent
  |
  | Tool Request
  v
Tool Gateway
  |
  +--> Tool exists?
  |
  +--> Input valid?
  |
  +--> Resource allowed?
  |
  +--> Operation allowed?
  |
  +--> Security policy satisfied?
  |
  +--> Execute
  |
  v
Tool Result
```

---

## 8. Input Validation

Tool inputs MUST be validated against the registered input contract before execution.

Validation MUST include, where applicable:

* required fields;
* data types;
* allowed values;
* path/resource constraints;
* size limits;
* operation restrictions;
* and other tool-specific safety constraints.

Malformed requests MUST be rejected.

The gateway MUST NOT silently transform an unsafe request into a different request merely to make execution succeed.

---

## 9. Resource Access Policy

Resource access MUST be explicitly bounded.

For repository and filesystem tools, the gateway MUST support restrictions such as:

* allowed root directories;
* allowed file types;
* allowed operations;
* read/write permissions;
* path traversal protection;
* and resource existence validation.

An agent MUST NOT be able to escape the authorized resource boundary through path manipulation or equivalent mechanisms.

For example:

```text
Allowed:
  /workspace/project/sample/

Denied:
  /etc/
  /home/other-user/
  arbitrary filesystem locations
```

The exact runtime paths are implementation-specific.

---

## 10. Operation Policy

Every tool MUST explicitly define the operations it supports.

For example, a repository inspection tool might support:

```text
READ_FILE
LIST_DIRECTORY
INSPECT_METADATA
```

but not:

```text
DELETE_FILE
EXECUTE_SHELL
MODIFY_SYSTEM
```

Operations not explicitly permitted by a tool definition MUST be rejected.

---

## 11. Read and Write Separation

Where a capability supports both read and write operations, the permissions MUST be explicitly separated.

Read access MUST NOT implicitly grant write access.

Write operations SHOULD require stronger authorization than read-only operations.

The gateway MUST NOT assume that an agent is authorized to modify a resource simply because the agent can read it.

---

## 12. Shell and Code Execution

The Tool Gateway MUST NOT expose unrestricted shell or arbitrary code execution as a general-purpose agent capability.

If shell or code execution is required for a specific future tool, it MUST:

* be explicitly registered;
* have a narrowly defined purpose;
* restrict the executable operations;
* restrict accessible resources;
* validate arguments;
* enforce execution limits;
* and return structured results.

An implementation MUST NOT create a generic:

```text
run_any_command(command)
```

capability for unrestricted agent use.

---

## 13. BI Parser Tool Boundary

Tableau and Power BI parsing capabilities MUST be exposed as controlled tools.

The Tool Gateway is responsible for controlling access to these capabilities.

The actual parsing logic belongs to the appropriate BI parser/agent implementation.

For example:

```text
Tool Gateway
      |
      +--> Tableau Parser Tool
      |
      +--> Power BI Parser Tool
```

The gateway MUST NOT contain the complete Tableau or Power BI parsing implementation.

---

## 14. Tool Result Contract

Tool results MUST be returned in a structured form.

A result SHOULD communicate at minimum:

* success or failure;
* tool identifier;
* tool version;
* result payload;
* error information when applicable;
* and relevant execution/provenance metadata.

Conceptually:

```text
ToolResult
├── status
├── tool_id
├── tool_version
├── data
├── error
└── provenance
```

The exact serialization format is an implementation decision.

---

## 15. Error Handling

The gateway MUST distinguish at least between:

* invalid request;
* unknown tool;
* unauthorized operation;
* unauthorized resource;
* validation failure;
* execution failure;
* timeout;
* and internal gateway failure.

Errors MUST be explicit.

The gateway MUST NOT report successful execution when the underlying tool failed.

Errors SHOULD contain enough structured information for the orchestrator to make a subsequent deterministic decision without exposing sensitive implementation details unnecessarily.

---

## 16. Timeout and Resource Controls

Tool execution SHOULD be bounded by appropriate resource controls, including where applicable:

* execution timeout;
* input size;
* output size;
* memory limits;
* concurrency limits;
* and other tool-specific resource constraints.

A tool that exceeds its permitted execution boundary MUST terminate or fail according to its defined failure policy.

---

## 17. Security Boundary

The Tool Gateway is a security boundary.

Agents MUST NOT be trusted to enforce the gateway's security rules themselves.

Security decisions MUST be enforced by deterministic gateway logic.

The gateway MUST therefore treat agent-provided:

* paths;
* commands;
* tool identifiers;
* resource identifiers;
* operation names;
* and other security-sensitive inputs

as untrusted input.

---

## 18. Provenance and Auditability

Where practical, tool invocation SHOULD produce sufficient provenance information to establish:

* which tool was invoked;
* which version was invoked;
* what resource was targeted;
* when execution occurred;
* whether execution succeeded;
* and what result was produced.

The provenance mechanism MUST NOT expose secrets or sensitive credentials.

Detailed audit-storage architecture is deferred to the implementation and later governance phases.

---

## 19. Secrets and Credentials

Tool implementations MUST NOT expose secrets or credentials to agents unless explicitly required and separately governed.

Secrets MUST NOT be:

* embedded in tool definitions;
* returned as normal tool output;
* written into logs;
* or included in provenance records.

Credential management is outside the Tool Gateway contract and MUST use an appropriate secure mechanism.

---

## 20. Determinism

Security and authorization decisions MUST be deterministic.

An LLM MAY assist an upstream component in deciding which tool to request, but the Tool Gateway MUST independently determine whether that requested operation is permitted.

Conceptually:

```text
LLM decision:
    "I want to call Tool X"

        ↓

Tool Gateway:
    "Is Tool X registered?"
    "Are these inputs valid?"
    "Is this resource allowed?"
    "Is this operation permitted?"

        ↓

ALLOW / DENY
```

The gateway MUST NOT delegate the final security decision to an LLM.

---

## 21. Framework Independence

This contract intentionally does not mandate:

* CrewAI;
* LangChain;
* LangGraph;
* Gemini CLI;
* Gemini subagents;
* MCP;
* a custom agent framework;
* or any other orchestration framework.

A future implementation may adopt one of these technologies if it can satisfy this contract.

Framework selection is therefore an implementation/architecture decision and not part of this contract.

---

## 22. Extensibility

The gateway MUST be designed so that additional tools can be registered without redesigning the entire gateway.

Future tools may include:

* Tableau metadata extraction;
* Power BI semantic-model extraction;
* workbook inspection;
* repository metadata inspection;
* lineage analysis;
* comparison tools;
* validation tools;
* and analysis-oriented tools.

Adding a tool MUST NOT bypass the gateway's validation and authorization mechanisms.

---

## 23. Responsibilities

### Tool Gateway is responsible for

* tool registration;
* request validation;
* authorization;
* resource boundaries;
* operation restrictions;
* execution policy;
* structured results;
* error handling;
* security enforcement;
* and applicable provenance.

### Tool Gateway is NOT responsible for

* agent reasoning;
* user intent interpretation;
* workflow planning;
* multi-agent coordination;
* Tableau parsing logic;
* Power BI parsing logic;
* business analysis;
* or final user-facing conclusions.

---

## 24. Relationship to Other BIOrch Components

The Tool Gateway is one component of the broader BIOrch architecture.

The intended progression is:

```text
Phase 2
Tool Gateway
      ↓
Phase 3
Repository Agent
      ↓
Phase 4
Deterministic Orchestrator
      ↓
Phase 5
Multiple Agents
      ↓
Phase 6+
Tableau + Power BI
```

The contracts for those future components are intentionally separate.

This contract MUST NOT define their complete behavior.

---

## 25. Implementation Conformance

An implementation conforms to this contract only when it demonstrably satisfies the mandatory requirements defined above.

At minimum, implementation review MUST verify:

* registered tools cannot be bypassed;
* unknown tools are rejected;
* inputs are validated;
* unauthorized resources are rejected;
* unauthorized operations are rejected;
* unrestricted shell execution is not exposed;
* security decisions do not depend solely on an LLM;
* failures are represented correctly;
* tool results are structured;
* and the gateway enforces its security boundary independently of agent reasoning.

Implementation-specific tests and acceptance criteria will be maintained separately from this contract.

---

## 26. Versioning

Contract changes MUST be version-controlled.

Changes that alter:

* security boundaries;
* authorization behavior;
* tool invocation semantics;
* resource access rules;
* or mandatory conformance requirements

MUST result in an explicit contract version change.

The contract manager and review process MUST preserve human approval for substantive contract changes.

---

## 27. Current State

**Contract:** Defined
**Implementation:** Not yet complete
**Phase:** Phase 2
**Framework:** Not selected
**Runtime agents:** Not yet implemented
**Tableau Agent:** Future phase
**Power BI Agent:** Future phase

This contract defines the target behavior of the Tool Gateway. It does not claim that the current repository implementation already satisfies the contract.

---

## 28. Acceptance Gate for Phase 2

Phase 2 SHOULD NOT be considered complete merely because this document exists.

Phase 2 completion requires:

1. Tool Gateway implementation exists.
2. Registered tools are explicitly defined.
3. Input validation is implemented.
4. Resource boundaries are enforced.
5. Operation authorization is enforced.
6. Arbitrary execution is prevented.
7. Structured tool results are implemented.
8. Error handling is implemented.
9. Security decisions are deterministic.
10. Automated tests demonstrate the required security boundaries.
11. `/biorch-review` verifies implementation against this contract.
12. Governance documentation records the resulting Phase 2 status.

---

## 29. Contract Ownership

**Canonical Location:**

```text
contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md
```

This file is the canonical Tool Gateway runtime contract.

Development tasks, Gemini CLI commands, implementation files, and review reports MUST NOT silently redefine the requirements in this document.

If implementation requirements change, this contract MUST be explicitly updated through the project's contract-management process.
