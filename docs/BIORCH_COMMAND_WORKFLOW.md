# BIOrch Command Workflow

## 1. Purpose

This document defines the standard sequence for using the BIOrch Gemini CLI
commands during development.

BIOrch development follows a governed lifecycle, tracked via the authoritative
governance index: `governance/gemini/PHASE_INDEX.md`.

## 2. Phase State Model

BIOrch development is organized into phases, each with a lifecycle state:

- **PLANNED**
- **IN_PROGRESS**
- **READY_FOR_CLOSURE**
- **CLOSED**

At any given time, the project state is summarized by three phase categories:

1. **LAST_COMPLETED**: The most recent phase that has transitioned to **CLOSED**.
2. **ACTIVE**: The phase currently in **IN_PROGRESS** or **READY_FOR_CLOSURE**.
3. **NEXT_PLANNED**: The phase currently in **PLANNED**.

The Gemini CLI commands provide controlled assistance based on this model,
while human approval remains the authority for important phase transitions and
contract changes.

---

# 3. Core Principle

A BIOrch phase should normally follow this lifecycle:

1. Understand the phase
2. Define or confirm the contract
3. Create the implementation/investigation task
4. Review the task
5. Implement the task
6. Review the implementation
7. Prepare phase closure
8. Human approves closure
9. Synchronize project state
10. Determine the next governed action

Do not skip directly from a contract to implementation.

---

# 3. Command Roles

## /biorch-contract

### Purpose

Manage and inspect canonical architecture contracts.

### Use when

- Creating a new contract
- Reading an existing contract
- Reviewing a contract
- Proposing a contract modification
- Applying an explicitly approved contract change

### Canonical contract location

Contracts are stored under:

contracts/

Example:

contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md

### Important rule

The contract is the authoritative architectural requirement.

Implementation code must not silently redefine the contract.

---

# 4. /biorch-task

### Purpose

Create a governed implementation or investigation task from the
ACTIVE phase requirements and canonical contract.

### Typical use

After a phase contract exists:

    /biorch-task

The command should inspect the relevant governance and contract material
and create the appropriate TASK.md artifact.

Example:

governance/gemini/phase-02-tool-gateway/TASK.md

### Important rule

The task translates the contract into actionable implementation or
investigation work.

The task does not replace the contract.

---

# 5. Task Review

## /biorch-review

### Purpose

Independently review the task or implementation against the applicable
contract and governance requirements.

### First review

After creating TASK.md:

    /biorch-review

The purpose is to determine whether the task itself is sufficiently
aligned with the contract before implementation begins.

Example:

Contract
    ↓
TASK.md
    ↓
/biorch-review
    ↓
Task APPROVED

### Second review

After implementation:

    /biorch-review

The command should review the actual implementation against:

- canonical contract
- TASK.md
- security requirements
- tests
- architectural boundaries

Example:

Implementation
    ↓
/biorch-review
    ↓
Implementation APPROVED

### Important rule

"Review" does not mean "implement."

The review should identify whether the current artifact satisfies the
requirements.

---

# 6. Implementation

Implementation is performed only after the task is sufficiently defined
and reviewed.

The implementation may be performed by Gemini CLI or another development
workflow.

Example:

Contract
    ↓
Task
    ↓
Task Review
    ↓
Implementation
    ↓
Tests
    ↓
Implementation Review

The implementation must remain within the scope defined by the task and
contract.

---

# 7. Phase Closure

After implementation and implementation review are complete, the phase
requires a closure decision.

The closure artifact should record:

- implementation completed
- tests completed
- review completed
- known gaps
- contract conformance
- closure recommendation

Example:

governance/gemini/phase-02-tool-gateway/PHASE_CLOSURE.md

Typical state:

READY_FOR_CLOSURE

This does not automatically mean the phase is closed.

Human approval is required.

---

# 8. /biorch-next

### Purpose

Determine the next governed action.

This is the command to use when asking:

"What am I allowed or expected to do next?"

Example:

    /biorch-next

It should inspect:

- phase state (LAST_COMPLETED, ACTIVE, NEXT_PLANNED)
- phase status
- contracts
- tasks
- reviews
- closure artifacts
- governance state
- roadmap

and determine the next permitted action.

### Example

If Phase 02 has:

- implementation complete
- tests passed
- implementation review approved
- PHASE_CLOSURE.md = READY_FOR_CLOSURE

then:

    /biorch-next

