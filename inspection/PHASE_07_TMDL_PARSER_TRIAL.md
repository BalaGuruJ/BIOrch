# Phase 07: TMDL Parser Trial Report

## 1. Test Environment
- **Operating System:** Linux
- **Python Version:** 3.12
- **Environment:** Temporary, isolated virtual environment (`/home/bala2703guru/.gemini/tmp/biorch/trial/venv`)
- **Isolation:** No modifications to repository environment or dependencies.

## 2. Fixture Under Test
- **Fixture:** `examples/artifacts/powerbi/AdventureWorks Sales/`
- **Target:** `AdventureWorks Sales.SemanticModel/definition/*.tmdl`

## 3. Candidate-by-Candidate Execution Results

| Candidate | Status | Result/Error |
| :--- | :--- | :--- |
| `pytmdl` | FAILED | Library `tmdl` imported, but `load_tmdl` is empty/pass. |
| `tmdlparser` | FAILED | Library `tmdlparser` imported, but `parse_tmdl` is a module, not a function. |
| .NET TOM | RUNTIME_ABSENT | Windows-based; cannot be executed on Linux in this environment. |
| `sempy_labs` | RUNTIME_ABSENT | Cloud/Fabric-native; requires Fabric environment. |

## 4. Capability Matrix

| Capability | pytmdl | tmdl-parser | .NET TOM | sempy_labs |
| :--- | :--- | :--- | :--- | :--- |
| Model Parsing | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| DAX Expressions | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| ... | ... | ... | ... | ... |

*All candidates are classified as NOT_TESTED for functional requirements due to runtime failure or environment incompatibility.*

## 5. Failure Analysis
- **Python Candidates (`pytmdl`, `tmdlparser`):** Both installed packages appear to be incomplete, placeholders, or incorrectly structured. They do not expose functional parsing APIs as expected from public documentation.
- **System Candidates (.NET TOM, `sempy_labs`):** These are inherently tied to Windows or cloud environments, which contradicts the local, Linux-based execution requirement.

## 6. Reproducibility Assessment
- **Poor:** Neither Python candidate could be demonstrated to load the fixture.

## 7. Offline/Local-File Suitability
- **None:** No candidate demonstrated the ability to read local TMDL files in this environment.

## 8. Contract-Required Capability Comparison
- **Not Met:** No candidate satisfied the requirement for robust, production-grade TMDL parsing.

## 9. What Remains Unknown
- Whether a functional, open-source Python parser exists that is not a placeholder.
- If interop with .NET/TOM is feasible on Linux without requiring a full Windows environment.

## 10. Recommended NEXT Investigation
- Conduct a broader investigation into professional-grade or alternative, actively maintained Python TMDL parsers, potentially evaluating the source code directly rather than just the installed packages.

TMDL_PARSER_TRIAL_COMPLETE
