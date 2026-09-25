# BIOrch Status Synchronization Governance

## Purpose

Human-controlled synchronization of:

```text
LOCAL BIOrch STATE
+
GOVERNANCE STATE
↓
GIT COMMIT
↓
GITHUB
```

## Human Trigger

`Update BIOrch project status`

## Controlled Outputs

### Local
* `docs/PROJECT_STATE.md`
* `governance/gemini/PHASE_INDEX.md`

### Repository
* Git commit
* GitHub push

## Human Control Boundary

> Updating local status and pushing to GitHub are separate actions.

The system may prepare the update automatically, but Git commit/push requires explicit human approval.

## Safety Rules

* no automatic push
* no implementation changes
* no phase completion without evidence
* no invented test results
* no invented Gemini responses
* no modification of historical RESPONSE.md records
* no rewriting of prior REVIEW.md decisions
* no destructive Git operations
* no force push
* no branch deletion
* no reset/rebase as part of status synchronization

## Architectural Principle

> BIOrch status synchronization is a governance operation, not an implementation operation.

> The status workflow may read project information and write governance documentation, but it must not silently modify application code.

## Future Implementation

`IMPLEMENTATION PENDING — Gemini CLI`

The following are intentionally deferred to Gemini CLI:
* actual skill execution
* shell command execution
* Git integration
* GitHub synchronization
* commit creation
* push handling
* error handling
* dirty working-tree handling
* branch handling
* remote validation
