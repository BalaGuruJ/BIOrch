# BIOrch Project Skill

Read `docs/PROJECT_STATE.md` before implementation.
Read `docs/ARCHITECTURE.md` and `docs/SECURITY.md` for architecture/security work.

Rules:
1. Small, single-purpose changes.
2. Preserve structured Task/Result contracts.
3. Do not bypass the Tool Gateway.
4. Do not add network access by default.
5. Never commit secrets.
6. Run tests before reporting completion.
7. Report changed files, tests, validation and risks.
8. Do not implement future phases opportunistically.

Preferred order:
Contracts → Tool Gateway → deterministic agent → deterministic orchestrator → parallelism → evaluator loop → LLM planning.
