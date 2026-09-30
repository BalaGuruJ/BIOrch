import os
from biorch.integrations.pbi.runtime import initialize_runtime, load_tom_assembly

class PowerBIAdapter:
    def __init__(self, tom_dll_path: str = None):
        initialize_runtime()
        # Allows optional override, or defaults to env-based resolution
        load_tom_assembly(tom_dll_path)
        
        # Import TOM types now that the assembly is loaded
        import Microsoft.AnalysisServices.Tabular as tom
        self.tom = tom

    def load_model(self, model_folder: str):
        """
        Loads a semantic model from a TMDL folder using TOM.
        """
        if not os.path.exists(model_folder):
            raise FileNotFoundError(f"Model folder not found: {model_folder}")
            
        # Accessing TOM deserialization
        # Security Boundary: Only accessing metadata, no DAX/M
        db = self.tom.TmdlSerializer.DeserializeDatabaseFromFolder(model_folder)
        return db
