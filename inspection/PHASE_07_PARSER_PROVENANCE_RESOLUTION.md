# PHASE 07 — Parser Provenance Resolution Report

## PARSER_PROVENANCE_RESOLUTION_COMPLETE

### A. Baseline Origin
The historical baseline, located at `examples/artifacts/powerbi/phase7_powerbi_parser/powerbi_parser_baseline/`, is documented in its `README.md` as a "raw copy of the external Power BI parser". Git history suggests it was snapshotted as part of a restart effort (commit `642181e`).

### B. Dependency Provenance
- FACT: The parser adapter (`src/powerbi/parsing/tmdl_parser_adapter.py`) explicitly imports `tmdlparser`.
- FACT: `tmdlparser` is not declared in `pyproject.toml`.
- FACT: No `requirements.txt` or similar dependency lock file containing `tmdlparser` exists in the repository.
- FACT: `tmdlparser` is missing from the current Python virtual environment.
- INFERENCE: The baseline was never successfully integrated or reproducible within the current BIOrch repository environment. It was likely developed in a separate, isolated environment.

### C. Exact tmdlparser Evidence
- Usage: `import tmdlparser` in `examples/artifacts/powerbi/phase7_powerbi_parser/powerbi_parser_baseline/src/powerbi/parsing/tmdl_parser_adapter.py`.
- Initialization: `self._parser = tmdlparser.TMLDParser()` within the `TMDLParserAdapter` class.
- Reported Errors: `ModuleNotFoundError: No module named 'tmdlparser'` (documented in `inspection/PHASE_07_BASELINE_RUNTIME_INVESTIGATION.md`).

### D. Reproducibility Assessment
**C. IRREPRODUCIBLE.**
The repository contains the adapter code that *uses* the parser but lacks the parser library itself, its source code, or any instructions/declarations for installing it.

### E. Missing Information
- The canonical source or repository for the `tmdlparser` package.
- Any evidence of the `tmdlparser` source code existing within the repository history.

### F. Consequence for Phase 07
The baseline Power BI parser cannot be executed, validated, or utilized as a reference baseline in the current state.

### G. Explicit Recommendation for the NEXT investigation
Initiate a search to identify the canonical source of `tmdlparser` or determine if an alternative, reproducible TMDL parser implementation is available that could serve as a functional replacement for the reference baseline.

---
**Summary of Operations:**
- Files created: `inspection/PHASE_07_PARSER_PROVENANCE_RESOLUTION_COMPLETE.md`
- Files modified: NONE
- Dependencies installed: NONE
- Implementation changes: NONE
- Contract changes: NONE
- Governance changes: NONE
- Baseline changes: NONE
- Git commits created: NONE
