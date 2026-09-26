# BIOrch — Gemini CLI Developer Experience Integration Audit

## 1. Executive Summary
BIOrch establishes a rigorous, document-driven governance model for development. However, the current workflow is plagued by high manual friction due to the need to shuttle tasks and results between ChatGPT (the architectural planner) and Gemini CLI (the execution engine). By adopting native Gemini CLI capabilities—specifically project-local `GEMINI.md` instructions, custom commands for governance, and integrated Plan Mode—we can transform Gemini CLI from a simple execution tool into a deeply integrated development orchestrator, significantly reducing manual copy/paste overhead while preserving project integrity.

## 2. Current BIOrch Gemini Workflow
The current developer cycle operates as:
1. **ChatGPT:** Architect role. Defines high-level tasks.
2. **Manual:** User copies prompt from ChatGPT to Gemini CLI.
3. **Gemini CLI:** Engineer role. Executes Task.
4. **Manual:** User copies response/output back to ChatGPT for review/planning.
5. **Human:** Evaluates result, triggers governance update, plans next phase.

**Friction Points:** Every cycle requires manual copying of task specifications, context, and output artifacts.

## 3. Existing Skills Inventory
The 10 skills in `.agents/skills/` (`biorch-task`, `biorch-investigation`, etc.) currently provide standardized *guidance* on *how* to perform tasks, but not *execution* support for the tasks themselves. They act as procedural checklists.
- **Recommendation:** Retain these skills as they represent essential "rules of engagement", but refactor those that overlap with governance actions into `custom commands`.

## 4. Gemini CLI Capability Inventory
- **GEMINI.md:** Project-local, authoritative instructions.
- **Commands (.gemini/commands/):** Project-local CLI extensions.
- **Plan Mode:** Structured, verifiable multi-step execution.
- **Skills:** Procedural, expert-level guidance for agents.
- **Sessions:** State preservation.

## 5. Capability Comparison Matrix

| Capability | Native Gemini CLI | Current BIOrch | Potential BIOrch | Recommendation | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GEMINI.md** | Instructions | None | Project rules | **ADOPT NOW** | Centralize governance. |
| **Commands** | `/` actions | None | Governance ops | **ADOPT NOW** | Reduce command fatigue. |
| **Skills** | Procedures | 10 Skills | Expert guidance | **INVESTIGATE** | Refactor overlaps. |
| **Plan Mode** | Structured exec | None | Task lifecycle | **ADOPT NOW** | Matches Task/Review. |

## 6. Copy/Paste Friction Analysis
The root cause is treating Gemini CLI as a stateless execution engine rather than a project-aware tool. By leveraging `GEMINI.md` to define the project's governance, and `commands` to trigger standardized workflows (e.g., `/biorch-task`), we eliminate the need for ChatGPT to provide the "how-to" for every task execution.

## 7. ChatGPT vs Gemini CLI Responsibility Boundary
- **ChatGPT:** Architect (Strategic planning, high-level reasoning, reviewing complex design alternatives, roadmap maintenance).
- **Gemini CLI:** Engineer (In-situ repository inspection, bounded task implementation, automated testing, repository-local validation, governance evidence generation).

## 8. Recommended Target Developer Workflow
1. **ChatGPT:** Defines high-level task.
2. **Human:** Inputs short task description into Gemini CLI via custom command (e.g., `/biorch-task create --objective "..."`).
3. **Gemini CLI:** Executes task, creates governance artifacts.
4. **Human:** Reviews output in situ, optionally asks ChatGPT for review.

## 9. Minimal Target Architecture
*Human -> ChatGPT (Planning/Decision) -> Gemini CLI (Commands/Skills/GEMINI.md/Execution) -> Governance (TASK/RESPONSE/REVIEW files).*

## 10. Adopt Now
- **GEMINI.md**: Create file to centralize project instructions.
- **Plan Mode**: Adopt for task lifecycle management.

## 11. Adopt Later
- **Custom Commands**: Implement after GEMINI.md stabilization.

## 12. Investigate
- **Skill Refactoring**: Identify which of the 10 skills can be converted into custom commands.

## 13. Do Not Adopt
- **Automated Git operations**: Maintain manual oversight for status/push.

## 14. Migration Plan
- **Stage 1:** Consolidate rules into `GEMINI.md`.
- **Stage 2:** Refactor redundant skills into a command-based workflow.
- **Stage 3:** Enable Plan Mode for all implementation tasks.

## 15. Risks / Trade-offs
- Over-automating governance could lead to loss of human oversight, a core BIOrch tenet. Strict adherence to human-triggered status updates is required.

## 16. Open Questions
- Can we safely expose repository governance directly to the CLI without risking state desynchronization?

## 17. Final Recommendation
Adopt `GEMINI.md` and `Plan Mode` immediately. Refactor the 10 skills into a combination of procedural documentation and automated custom commands to align with the Task/Response/Review cycle.
