# BIOrch Codex Environment Setup Guide

This guide documents the Codex Cloud environment used to migrate and validate
BIOrch after the Google Cloud Shell / Gemini CLI workflow.

The validated environment has these characteristics:

- Ubuntu 24.04.x LTS
- amd64 / x86_64
- Python 3.12+
- .NET 8 SDK / CoreCLR
- External Python virtual environment at `/opt/biorch-venv`
- Repository root at `/workspace/BIOrch`
- Tracked TOM assemblies under `.deps/`

## 1. Required Environment Variables

Set the following variables in the Codex environment:

```text
DOTNET_ROOT=/usr/lib/dotnet
PYTHONNET_RUNTIME=coreclr
BIORCH_TOM_DLL_PATH=/workspace/BIOrch/.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Tabular.dll
PATH=/opt/biorch-venv/bin:${PATH}
```

- `DOTNET_ROOT` identifies the .NET installation used by pythonnet/CoreCLR. It
  must match the actual .NET installation in the Codex environment.
- `PYTHONNET_RUNTIME` selects CoreCLR for pythonnet.
- `BIORCH_TOM_DLL_PATH` locates the tracked Microsoft Analysis Services Tabular
  Object Model (TOM) assembly.
- `PATH` places the external BIOrch virtual environment before other Python
  executables.

## 2. Codex Environment Setup Script

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== BIOrch Codex Environment Setup ==="

echo "=== Installing system prerequisites ==="
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  python3.12 \
  python3.12-venv

echo "=== Installing Microsoft package repository ==="
curl -fsSL \
  https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb \
  -o /tmp/packages-microsoft-prod.deb

dpkg -i /tmp/packages-microsoft-prod.deb
rm -f /tmp/packages-microsoft-prod.deb

echo "=== Installing .NET 8 SDK / CoreCLR ==="
apt-get update
apt-get install -y --no-install-recommends dotnet-sdk-8.0

echo "=== Creating BIOrch Python environment ==="
python3.12 -m venv /opt/biorch-venv

/opt/biorch-venv/bin/python -m pip install --upgrade pip

echo "=== Installing BIOrch Python dependencies ==="
/opt/biorch-venv/bin/python -m pip install \
  'pydantic>=2.0' \
  'pythonnet==3.2.0' \
  'clr_loader==0.3.1' \
  'cffi==2.1.1' \
  'pytest>=8' \
  'jsonschema>=4,<5' \
  'lxml>=5,<7'

echo "=== Installing BIOrch editable package ==="
/opt/biorch-venv/bin/python -m pip install -e "/workspace/BIOrch[dev]"

echo "=== Validating BIOrch import ==="
/opt/biorch-venv/bin/python -c "import biorch; print('BIOrch import: OK')"

echo "=== Validating Python environment ==="
/opt/biorch-venv/bin/python --version
/opt/biorch-venv/bin/python -m pip --version

echo "=== Validating .NET ==="
dotnet --version

echo "=== Validating BIOrch TOM assemblies ==="

TOM_DLL="/workspace/BIOrch/.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Tabular.dll"

if [ -f "$TOM_DLL" ]; then
    echo "TOM assembly found: $TOM_DLL"
else
    echo "ERROR: TOM assembly not found: $TOM_DLL"
    exit 1
fi

CORE_DLL="/workspace/BIOrch/.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Core.dll"

if [ -f "$CORE_DLL" ]; then
    echo "TOM Core assembly found: $CORE_DLL"
else
    echo "ERROR: TOM Core assembly not found: $CORE_DLL"
    exit 1
fi

echo "=== BIOrch Codex Environment Setup Complete ==="
```

## 3. Why These Python Dependencies Are Present

The validated dependency set is:

- `pydantic >=2.0`
- `pythonnet ==3.2.0`
- `clr_loader ==0.3.1`
- `cffi ==2.1.1`
- `pytest >=8`
- `jsonschema >=4,<5`
- `lxml >=5,<7`

`jsonschema` and `lxml` were required during Codex migration validation even
though they were not both declared in the original project dependency metadata.
This guide does not change `pyproject.toml`.

## 4. Power BI / TOM Runtime Configuration

.NET 8 SDK/CoreCLR is required for the Power BI TOM path. The TOM assemblies
are already tracked in the repository. The primary TOM DLL is:

```text
/workspace/BIOrch/.deps/microsoft.analysisservices/19.117.0/lib/net8.0/Microsoft.AnalysisServices.Tabular.dll
```

`BIORCH_TOM_DLL_PATH` must point to that assembly, `PYTHONNET_RUNTIME` must be
`coreclr`, and `DOTNET_ROOT` must point to the actual .NET installation root.

## 5. Validation Commands

Use these read-only validation commands:

```bash
python --version
python -m pip --version
dotnet --version
dotnet --info
git status --short --branch
git remote -v
```

Run the focused Phase 08 validation:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/biorch-venv/bin/python -m pytest -p no:cacheprovider tests/test_runtime_demo.py
```

Run the full suite:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/biorch-venv/bin/python -m pytest -p no:cacheprovider
```

Successful migration validation recorded:

```text
120 passed in 64.71s
exit code 0
```

## 6. Git Setup in Codex

The Codex checkout may initially have no configured `origin` remote and may use
a local working branch. The canonical repository is:

```text
https://github.com/BalaGuruJ/BIOrch.git
```

Configure the expected origin with:

```bash
git remote add origin https://github.com/BalaGuruJ/BIOrch.git
```

Then verify it with:

```bash
git remote -v
```

Use this safe migration verification sequence:

```bash
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
```

Before pushing, confirm that the intended remote branch has not advanced
unexpectedly.

## 7. Safe Push Workflow

Preferred workflow:

```bash
git status --short --branch
git diff --check
git diff -- <changed-file>
git add <intended-file>
git status --short
git commit -m "<message>"
git push origin <branch>
```

- Never use force-push for normal BIOrch migration work.
- Never amend an existing commit unless explicitly requested.
- Review the staged diff before committing.
- Push only the intended branch.
- Verify the resulting remote commit after pushing.

## 8. Codex Migration Lessons

1. The repository checkout can be complete while the Codex environment is
   missing runtime dependencies.
2. Python dependencies and .NET/CoreCLR dependencies must both be validated.
3. The tracked `.deps` TOM assemblies remove the need to reacquire the TOM
   assemblies for this repository baseline.
4. `DOTNET_ROOT` must match the actual .NET installation path.
5. pythonnet/CoreCLR should be smoke-tested by importing `clr` and loading the
   tracked TOM assembly.
6. The focused Phase 08 runtime test should pass before relying on the full
   suite.
7. The full suite was ultimately validated at 120/120 passing.
8. Git remote/branch configuration should be independently verified after
   migration.

## 9. Known Repository Packaging Note

Migration validation identified runtime imports for `jsonschema` and `lxml`
that were not fully represented in the original declared dependency metadata.

> This document records the environment workaround used during migration. It
> does not authorize or perform a dependency-metadata change.

## 10. Current Validated Baseline

Repository:

```text
BalaGuruJ/BIOrch
```

Phase:

```text
Phase 08
```

Baseline commit:

```text
649abed36c55f03261c73a5f7fd55a1e2b9e65c5
```

Validated result:

```text
Focused Phase 08 runtime tests: 3 passed
Full test suite: 120 passed
Full-suite exit code: 0
```

Phase 09 has not started.
