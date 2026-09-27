# BIOrch Git Command Design (/biorch-git)

## 1. Existing Git Architecture
Current BIOrch Git operations are entirely under human control. The existing governance commands (`/biorch-sync`, `/biorch-status`, `/biorch-next`) are strictly read-only or limited to documentation/phase-state reconciliation. They do not perform Git mutations (stage, commit, push). All Git operations are currently handled manually by the developer in the terminal, outside of the governed command framework.

## 2. /biorch-sync Responsibility Boundary
- **Purpose**: Documentation synchronization and phase-state reconciliation based on the three-part state model (LAST_COMPLETED, ACTIVE, NEXT_PLANNED).
- **Prohibitions**: Performs NO Git mutations (add, commit, push).
- **Scope**: Modifies ONLY approved derived documentation (`docs/PROJECT_STATE.md`, `docs/ROADMAP.md`, `README.md`).

## 3. /biorch-git Responsibility Boundary
- **Purpose**: A dedicated, governed workflow for Git inspection, change staging, commit preparation, and push operations.
- **Responsibility**: Git inspection, change classification, approval, staging, staged-diff verification, commit, and push.
- **Constraints**: Must remain separate from `/biorch-sync` to maintain a clear distinction between documentation updates and Git lifecycle operations.

## 4. Proposed Lifecycle
The governed `/biorch-git` lifecycle:
1.  **Phase 1 — Git state inspection**: `git status`, branch info.
2.  **Phase 2 — Change inventory**: List untracked/modified/staged files.
3.  **Phase 3 — Change classification**: Human classifies changes (governance task evidence, code, etc.).
4.  **Phase 4 — Commit scope proposal**: Command proposes files to stage.
5.  **Phase 5 — Human approval**: Human reviews and approves proposed staging scope.
6.  **Phase 6 — Staging**: Command stages ONLY the approved files.
7.  **Phase 7 — Staged-diff verification**: Command shows `git diff --staged`.
8.  **Phase 8 — Commit approval**: Human reviews diff and approves commit.
9.  **Phase 9 — Commit**: Command performs `git commit`.
10. **Phase 10 — Push decision**: Command proposes push based on remote status.
11. **Phase 11 — Push approval**: Human reviews push proposal.
12. **Phase 12 — Push**: Command performs `git push` (if approved).
13. **Phase 13 — Final verification**: Command reports successful operation state.

## 5. Human Approval Gates
- **Staging Scope**: Explicitly approve files to be staged.
- **Commit Message**: Explicitly approve proposed commit message.
- **Staged Diff**: Review changes before commit.
- **Push Proposal**: Explicitly approve push after reviewing remote status.

## 6. Staging Safety Model
- Never use `git add .` blindly.
- Inspect `git status`.
- Present list of candidate files.
- Require explicit selection/confirmation.
- Ensure only approved files are staged.

## 7. Commit Safety Model
- Never automatically commit.
- Require review of staged changes before committing.
- Display branch, local HEAD, and staged files before commit.
- Require commit message approval.

## 8. Push Safety Model
- Push is an independent decision.
- Before push: show branch, remote, local/remote status (ahead/behind), and list of commits to be pushed.
- Explicit approval required.
- NO force push, NO history rewriting.

## 9. Failure/STOP Behavior
- Default behavior is to **STOP and report** upon any failure (staging, diff mismatch, commit error, auth failure, remote divergence, etc.).
- Do not attempt recovery or auto-retry.

## 10. Command Registration Considerations
- Register as `/biorch-git` in `.gemini/commands/biorch-git.toml`.
- Must avoid collision with existing command definitions.

## 11. Files to be Created/Modified
- **Create**: `.gemini/commands/biorch-git.toml` (registration).
- **Create**: `src/biorch/tools/git.py` (implementation).
- **Update**: `.gemini/commands/` (if needed for registration structure).

## 12. Files That MUST NOT be Modified
- `.gemini/commands/biorch-sync.toml`
- Historical artifacts (`TASK.md`, `RESPONSE.md`, `REVIEW.md`, `PHASE_CLOSURE.md`)
- Existing documentation (except via `/biorch-sync`)
- Canonical source artifacts (`examples/artifacts/*`)
- Any files outside the approved staging scope.

## 13. Open Design Questions
- How to handle staging of generated files vs. source code in the classification step?
- Should `/biorch-git` require a link to a `TASK.md` to be "governed"?

## 14. Recommended Implementation Sequence
1.  Human review and approve this design (`DESIGN_READY`).
2.  Implement staging safety logic.
3.  Implement commit safety and approval logic.
4.  Implement independent push safety and approval logic.
5.  Register the command.

---
Final Verdict: DESIGN_READY