may report:

    Phase 02 requires human closure approval.

After human approval:

    Phase 02 → CLOSED

and the next governed phase becomes:

    Phase 03

### Important rule

`/biorch-next` is a decision/navigation command.

It should not automatically begin implementation of the next phase.

---

# 9. /biorch-status

### Purpose

Synchronize project-state documentation with the actual governed state.

It may update:

    docs/PROJECT_STATE.md

and related governance state.

It can also propose a Git synchronization/commit.

### Typical use

After an important state transition such as:

    Phase 02 → CLOSED

run:

    /biorch-status

Then inspect the proposed changes.

### Important rule

Review proposed Git changes before approving synchronization.

Do not blindly approve a commit simply because the status command
proposes one.

---

# 10. /biorch-governance

### Purpose

Inspect or work with the project's governance structure.

Use this when:

- checking governance rules
- examining phase governance
- investigating governance artifacts
- validating the governance structure

This is a supporting command rather than the normal implementation
sequence.

---

# 11. /biorch-roadmap

### Purpose

Manage the project roadmap.

Use this when the roadmap itself needs to change.

Examples:

    /biorch-roadmap

Typical operations include:

- inspecting roadmap phases
- proposing a phase change
- adding a phase
- modifying roadmap descriptions

### Important rule

Roadmap changes require explicit human approval.

Example:

Gemini proposes:

    Phase 13 — Deployment and Operations

Human:

    yes

Only then is the roadmap modified.

---

# 12. /biorch-sync

### Purpose

Synchronize governed project documentation/state where required.

This is a supporting command rather than a command that should be
executed automatically at every phase step.

Use it when the command's specific synchronization purpose is required.

Always inspect the proposed changes before accepting them.

---

# 13. Recommended Standard Phase Workflow

For a normal implementation phase, use the following sequence.

## Step 1 — Determine where we are

    /biorch-status

or:

    /biorch-next

Use `/biorch-next` when the main question is:

    "What should I do next?"

---

## Step 2 — Confirm the contract

    /biorch-contract

Verify that the canonical contract exists and represents the intended
architecture.

---

## Step 3 — Create the task

    /biorch-task

This creates the governed TASK.md for the phase.

---

## Step 4 — Review the task

    /biorch-review

Confirm that the task correctly translates the contract into
implementation/investigation requirements.

---

## Step 5 — Human approval

If the review or task workflow requires a human decision, approve it
before implementation.

---

## Step 6 — Implement

Perform the implementation described by TASK.md.

Run the required tests.

---

## Step 7 — Review implementation

    /biorch-review

The implementation is reviewed against:

- contract
- task
- architecture
- security requirements
- tests

---

## Step 8 — Phase closure

The review/closure workflow produces:

    PHASE_CLOSURE.md

Typical state:

    READY_FOR_CLOSURE

---

## Step 9 — Ask what happens next

    /biorch-next

If the phase is ready for closure, Gemini should identify the human
closure decision.

---

## Step 10 — Human closes the phase

Human explicitly approves the closure.

Example:

    yes, confirming Phase 02 closure

The governance index is then updated.

Example:

    Phase 02 → CLOSED

---

## Step 11 — Synchronize project state

    /biorch-status

Review the proposed PROJECT_STATE.md and any Git synchronization.

---

## Step 12 — Determine the next phase

    /biorch-next

The command should now identify the next governed phase/action.

---

# 14. Complete Lifecycle Example

Example: Phase 02 — Tool Gateway

    /biorch-next
          ↓
    Phase 02 identified
          ↓
    /biorch-contract
          ↓
    TOOL_GATEWAY_CONTRACT.md
          ↓
    /biorch-task
          ↓
    TASK.md
          ↓
    /biorch-review
          ↓
    TASK APPROVED
          ↓
    IMPLEMENTATION
          ↓
    TESTS
          ↓
    /biorch-review
          ↓
    IMPLEMENTATION APPROVED
          ↓
    PHASE_CLOSURE.md
          ↓
    /biorch-next
          ↓
    Human approval
          ↓
    Phase 02 CLOSED
          ↓
    /biorch-status
          ↓
    PROJECT_STATE synchronized
          ↓
    /biorch-next
          ↓
    Phase 03 identified

---

# 15. Commands That Are NOT Normally Sequential

The following commands are supporting tools rather than mandatory
commands in every phase:

