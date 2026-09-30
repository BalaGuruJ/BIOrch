import sys
import os

# Add baseline to path
baseline_path = os.path.abspath("examples/artifacts/powerbi/phase7_powerbi_parser/powerbi_parser_baseline/src")
if baseline_path not in sys.path:
    sys.path.append(baseline_path)

# Import from baseline
from powerbi.parsing.tmdl_parser_adapter import TMDLParserAdapter

class PowerBIAdapter:
    def __init__(self):
        self._adapter = TMDLParserAdapter()

    def parse(self, model_directory: str):
        return self._adapter.parse_semantic_model(model_directory)
