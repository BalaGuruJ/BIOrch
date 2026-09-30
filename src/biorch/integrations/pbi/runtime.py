import os
import sys

def initialize_runtime():
    """
    Initializes the .NET runtime (CoreCLR) and pythonnet for PBI integration.
    """
    os.environ["PYTHONNET_RUNTIME"] = "coreclr"
    
    # 1. Robust DOTNET_ROOT validation (via environment)
    dotnet_root = os.environ.get("DOTNET_ROOT")
    
    if not dotnet_root or not os.path.exists(dotnet_root):
        raise RuntimeError(
            "DOTNET_ROOT not set or invalid. Please set DOTNET_ROOT to the "
            "path of your .NET 8+ installation."
        )

    try:
        import clr
    except ImportError as e:
        raise RuntimeError("Failed to import pythonnet/clr. Ensure dependencies are installed.") from e

    return clr

def load_tom_assembly(dll_path: str = None):
    """
    Loads the Microsoft.AnalysisServices.Tabular assembly.
    Uses BIORCH_TOM_DLL_PATH environment variable if dll_path is None.
    """
    path = dll_path or os.environ.get("BIORCH_TOM_DLL_PATH")
    if not path:
        raise RuntimeError("TOM DLL path not provided and BIORCH_TOM_DLL_PATH not set.")

    if not os.path.exists(path):
        raise FileNotFoundError(f"TOM DLL not found at: {path}")
        
    import clr
    try:
        clr.AddReference(path)
    except Exception as e:
        raise RuntimeError(f"Failed to load TOM assembly from {path}") from e
