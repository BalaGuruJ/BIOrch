# Phase 08.1 — Agent / Orchestrator Contract Boundary Audit

## 1. Audit Scope
This audit evaluates the Phase 08 architecture draft against existing BIOrch deterministic contracts (Agent, Orchestrator, Tool Gateway) and governance to determine if parallel subprocess-based execution is compatible with the current governance model and to identify needed contract changes or corrections.

## 2. Repository Evidence Examined
- `docs/phase-08/PHASE_08_ARCHITECTURE_DRAFT.md`
- `contracts/agent/DETERMINISTIC_AGENT_CONTRACT.md`
- `contracts/orchestrator/ORCHESTRATOR_CONTRACT.md`
- `contracts/powerbi-agent/POWERBI_AGENT_CONTRACT.md`
- `contracts/tableau-agent/TABLEAU_AGENT_CONTRACT.md`
- `contracts/tool-gateway/TOOL_GATEWAY_CONTRACT.md`
- `.agents/skills/` (procedural context)
- `governance/gemini/` (operating protocol)

## 3. Orchestrator Boundary Analysis
- The existing `ORCHESTRATOR_CONTRACT` (BIORCH-ORCH-001) is strictly limited to Phase 04 deterministic sequential orchestration.
- Phase 08's parallel subprocess-based orchestration falls outside the existing contract's scope (which explicitly prohibits parallel execution).
- The future orchestrator must remain the authoritative governance layer, treating Gemini CLI as a substrate (consistent with existing principles).

## 4. Agent Boundary Analysis
- The current `DETERMINISTIC_AGENT_CONTRACT` (BIORCH-AGENT-001) is designed for a single agent. It does not account for a subprocess-isolated specialist worker initiated by a higher-level orchestrator.
- Tableau and Power BI agents can represent specialist execution units, provided they conform to the existing Tool Gateway interface and structured agent result contract.

## 5. Proposed Result Contract Compatibility
- The proposed `agent_result_contract` in the architecture draft (`{"agent_id": "...", "status": "SUCCESS", ...}`) is compatible with BIOrch's structured result conventions (e.g., `BIORCH-AGENT-001` section 11/12). 
- Provenance requirements in `BIORCH-AGENT-001` (section 15) must be strictly applied.

## 6. Governance Boundary Analysis
- Gemini-generated output MUST remain untrusted until deterministic validation.
- The existing Tool Gateway (`BIORCH-TG-001`) remains the mandatory boundary for all external capabilities. Specialist agents in Phase 08 MUST NOT bypass this gateway, even if they operate in isolated subprocesses.

## 7. Phase 07 Protection Analysis
- Power BI integration contracts (`POWERBI_AGENT_CONTRACT`) and PBIParser boundaries must remain isolated. Phase 08 must consume PBIParser outputs deterministically; it must not modify or re-implement Phase 07 logic.

## 8. Compatibility Matrix

| Assumption | Observed Evidence | Classification |
|---|---|---|
| Parallel execution | Prohibited by Phase 04 Orchestrator Contract | CONFLICT |
| Gemini CLI subprocess isolation | Consistent with BIOrch security boundary | PASS |
| Deterministic validation requirement | Explicitly supported by BIOrch governance | PASS |
| Tool Gateway role | Mandatory for all external agent tools | PASS |

## 9. Conflicts Requiring Resolution
- **Sequential Orchestration vs Parallel Orchestration:** The current `BIORCH-ORCH-001` contract explicitly forbids parallel execution. Phase 08 requires a new, higher-level orchestrator contract or an amendment to the existing one to support parallel workflows.

## 10. Required Contract Changes
- **New Orchestrator Contract:** Phase 08 needs a new contract (e.g., `PARALLEL_ORCHESTRATOR_CONTRACT`) to govern parallel execution, as modifying `BIORCH-ORCH-001` would break Phase 04.
- **Agent Contract Extension:** The existing `DETERMINISTIC_AGENT_CONTRACT` may need an amendment to define expectations for a "specialist worker" agent operating within a parallel orchestration graph.

## 11. Architecture Draft Corrections
- None required to the draft itself, but it must be acknowledged that the draft's "Option B" (process orchestrator) implies a conflict with `BIORCH-ORCH-001` that requires formal architectural resolution (e.g., a new contract).

## 12. Final Status
- PASS count: 3
- PASS-WITH-CHANGE count: 0
- CONFLICT count: 1
- NOT-YET-IMPLEMENTED count: 0
- Conclusion: Phase 08 can proceed to implementation design, provided the parallel orchestration conflict with `BIORCH-ORCH-001` is formally resolved via a new contract in the next phase.
