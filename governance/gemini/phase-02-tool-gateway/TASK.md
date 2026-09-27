# TASK: Phase 02 - Tool Gateway Implementation

**Task ID:** PHASE-02-IMPLEMENTATION

**Phase:** 02 - Tool Gateway

**Status:** DRAFT

**Contract:** `BIORCH-TG-001`

**Canonical Contract:**
`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

---

## 1. Objective

Implement the BIOrch Tool Gateway as the deterministic runtime security and execution boundary defined by the canonical Tool Gateway Contract.

The implementation MUST enforce the contract independently of agent or LLM reasoning and MUST fail closed whenever a tool invocation cannot be deterministically validated and authorized.

The implementation must establish the foundation required for later BIOrch components to safely invoke governed tools.

---

## 2. Source of Truth

The canonical source of requirements for this implementation is:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

The implementation MUST NOT redefine, weaken, or silently reinterpret mandatory requirements in the contract.

If an implementation detail is not specified by the contract, inspect the existing repository architecture and choose the smallest appropriate implementation consistent with the current project.

Do not modify the canonical contract as part of this task.

---

## 3. Repository Inspection Before Implementation

Before modifying source code, inspect the existing repository to determine:

- existing Tool models;
- existing Result models;
- existing schemas;
- existing package/module structure;
- existing validation utilities;
- existing error-handling patterns;
- existing test structure;
- existing orchestration/core boundaries;
- existing configuration patterns.

The implementation location MUST be selected based on the existing repository architecture.

Do NOT assume that the gateway belongs in a particular directory before inspection.

Document the selected implementation modules in the implementation changes.

---

## 4. Scope

Implement the minimum runtime functionality necessary to satisfy the canonical Tool Gateway Contract.

The implementation MUST include:

### 4.1 Tool Registration

Implement deterministic registration of explicitly approved tools.

Each registered tool MUST provide the contract-required information, including where applicable:

- unique identifier;
- name;
- version;
- purpose;
- input schema;
- output schema;
- allowed resources;
- permitted operations;
- security classification;
- failure behavior;
- ownership information.

Unknown or unregistered tools MUST NOT be executable.

---

### 4.2 Tool Invocation

Implement a controlled gateway entry point for tool invocation.

An invocation MUST contain sufficient information to determine:

- requested tool;
- requested version;
- supplied inputs;
- targeted resource;
- requested operation;
- execution context required for authorization.

The gateway MUST validate the invocation before execution.

---

### 4.3 Deterministic Input Validation

Validate tool inputs against the registered tool contract.

Where applicable, validation MUST cover:

- required fields;
- data types;
- allowed values;
- resource/path constraints;
- size limits;
- operation restrictions;
- tool-specific safety constraints.

Malformed requests MUST be rejected.

The gateway MUST NOT silently transform an unsafe request into a different request merely to make execution succeed.

---

### 4.4 Resource Authorization

Implement explicit resource authorization.

For filesystem/repository-oriented tools, enforce appropriate boundaries such as:

- allowed root directories;
- allowed file types where applicable;
- allowed operations;
- read/write permissions;
- path traversal protection;
- resource existence validation.

Path manipulation MUST NOT allow an invocation to escape its authorized resource boundary.

---

### 4.5 Operation Authorization

Every registered tool MUST explicitly define the operations it supports.

Operations not explicitly permitted by the tool definition MUST be rejected.

Read access MUST NOT implicitly grant write access.

Where both read and write operations exist, they MUST be explicitly separated.

---

### 4.6 Fail-Closed Enforcement

The gateway MUST reject a request whenever required validation or authorization cannot be satisfied.

Examples include:

- unknown tool;
- unknown tool version;
- malformed input;
- invalid resource;
- unauthorized resource;
- unauthorized operation;
- missing policy;
- invalid execution context;
- unsupported operation;
- security-policy failure.

The gateway MUST NOT relax security restrictions to make a request succeed.

---

### 4.7 Execution Boundary

Implement controlled execution of registered tools.

The gateway MUST NOT expose unrestricted:

- shell execution;
- Python execution;
- operating-system execution;
- arbitrary command execution;
- equivalent generic execution capabilities.

If execution of a registered tool requires an underlying callable, the callable MUST be reached only through the registered and authorized tool definition.

---

### 4.8 Structured Results

Implement the structured ToolResult behavior defined by the contract.

Results MUST communicate, as applicable:

- success/failure status;
- tool identifier;
- tool version;
- result payload;
- structured error information;
- provenance metadata.

The gateway MUST NOT report successful execution when the underlying tool failed.

---

### 4.9 Error Handling

Implement explicit error categories for at least:

- invalid request;
- unknown tool;
- unauthorized operation;
- unauthorized resource;
- validation failure;
- execution failure;
- timeout;
- internal gateway failure.

Errors MUST be structured and deterministic.

Errors MUST NOT expose secrets or unnecessary sensitive implementation details.

---

### 4.10 Execution Limits

Implement appropriate execution controls supported by the existing repository architecture.

At minimum, determine how the gateway will enforce or represent:

- execution timeout;
- input size limits;
- output size limits where applicable;
- concurrency/resource limits where applicable.

If a contract requirement is intentionally deferred because the current architecture does not yet support it, document the limitation explicitly rather than silently omitting it.

---

### 4.11 Provenance

Implement the minimum provenance necessary to establish, where practical:

- tool invoked;
- tool version;
- targeted resource;
- execution occurrence/time;
- success/failure;
- result relationship.

Do not expose secrets or credentials through provenance.

Detailed durable audit-storage architecture is outside this phase unless already supported by the repository.

---

### 4.12 Secrets and Credentials

Do not introduce hard-coded credentials or secrets.

Do not expose credentials through:

- tool definitions;
- ToolResult payloads;
- error messages;
- logs;
- provenance records.

Do not implement a new credential-management system as part of this task.

---

## 5. BI Parser Boundary

Do NOT implement Tableau or Power BI parsing logic in this phase.

The Tool Gateway may establish the controlled interface required for future parser tools, but actual:

- Tableau parsing;
- Power BI parsing;
- semantic-model extraction;
- workbook parsing;
- lineage analysis;

remain outside Phase 2.

Future BI parser capabilities MUST be exposed through the Tool Gateway rather than bypassing it.

---

## 6. Architectural Separation

The Tool Gateway MUST remain separate from:

- agent reasoning;
- user-intent interpretation;
- workflow planning;
- multi-agent coordination;
- Tableau parsing;
- Power BI parsing;
- business analysis;
- final user-facing conclusions.

The gateway is a security and execution boundary, not an agent.

Security and authorization decisions MUST be deterministic and MUST NOT depend solely on an LLM.

---

## 7. Framework Constraints

Do NOT introduce:

- CrewAI;
- LangChain;
- LangGraph;
- Gemini subagents;
- MCP;
- another external agent framework;

unless an existing repository dependency already requires it or the contract is explicitly changed through the contract-management process.

Phase 2 is framework-independent.

Use the existing repository architecture and dependencies wherever practical.

---

## 8. Implementation Steps

1. Inspect the existing repository architecture and identify the appropriate gateway location.
2. Inspect and reuse existing Tool/Result/schema models where appropriate.
3. Define or extend the Tool registration model.
4. Implement deterministic ToolRegistry behavior.
5. Implement invocation validation.
6. Implement input validation.
7. Implement resource authorization.
8. Implement operation authorization.
9. Implement fail-closed enforcement.
10. Implement controlled execution of registered tools.
11. Implement structured ToolResult and error handling.
12. Implement applicable timeout/resource controls.
13. Implement minimum required provenance.
14. Add safe representative tools for testing where necessary.
15. Add comprehensive unit and integration tests.
16. Verify implementation against every mandatory requirement of `BIORCH-TG-001`.

---

## 9. Testing Requirements

Tests MUST demonstrate the security boundary rather than only the happy path.

At minimum, tests MUST cover:

### Registration

- valid tool registration;
- duplicate tool rejection;
- unknown tool rejection;
- invalid tool definition rejection.

### Invocation

- valid authorized invocation;
- unknown tool;
- unknown version;
- malformed request;
- invalid input;
- unsupported operation.

### Resource Security

- authorized resource;
- unauthorized resource;
- path traversal attempt;
- resource outside the configured boundary;
- invalid/nonexistent resource where applicable.

### Operation Security

- explicitly permitted operation;
- unauthorized operation;
- read/write separation;
- operation not present in tool policy.

### Fail-Closed Behavior

- missing policy;
- invalid policy;
- ambiguous authorization;
- validation failure;
- execution failure;
- timeout.

Every security failure MUST result in rejection or the contract-defined failure behavior.

### Execution

- successful registered tool execution;
- failed tool execution;
- structured result generation;
- structured error generation.

### Security Boundary

Tests MUST demonstrate that the gateway does NOT expose unrestricted arbitrary shell/code execution.

### Provenance

Tests SHOULD verify that required provenance fields are produced without exposing secrets.

---

## 10. Acceptance Criteria

Phase 2 implementation is acceptable only when all applicable criteria below are satisfied:

- [ ] Implementation conforms to `BIORCH-TG-001`.
- [ ] Tool registration is explicit and deterministic.
- [ ] Unknown/unregistered tools are rejected.
- [ ] Tool versions are handled deterministically.
- [ ] Inputs are validated before execution.
- [ ] Resources are explicitly authorized.
- [ ] Path/resource boundaries are enforced.
- [ ] Operations are explicitly authorized.
- [ ] Read/write permissions are separated.
- [ ] Security decisions do not depend on an LLM.
- [ ] Gateway behavior fails closed.
- [ ] Unrestricted shell/arbitrary code execution is not exposed.
- [ ] Registered tools can execute only after authorization.
- [ ] Tool results are structured.
- [ ] Required error categories are represented.
- [ ] Execution failures are not reported as successful results.
- [ ] Applicable timeout/resource controls are enforced or explicitly documented.
- [ ] Minimum required provenance is supported.
- [ ] Secrets are not exposed through results, errors, logs, or provenance.
- [ ] Automated tests cover the mandatory security boundaries.
- [ ] Tableau/Power BI parsing remains outside the gateway implementation.
- [ ] Gateway responsibilities remain separated from agent reasoning and orchestration.
- [ ] `/biorch-review` verifies the implementation against the canonical contract.

---

## 11. Explicit Non-Goals

This task MUST NOT:

- implement Tableau parsing;
- implement Power BI parsing;
- implement the Repository Agent;
- implement the Deterministic Orchestrator;
- implement multiple BI agents;
- implement LLM planning;
- implement review loops;
- implement Tableau ↔ Power BI comparison;
- implement analysis-ready output;
- select an external agent framework;
- modify the canonical Tool Gateway contract;
- create a generic unrestricted shell/code execution interface;
- create a second Tool Gateway contract;
- create a second roadmap;
- perform Git commits, pushes, or other Git mutations.

---

## 12. Dependencies

### Required

Canonical contract:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

Existing repository models, schemas, and test infrastructure MUST be inspected and reused where appropriate.

### Future Dependencies

Future BI agents and orchestration components will depend on the Tool Gateway.

Those components are NOT part of this task.

---

## 13. Contract Traceability

The implementation and tests MUST be traceable to the mandatory requirements in:

`contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`

Before considering the implementation complete, verify at minimum:

- Tool registration
- Tool invocation
- Input validation
- Resource authorization
- Operation authorization
- Read/write separation
- No arbitrary execution
- Structured results
- Error handling
- Timeout/resource controls
- Security boundary
- Provenance
- Secrets protection
- Deterministic authorization
- Framework independence
- Extensibility

Any contract requirement that cannot be implemented in Phase 2 MUST be explicitly identified during review with the reason and proposed follow-up phase.

---

## 14. Required Review

After implementation:

1. Run the project's automated tests.
2. Run `/biorch-review`.
3. `/biorch-review` MUST evaluate the implementation against:
   `contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`
4. Review MUST identify any contract requirement that is:
   - implemented;
   - partially implemented;
   - missing;
   - contradicted;
   - or not verifiable.
5. Phase 2 MUST NOT be marked complete solely because the implementation code exists.

---

## 15. Completion Condition

Phase 2 is complete only when:

1. The Tool Gateway implementation exists.
2. Mandatory contract requirements are implemented.
3. Automated tests demonstrate the required behavior.
4. Security boundaries are demonstrated through negative tests.
5. `/biorch-review` confirms contract conformance.
6. Any remaining gaps are explicitly documented.
7. Governance status is updated through the project's governed workflow.

---

## 16. Status

**Current Status:** DRAFT

**Implementation:** NOT STARTED

**Contract:** DEFINED

**Contract ID:** BIORCH-TG-001

**Phase:** 02 - Tool Gateway