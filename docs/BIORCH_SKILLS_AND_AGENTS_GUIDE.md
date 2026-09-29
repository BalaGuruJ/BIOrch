# BIOrch — Skills, Commands, and Agents Guide

## Purpose

This document explains the custom Gemini CLI skills, Gemini commands, and runtime agents currently present in BIOrch.

A critical distinction:

> **BIOrch has three different concepts that are easy to confuse:**
>
> 1. **Gemini CLI Skills** — reusable procedural instructions for the development assistant.
> 2. **Gemini CLI Commands** — slash commands that start governed development workflows.
> 3. **BIOrch Runtime Agents** — Python components that will eventually perform BI/repository work at runtime.

The first two are **development infrastructure**. They are not the multi-agent runtime itself.

---

# 1. Current inventory

Based on the current repository snapshot:

| Category | Count | Location |
|---|---:|---|
| Gemini CLI Skills | 12 | `.agents/skills/` |
| Gemini CLI Commands | 10 | `.gemini/commands/` |
| Implemented runtime agent executor | 1 | `src/biorch/agents/deterministic_agent.py` |
| Runtime agent model | 1 | `src/biorch/core/agent.py` |
| Planned domain agents | Several | Contracts/docs only; not implemented |

---

# 2. The most important distinction

## 2.1 Gemini Skill

A skill is a **procedure/instruction set** that tells Gemini how to perform a type of development task.

Example:

```text
.agents/skills/biorch-review/SKILL.md
```

This does not create a BIOrch runtime agent.

It teaches Gemini:

> "When reviewing BIOrch work, follow these review rules."

Think of a skill as a **Standard Operating Procedure (SOP)**.

---

## 2.2 Gemini Command

A command is a **user-facing entry point** defined under:

```text
.gemini/commands/
```

For example:

```text
/biorch-review
/biorch-task
/biorch-next
```

The command contains a prompt/workflow telling Gemini what to inspect, what approvals to request, and what mutations are allowed.

Think of a command as a **button/operation that starts a governed workflow**.

---

## 2.3 BIOrch Runtime Agent

A runtime agent is actual Python application code.

The currently implemented executor is:

```text
src/biorch/agents/deterministic_agent.py
```

It uses:

```text
Agent
  ↓
Task
  ↓
DeterministicAgentExecutor
  ↓
ToolGateway
  ↓
Tool
  ↓
Result
```

This is part of the BIOrch product architecture.

It is NOT the same thing as `.agents/skills/`.

---

# 3. Current Gemini CLI Skills

## 3.1 `biorch-bi-inventory`

**Purpose:** Inspect Tableau/Power BI artifacts and establish what objects exist before downstream analysis.

**Use when:**
- inspecting `.twb` / `.twbx`
- inspecting Power BI PBIP/TMDL artifacts
- inventorying BI metadata
- determining available objects before routing work

**Does not mean:** Implementing a BI parser.

---

## 3.2 `biorch-contract-review`

**Purpose:** Review BIOrch schemas/core contracts for architectural consistency.

**Use when:**
- changing `schemas/`
- changing `src/biorch/core/`
- evaluating whether a proposed model change violates architecture

**Key principle:** Contracts remain authoritative.

---

## 3.3 `biorch-implementation`

**Purpose:** Execute a bounded implementation task without uncontrolled refactoring.

**Use when:**
- an approved `TASK.md` exists
- code changes are explicitly authorized
- tests need to be added/updated

**Key principle:** Implement the approved scope; do not silently expand it.

---

## 3.4 `biorch-investigation`

**Purpose:** Perform a read-only technical investigation.

**Use when:**
- you are unsure how the repository currently works
- investigating architecture
- investigating security
- evaluating parsers/integrations
- looking for discrepancies before changing code

**Key principle:** Investigation comes before implementation when the current state is uncertain.

---

## 3.5 `biorch-next`

**Purpose:** Determine the next permitted governance action.

**Use when:**

```text
What should I do next?
```

It checks the authoritative phase state and evidence.

**It should not implement the next phase automatically.**

---

## 3.6 `biorch-phase-closure`

**Purpose:** Determine whether a phase has sufficient evidence for closure.

**Use after:**
- implementation
- validation
- independent review

It evaluates whether the phase is ready to move toward closure.

---

## 3.7 `biorch-review`

**Purpose:** Perform an independent architectural/contract review.

**Use when:**
- reviewing a completed implementation
- reviewing a task
- checking security/architecture boundaries
- verifying tests and evidence

This was the skill used during the Phase 04 corrective review.

---

## 3.8 `biorch-status`

