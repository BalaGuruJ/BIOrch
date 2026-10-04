# BIOrch Demo #1 — Power BI Runtime Environment Verification

## 1. Environment Status
**NEEDS_CONFIGURATION**

---

## 2. Component Verification Details

- **Python Status:**
  - Python Version: `3.12.3`
  - Virtual Environment (`.venv`): Exists and operational at `/home/balaguruj8/BIOrch/.venv`.
  - Package Import: `biorch` package successfully imports when `PYTHONPATH=src` is set.

- **pythonnet Status:**
  - Status: Successfully installed and importable in `.venv` (`pythonnet` package present in site-packages).

- **.NET Status:**
  - Status: Missing / Not installed on host.
  - `dotnet --info`: Returned error / Cloud Shell instruction indicating .NET SDK/runtime is not pre-installed on the host system.

- **DOTNET_ROOT Status:**
  - Status: Unset (empty string `''`).

- **TOM DLL Status:**
  - Status: Present in repository dependencies.
  - Exact Path: `/home/balaguruj8/BIOrch/.deps/microsoft.analysisservices/19.117.0/lib/net6.0/Microsoft.AnalysisServices.Tabular.dll`
  - File Size: `2,237,344` bytes.

- **Tableau Artifact Status:**
  - Status: Present in repository artifacts.
  - Exact Path: `/home/balaguruj8/BIOrch/examples/artifacts/tableau/superstore_base.twb`
  - File Size: `1,167,032` bytes.

- **Power BI Artifact Status:**
  - Status: Present in repository artifacts.
  - Exact Path: `/home/balaguruj8/BIOrch/examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel`

- **Demo Entrypoint Status:**
  - Status: Exists.
  - Exact Path: `/home/balaguruj8/BIOrch/src/biorch/runtime_demo.py`

---

## 3. Exact Missing Prerequisite(s)
1. **.NET 8+ Runtime / SDK:** The `dotnet` runtime/CLI is not installed on the host system.
2. **`DOTNET_ROOT` Environment Variable:** Not configured in the active environment.
3. **`BIORCH_TOM_DLL_PATH` Environment Variable:** Not configured in the active environment (though the DLL file exists in `.deps/`).

---

## 4. Exact Next SINGLE Human Action Required
Install the .NET SDK on the host machine (e.g., via `sudo apt-get update && sudo apt-get install -y dotnet-sdk-8.0` or `dotnet-sdk-10.0`), set `DOTNET_ROOT` to the installation directory, and configure `BIORCH_TOM_DLL_PATH`.
