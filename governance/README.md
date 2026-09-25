# BIOrch Governance

## Purpose

The governance structure exists to ensure disciplined, traceable, and verifiable implementation of the BIOrch platform. It enforces a strict separation between the procedural "how" (skills) and the actual evidence of work performed (tasks).

## Key Relationships

* **Phases and Tasks:** A phase represents a major architectural milestone. A task is a concrete unit of work executed by an agent (e.g., Gemini CLI) to advance a phase. A phase is not considered closed merely because implementation files exist; it requires formal validation and review of all constituent tasks.
* **Skills and Tasks:** Skills (defined in `.agents/skills/`) describe standard operating procedures. Tasks are specific assignments that rely on those skills.
* **Gemini Responses and Evidence:** A task response from Gemini alone does not mean the task is complete or correct. The response must be backed by factual evidence (tests, diffs, analysis).
* **Validation and Review:** Validation confirms that the work functions as expected based on evidence. Review ensures the work aligns with architectural boundaries, security policies, and contracts. Both must pass before a task or phase can close.
* **Project Status:** Overall project status is determined by aggregating the closure status of individual phases.

## Conceptual Lifecycle

```text
BIOrch Phase
     │
     ├── Gemini Task
     │       │
     │       ▼
     │   Gemini Response
     │       │
     │       ▼
     │   Validation
     │       │
     │       ▼
     │     Review
     │       │
     │       ▼
     │   Closure Decision
     │       │
     │       ▼
     └── Project State
```

> **A task response alone does not mean the task is complete.**
> **A phase is not considered closed merely because implementation files exist.**
