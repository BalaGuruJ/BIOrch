import pytest
import os
from biorch.integrations.pbi.runtime import initialize_runtime, load_tom_assembly
from biorch.integrations.powerbi.adapter import PowerBIAdapter

# Helpers to mock/get environment paths
def get_tom_dll_path():
    path = os.environ.get("BIORCH_TOM_DLL_PATH")
    if not path:
        pytest.fail("BIORCH_TOM_DLL_PATH not set.")
    return path

def test_runtime_initialization():
    """Verify pythonnet/CoreCLR initializes."""
    # This might fail if DOTNET_ROOT is not set, which is expected behavior for clean environment
    if not os.environ.get("DOTNET_ROOT"):
        with pytest.raises(RuntimeError, match="DOTNET_ROOT not set or invalid"):
            initialize_runtime()
        return
        
    clr = initialize_runtime()
    assert clr is not None
    # Verify runtime is coreclr
    assert os.environ.get("PYTHONNET_RUNTIME") == "coreclr"

def test_missing_tom_dll_path_fails():
    """Verify missing BIORCH_TOM_DLL_PATH causes explicit failure."""
    # Clear environment if set
    old_env = os.environ.get("BIORCH_TOM_DLL_PATH")
    if "BIORCH_TOM_DLL_PATH" in os.environ:
        del os.environ["BIORCH_TOM_DLL_PATH"]
        
    with pytest.raises(RuntimeError, match="TOM DLL path not provided"):
        load_tom_assembly()
        
    if old_env:
        os.environ["BIORCH_TOM_DLL_PATH"] = old_env

def test_invalid_tom_dll_path_fails():
    """Verify invalid BIORCH_TOM_DLL_PATH causes explicit failure."""
    old_env = os.environ.get("BIORCH_TOM_DLL_PATH")
    os.environ["BIORCH_TOM_DLL_PATH"] = "/invalid/path/to/dll"
        
    with pytest.raises(FileNotFoundError):
        load_tom_assembly()
        
    if old_env:
        os.environ["BIORCH_TOM_DLL_PATH"] = old_env
    else:
        del os.environ["BIORCH_TOM_DLL_PATH"]

def test_no_developer_path_embedded():
    """Verify no hardcoded developer-specific paths in source."""
    # This is a static analysis check, not a runtime test.
    # The fix applied to runtime.py removes hardcoded paths.
    # We check here just to be sure.
    import biorch.integrations.pbi.runtime as runtime
    import inspect
    source = inspect.getsource(runtime.initialize_runtime)
    assert "/home/" not in source
    assert "/usr/lib/dotnet" not in source
    assert "/usr/share/dotnet" not in source

def test_fixture_path_independence():
    """Verify AdventureWorks fixture resolves independently of CWD."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixture_path = os.path.join(repo_root, "examples/artifacts/powerbi/AdventureWorks Sales")
    
    # Assert that it is an absolute path and doesn't depend on CWD
    assert os.path.isabs(fixture_path)
    assert "examples/artifacts/powerbi/AdventureWorks Sales" in fixture_path
    
    # Check if it exists
    assert os.path.exists(fixture_path)

def test_tom_assembly_loading():
    """Verify Microsoft.AnalysisServices.Tabular can be loaded using environment variables."""
    dll_path = get_tom_dll_path()
        
    initialize_runtime()
    load_tom_assembly(dll_path)
    
    # Check if assembly types are accessible
    import Microsoft.AnalysisServices.Tabular as tom
    assert tom is not None
    
    # Try to access a known class to verify successful interop
    server = tom.Server()
    assert server is not None

def test_powerbi_adapter_loading():
    """Verify PowerBIAdapter loads the AdventureWorks fixture."""
    dll_path = get_tom_dll_path()
        
    # Fixture path is independent of CWD
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixture_path = os.path.join(repo_root, "examples/artifacts/powerbi/AdventureWorks Sales")
    if not os.path.exists(fixture_path):
        pytest.fail(f"AdventureWorks fixture not found at {fixture_path}")
        
    adapter = PowerBIAdapter(dll_path)
    db = adapter.load_model(fixture_path)
    
    assert db is not None
    # Basic check for table existence to confirm metadata parsing
    assert db.Model is not None
    assert db.Model.Tables.Count > 0