- /biorch-governance
- /biorch-roadmap
- /biorch-sync
- /biorch-contract

Their usage depends on the situation.

For example, `/biorch-roadmap` should only be used when the roadmap
actually needs to change.

Similarly, `/biorch-contract` is important when defining or changing
architecture contracts, but does not necessarily need to modify anything
during every phase.

---

# 16. The Simple Mental Model

When developing a normal BIOrch phase, remember:

    CONTRACT
       ↓
     TASK
       ↓
    REVIEW
       ↓
    BUILD
       ↓
    REVIEW
       ↓
    CLOSE
       ↓
    HUMAN
       ↓
     STATUS
       ↓
     NEXT

The most important commands are therefore:

    /biorch-contract
    /biorch-task
    /biorch-review
    /biorch-next
    /biorch-status

The other commands are supporting governance tools.

---

# 17. Human-Controlled Gates

The following actions should remain human-controlled:

- substantive contract changes
- roadmap changes
- approval of implementation decisions where required
- phase closure
- Git synchronization/commits when proposed by governance commands
- transition into the next governed phase

Gemini CLI can inspect, propose, implement, review, and document.

It should not silently redefine architectural authority.

---

# 18. Phase 02 Example

The actual Phase 02 lifecycle followed approximately:

    Tool Gateway Contract
            ↓
    Phase 02 TASK.md
            ↓
    Task Review
            ↓
    Tool Gateway Implementation
            ↓
    7/7 Tests Passed
            ↓
    Implementation Review
            ↓
    REVIEW.md = APPROVED
            ↓
    PHASE_CLOSURE.md = READY_FOR_CLOSURE
            ↓
    Human Approval
            ↓
    PHASE 02 = CLOSED
            ↓
    Phase 03 = Next Phase

This is the reference lifecycle for future implementation phases.




| Command              | Think of it as                     | Main purpose                     |
| -------------------- | ---------------------------------- | -------------------------------- |
| `/biorch-contract`   | **What are the rules?**            | Manage/inspect contracts         |
| `/biorch-task`       | **What are we building?**          | Create governed task             |
| `/biorch-review`     | **Is this correct?**               | Review task/implementation       |
| `/biorch-next`       | **What happens next?**             | Determine governed next action   |
| `/biorch-status`     | **Where are we?**                  | Synchronize project state        |
| `/biorch-roadmap`    | **Where is the project going?**    | Manage roadmap                   |
| `/biorch-governance` | **What are our governance rules?** | Governance inspection/operations |
| `/biorch-sync`       | **Synchronize things**             | Supporting synchronization       |


Mental model:

                 ┌──────────────────────────┐
                 │  PHASE CONTRACT / DESIGN │
                 │                          │
                 │ Define what this phase   │
                 │ is supposed to achieve   │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-task            │
                 │                          │
                 │ Start phase              │
                 │ PLANNED → IN_PROGRESS    │
                 │                          │
                 │ Gemini performs the      │
                 │ actual implementation    │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-review           │
                 │                          │
                 │ Validate implementation  │
                 │ against contract + task  │
                 │                          │
                 │ IN_PROGRESS              │
                 │ → READY_FOR_CLOSURE      │
                 └────────────┬─────────────┘
                              │
                         Human approval
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-close            │
                 │                          │
                 │ Final closure audit       │
                 │ Create closure evidence   │
                 │                          │
                 │ READY_FOR_CLOSURE         │
                 │ → CLOSED                 │
                 └────────────┬─────────────┘
                              │
                              ▼
              ╔══════════════════════════════════╗
              ║       POST-PHASE CHECKPOINT      ║
              ╚══════════════════════════════════╝
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-sync             │
                 │                          │
                 │ Bring derived docs/state  │
                 │ into synchronization      │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-status           │
                 │                          │
                 │ "Is everything actually  │
                 │ consistent?"             │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │  /biorch-git              │
                 │                          │
                 │ Review/commit/push the    │
                 │ completed phase changes   │
                 └────────────┬─────────────┘
                              │
                              ▼
              ╔══════════════════════════════════╗
              ║       PLAN THE NEXT PHASE        ║
              ╚══════════════════════════════════╝
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ /biorch-next    │   │ /biorch-roadmap │
          │                 │   │                 │
          │ What should     │   │ Where is the    │
          │ I do next?      │   │ project going?  │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
                    NEXT PHASE CONTRACT
                              │
                              ▼
                         🔄 REPEAT