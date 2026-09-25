# Gemini Task Governance

This directory serves as the canonical Gemini CLI execution-governance area for BIOrch. It contains the authoritative task specifications, execution records, and reviews for work performed through the Gemini CLI.

## Key Files

* **TASK.md:** The instructions given to Gemini.
* **RESPONSE.md:** Gemini's execution response and evidence.
* **REVIEW.md:** Architectural and human review of the result.
* **PHASE_INDEX.md:** Phase-level status dashboard tracking the overall progress.
* **EXECUTION_PROTOCOL.md:** Rules governing Gemini task execution and acceptance.

## Reference Architecture

This governance structure must align with the existing canonical architectural documents:

* [ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
* [ROADMAP.md](../../docs/ROADMAP.md)
* [SECURITY.md](../../docs/SECURITY.md)
* [REAL_WORLD_SCENARIOS.md](../../docs/REAL_WORLD_SCENARIOS.md)
* [FRAMEWORK_EVALUATION.md](../../docs/FRAMEWORK_EVALUATION.md)

It also relies on the defined structural contracts:

* [agent.schema.json](../../schemas/agent.schema.json)
* [task.schema.json](../../schemas/task.schema.json)
* [result.schema.json](../../schemas/result.schema.json)
* [tool.schema.json](../../schemas/tool.schema.json)
* [workflow.schema.json](../../schemas/workflow.schema.json)

## Important Distinction

> The phase roadmap describes the intended architectural evolution of BIOrch. The Gemini task registry describes the concrete implementation work that will be authorized for each phase.

Therefore:
* ROADMAP ≠ TASK
* Architecture ≠ IMPLEMENTATION
* TASK ≠ ACCEPTANCE
* Gemini RESPONSE ≠ ARCHITECTURAL APPROVAL
