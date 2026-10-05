import sys
from pathlib import Path
sys.path.append(str(Path('/home/bala2703guru/BIOrch/src')))
from biorch.integrations.tableau.cli import run_pipeline
import tempfile
import shutil

input_twb = '/home/bala2703guru/BIOrch/examples/artifacts/tableau/superstore_base.twb'
output_dir = tempfile.mkdtemp()
try:
    print(f"Running pipeline on {input_twb}")
    run_pipeline(input_twb, output_dir)
    print("Pipeline completed successfully")
except Exception as e:
    print(f"Pipeline failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    shutil.rmtree(output_dir)