**Purpose:** Help establish current project status using the project state model.

**Use when:**
- checking phase state
- checking Git state
- checking environment/artifacts
- detecting documentation drift

---

## 3.9 `biorch-sync`

**Purpose:** Synchronize derived documentation with authoritative phase state.

**Use after a governed phase-state change**, when:

```text
PHASE_INDEX.md
```

has changed and derived documents may need updating.

It should not modify historical task/review evidence.

---

## 3.10 `biorch-task-record`

**Purpose:** Preserve task lifecycle traceability.

**Use when:**
- creating or maintaining task/response/review evidence
- ensuring work can be traced from objective to final decision

There is currently no corresponding `.gemini/commands/biorch-task-record.toml`; it is a skill rather than a slash command.

---

## 3.11 `biorch-task`

**Purpose:** Standardize creation of governed implementation/investigation tasks.

**Use when starting a new governed unit of work.**

Typical flow:

```text
Phase
  ↓
Contract
  ↓
/biorch-task
  ↓
TASK.md
```

---

## 3.12 `biorch-validation`

**Purpose:** Validate completed work against acceptance criteria and factual evidence.

**Use after implementation and before final review/closure.**

It should answer:

> Does the implementation actually work as specified?

---

# 4. Current Gemini CLI Commands

These are the slash commands currently defined in `.gemini/commands/`.

## `/biorch-task`

Starts a governed task proposal.

Use:

```text
/biorch-task <objective>
```

Typical result:

```text
PLANNED
   ↓
human approval
   ↓
IN_PROGRESS
```

It should not implement code itself.

---

## `/biorch-contract`

Two modes:

```text
/biorch-contract
```

Read/summary mode.

Or:

```text
/biorch-contract <change request>
```

Contract-change proposal mode.

Important:

> Contract modifications require explicit human approval.

---

## `/biorch-review`

Reviews the active phase/task/implementation and may propose:

```text
IN_PROGRESS
   ↓
READY_FOR_CLOSURE
```

It must obtain human approval for the state transition.

---

## `/biorch-close`

Performs the closure audit for a phase already marked:

```text
READY_FOR_CLOSURE
```

It verifies:

- TASK.md
- RESPONSE.md
- REVIEW.md
- PHASE_CLOSURE.md

Then asks for human approval before:

```text
READY_FOR_CLOSURE
   ↓
CLOSED
```

---

## `/biorch-next`

Answers:

```text
What is the next permitted governed action?
```

This is primarily a navigation/decision command.

It should not autonomously start the next phase.

---

## `/biorch-status`

Provides a read-only status report including:

- LAST_COMPLETED
- ACTIVE
- NEXT_PLANNED
- documentation drift
- Git status
- environment status
- BI sample availability

---

## `/biorch-sync`

Synchronizes derived documentation with authoritative phase state.

Typical relationship:

```text
PHASE_INDEX.md
      ↓
PROJECT_STATE.md
ROADMAP.md
README.md
```

Human approval is required before documentation modifications.

---

## `/biorch-git`

Provides a governed Git lifecycle:

```text
inspect
  ↓
inventory
  ↓
classify
  ↓
propose staging
  ↓
human approval
  ↓
stage
  ↓
verify staged diff
  ↓
human approval
  ↓
commit
  ↓
verify
  ↓
push proposal
  ↓
human approval
  ↓
push
```

This is the command to use instead of casually running:

```text
git add .
git commit
git push
```

---

## `/biorch-roadmap`

Inspects or proposes changes to:

```text
docs/ROADMAP.md
```

Roadmap changes require human approval.

---

## `/biorch-governance`

Performs a read-only governance alignment audit.

Use when asking:

> Does the governance documentation actually match repository reality?

It should not modify files.

---

# 5. Recommended command workflow

For a normal new phase:

```text
/biorch-next
      ↓
/biorch-contract
      ↓
/biorch-task
      ↓
TASK REVIEW
      ↓
IMPLEMENTATION
      ↓
/biorch-validation
      ↓
/biorch-review
      ↓
/biorch-close
      ↓
/biorch-sync
      ↓
/biorch-next
```

Not every command is required every time.

For example:

- `/biorch-roadmap` is only needed when the roadmap changes.
- `/biorch-contract` is needed when contracts are created/reviewed/changed.
- `/biorch-sync` is needed when derived documentation must be reconciled.
- `/biorch-git` is used when you want governed Git operations.

---

# 6. What runtime agents actually exist today?

This is where the terminology becomes important.

## Implemented

### DeterministicAgentExecutor

Location:

```text
src/biorch/agents/deterministic_agent.py
```

This is currently the actual executable agent component.

