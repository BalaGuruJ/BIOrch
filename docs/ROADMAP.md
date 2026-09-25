# BIOrch Roadmap

The project is structured into distinct phases, designed to establish a solid foundation before introducing complexity.

## Current Scope

- **[CURRENT] Phase 0 — Foundation:** Project repository, Python environment, initial directory structure.
- **[CURRENT] Phase 1 — Contracts:** Establishing the JSON and Python structural contracts (Agent, Task, Result, Tool, Workflow) in a framework-neutral manner. No execution logic.

## Future Phases

- **Phase 2 — Tool Gateway:** Implementation of the security boundary, tool validation, and execution policies.
- **Phase 3 — First deterministic Agent:** Implementation of the first specialized agent (e.g., RepositoryAgent) proving the Agent → Tool Gateway → Result flow.
- **Phase 4 — Deterministic Orchestrator:** Hardcoded orchestration flows (e.g., inspect → analyze → implement → validate → review).
- **Phase 5 — Multiple Agents:** Introducing domain agents (TableauAgent, PowerBIAgent) into the orchestrator.
- **Phase 6 — TabUI Integration:** Orchestrating TabUI capabilities for Tableau analysis.
- **Phase 7 — PBIParser Integration:** Orchestrating PBIParser capabilities for Power BI analysis.
- **Phase 8 — Parallel Orchestration:** Allowing independent tasks (e.g., concurrent Tableau and Power BI analysis) to execute in parallel.
- **Phase 9 — Evaluator / Reviewer Loops:** Introducing Maker/Checker loops with retry limits.
- **Phase 10 — LLM-based Planning:** Replacing deterministic workflows with dynamic LLM-based task graph generation and routing.
- **Phase 11 — Cross-BI Analysis:** Enabling comparative analysis between different BI platforms (e.g., Tableau vs. Power BI).
- **Phase 12 — Reporting / Analysis Platform:** Outputting canonical, analysis-ready metadata in various formats (CSV, JSON, Excel).
