# Gemini Execution Protocol

## Execution Principles

1. Every implementation phase must have a `TASK.md`.
2. Every executed task must have a `RESPONSE.md`.
3. Every completed phase should eventually have a `REVIEW.md`.
4. Gemini responses must not be treated as independent proof of correctness.
5. Acceptance criteria must be explicit.
6. Implementation and architecture review remain separate concerns.
7. A later phase should not silently modify the architectural assumptions of an earlier phase.
8. Scope creep must be documented rather than silently introduced.
9. Runtime execution restrictions must be stated in each task where applicable.
10. Phase completion requires review/acceptance rather than merely a successful Gemini response.

## Task Lifecycle

```text
TASK
↓
Gemini CLI execution
↓
RESPONSE
↓
Review
↓
Acceptance
↓
Next phase
```
