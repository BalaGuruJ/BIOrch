# BIOrch Agent Instructions

Before changing code:
- inspect repository state
- read relevant docs
- identify exact task scope
- preserve contracts/security boundaries

After implementation:
- add/update tests
- run validation
- inspect git diff
- summarize files changed and validation results

Do not implement future phases opportunistically.

## BIOrch Project Status Governance

- BIOrch maintains project status through tracked repository documentation.
- `docs/PROJECT_STATE.md` is the current project-state record.
- `governance/gemini/PHASE_INDEX.md` tracks phase progression.
- Gemini task execution is recorded through TASK/RESPONSE/REVIEW artifacts.
- Project status synchronization is human-triggered.
- The phrase/request:
  `Update BIOrch project status`
  is the intended human trigger for the future status-maintenance workflow.
- No automatic status update should occur merely because files changed.
- No automatic Git push should occur without explicit human approval.
- Status must remain factual and traceable.