Its responsibility is bounded:

```text
Task
 ↓
validate agent identity
 ↓
validate required inputs
 ↓
validate allowed tool
 ↓
ToolGateway.invoke()
 ↓
Result
```

It is deterministic and does not perform LLM planning.

---

# 7. Agent model vs agent implementation

`src/biorch/core/agent.py` contains the **Agent data model**.

It describes things such as:

- `agent_id`
- `name`
- `role`
- `capabilities`
- `allowed_tools`
- `supported_operations`
- `provider_info`

That does NOT mean each described agent exists as executable code.

It is a contract/model.

---

# 8. Planned domain agents

The architecture currently describes future specialized agents such as:

```text
RepositoryAgent
TableauAgent
PowerBIAgent
ReviewAgent
ReportAgent
```

These should currently be treated as **architectural targets/planned roles**, not as implemented runtime agents.

The current phase index confirms that Multiple Agents is the next major runtime expansion after Phase 04.

---

# 9. Important terminology map

| What you see | What it really is |
|---|---|
| `.agents/skills/` | Gemini development procedures |
| `.gemini/commands/` | Gemini slash-command workflows |
| `src/biorch/core/agent.py` | Runtime Agent data model |
| `src/biorch/agents/deterministic_agent.py` | Actual runtime agent executor |
| `src/biorch/orchestration/` | Runtime orchestration implementation |
| `contracts/` | Runtime architectural contracts |
| `governance/` | Development governance/evidence |
| `docs/` | Project architecture/process documentation |

---

# 10. How you should use them

You do NOT need to manually activate every skill.

For normal work, describe your objective clearly.

For example:

```text
I want to investigate whether the current Phase 05 design is complete.
Do a read-only investigation and do not modify files.
```

Gemini can use:

```text
biorch-investigation
```

For implementation:

```text
I have an approved TASK.md. Implement only the defined scope,
run the required tests, and provide evidence.
```

Use:

```text
biorch-implementation
```

For review:

```text
Review the completed implementation against the canonical contract,
TASK.md, security boundaries, and test evidence. Do not modify code.
```

Use:

```text
biorch-review
```

For artifact inspection:

```text
Inspect the Tableau/Power BI sample and inventory its metadata.
Do not implement parser logic.
```

Use:

```text
biorch-bi-inventory
```

For deciding what to do next:

```text
/biorch-next
```

For governed Git:

```text
/biorch-git
```

---

# 11. What should NOT be confused

Do not think:

```text
biorch-bi-inventory
        =
TableauAgent
```

It does not.

Instead:

```text
biorch-bi-inventory
        =
Gemini procedure for inspecting BI artifacts
```

while eventually:

```text
TableauAgent
        =
BIOrch runtime agent responsible for Tableau capabilities
```

Similarly:

```text
biorch-review
        ≠
ReviewAgent
```

The first is a Gemini development skill.

The second is a planned BIOrch runtime role.

---

# 12. Current architecture in one picture

```text
                 DEVELOPMENT TIME
                 ================

Human
  │
  ├── /biorch-task
  ├── /biorch-review
  ├── /biorch-close
  ├── /biorch-next
  └── /biorch-git
          │
          ▼
     Gemini CLI
          │
          └── .agents/skills/
                ├── investigation
                ├── implementation
                ├── validation
                ├── review
                ├── BI inventory
                └── governance procedures


                 RUNTIME
                 =======

User Request
     │
     ▼
Deterministic Orchestrator
     │
     ▼
Runtime Agent
     │
     ▼
Tool Gateway
     │
     ▼
Tools / Domain Engines
     │
     ├── Tableau / TabUI
     └── Power BI / PBIParser
```

The two layers are deliberately separate.

---

# 13. Recommended mental model

When you are working on the repository, remember:

### Skills = HOW Gemini works

### Commands = HOW you start governed Gemini workflows

### Agents = WHAT BIOrch executes at runtime

### Tools = WHAT agents are allowed to invoke

### Contracts = RULES that everything must obey

### Governance = EVIDENCE and approval history

This distinction should prevent most of the confusion around the current project structure.

---

# 14. Current recommended usage

For your current BIOrch workflow, the safest pattern is:

```text
1. /biorch-status
2. /biorch-next
3. Read/review the applicable contract
4. Create an explicit task
5. Investigate first if the design is uncertain
6. Implement only the approved scope
7. Validate with tests
8. Independently review
9. Close only after evidence is sufficient
10. Synchronize documentation
11. Use /biorch-git for controlled Git operations
```

The project should not treat the Gemini development skills as part of the BIOrch production runtime architecture.
