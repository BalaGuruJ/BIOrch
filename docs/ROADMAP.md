# BIOrch Roadmap

## Overall Project Goal
The project is building a governed multi-agent BI orchestration system capable of coordinating specialized agents for Tableau and Power BI repositories.

## Target Runtime Architecture
User request
    ↓
Tool Gateway
    ↓
RepositoryAgent
    ↓
Deterministic Orchestrator
    ↓
Specialized BI agents
    ├── Tableau agent
    └── Power BI agent
    ↓
Parallel execution / review loops
    ↓
LLM-assisted planning where appropriate
    ↓
Cross-platform Tableau ↔ Power BI comparison
    ↓
Analysis-ready output

## Roadmap Status
- [COMPLETED]: Finished
- [IN PROGRESS]: Actively being worked on
- [PLANNED]: Future work
- [DEFERRED]: Postponed

## Phases

- [COMPLETED] Phase 0 — Foundation: Project repository, Python environment, initial directory structure.
- [COMPLETED] Phase 1 — Contracts: Establishing the JSON and Python structural contracts (Agent, Task, Result, Tool, Workflow) in a framework-neutral manner. No execution logic.
- [COMPLETED] Phase 2 — Tool Gateway: Implementation of the security boundary, tool validation, and execution policies.
- [PLANNED] Phase 3 — First deterministic Agent: Implementation of the first specialized agent (e.g., RepositoryAgent) proving the Agent → Tool Gateway → Result flow.
- [PLANNED] Phase 4 — Deterministic Orchestrator: Hardcoded orchestration flows (e.g., inspect → analyze → implement → validate → review).
- [PLANNED] Phase 5 — Multiple Agents: Introducing domain agents (TableauAgent, PowerBIAgent) into the orchestrator.
- [PLANNED] Phase 6 — TabUI Integration: Orchestrating TabUI capabilities for Tableau analysis.
- [PLANNED] Phase 7 — PBIParser Integration: Orchestrating PBIParser capabilities for Power BI analysis.
- [PLANNED] Phase 8 — Parallel Orchestration: Allowing independent tasks (e.g., concurrent Tableau and Power BI analysis) to execute in parallel.
- [PLANNED] Phase 9 — Evaluator / Reviewer Loops: Introducing Maker/Checker loops with retry limits.
- [PLANNED] Phase 10 — LLM-based Planning: Replacing deterministic workflows with dynamic LLM-based task graph generation and routing.
- [PLANNED] Phase 11 — Cross-BI Analysis: Enabling comparative analysis between different BI platforms (e.g., Tableau vs. Power BI).
- [PLANNED] Phase 12 — Reporting / Analysis Platform: Outputting canonical, analysis-ready metadata in various formats (CSV, JSON, Excel).
- [PLANNED] Phase 13 — Deployment and Operations: Establishing production infrastructure, CI/CD pipelines, and operational monitoring for the BIOrch system.

## Infrastructure Distinction
Note: The roadmap describes the TARGET BIOrch runtime architecture.
Development infrastructure such as:
- .agents/skills/
- Gemini CLI commands
- development-process documentation
- governance tooling
must NOT be interpreted as runtime BI orchestration agents.

## Change History
- 2026-09-27: Initial roadmap canonicalization and structuring.
