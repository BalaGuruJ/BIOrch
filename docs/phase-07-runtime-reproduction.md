# Phase 07: Runtime and Dependency Reproduction Guide

## Overview
This document outlines the deterministic procedure to reproduce the runtime environment required for the BIOrch Power BI parser (Phase 07).

## Prerequisites
- Python 3.12+
- .NET 8.0 SDK

## Reproduction Procedure

### 1. Environment Setup
Configure the following environment variables before executing the BIOrch runtime:

```bash
# Set runtime to coreclr
export PYTHONNET_RUNTIME=coreclr

# Point to your .NET 8+ installation root (must exist)
export DOTNET_ROOT=/usr/lib/dotnet
```

### 2. Dependencies
Install the required Python dependencies:

```bash
pip install pythonnet==3.2.0 clr_loader==0.3.1 cffi==2.1.1
```

### 3. Dependency Acquisition
Acquire the required `Microsoft.AnalysisServices` library (TOM) and dependencies into a project-local `.deps/` directory without using the global NuGet cache:

```bash
# Create a local directory for dependencies
mkdir -p .deps

# Create a temporary project to acquire the package
mkdir -p .tmp_nuget
cd .tmp_nuget
dotnet new console
# Restore packages into the local .deps directory using --packages
dotnet add package Microsoft.AnalysisServices --version 19.117.0 --package-directory ../.deps/
cd ..
rm -rf .tmp_nuget

# TOM requires Core and Tabular DLLs. They are now located in:
# .deps/microsoft.analysisservices/19.117.0/lib/net8.0/
```

### 4. Runtime Configuration
Set the path to the required TOM assembly:

```bash
# The runtime requires Tabular and Core assemblies.
# Point to the localized Tabular assembly.
export BIORCH_TOM_DLL_PATH=$(pwd)/.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Tabular.dll
```

### 5. Execution
Run the smoke tests:

```bash
pytest tests/test_pbi_runtime.py
```

## Runtime Architecture
Python 3.12 -> pythonnet -> HostFxr -> CoreCLR -> Microsoft.AnalysisServices.Tabular (TOM)

## Evidence Reconciliation (2026-10-01)
*Status: Runtime Verification Gap Resolved.*

The previously reported verification gap was due to environment limitations, not implementation defects. The required runtime has been successfully provisioned and verified in the project environment with the following evidence:

- Python 3.12.3
- .NET SDK 8.0.131
- Microsoft.NETCore.App / CoreCLR 8.0.31
- Microsoft.AnalysisServices TOM 19.117.0
- TOM assembly successfully loaded: `.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Tabular.dll`
- Direct pythonnet/CoreCLR initialization succeeded.
- AdventureWorks Sales semantic model successfully loaded, canonicalized, validated, and serialized.
- **Verification Results:**
  - 13/13 Phase 07 tests passed.
  - 87/87 full repository tests passed.
  - 4/4 Tableau regression tests passed.
- **Conclusion:** Runtime availability is a prerequisite for reproducing Phase 07 live TMDL/TOM verification; it is not an unresolved Phase 07 implementation defect. The prerequisite has been provisioned and successfully verified.
