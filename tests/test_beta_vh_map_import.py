import sys
from pathlib import Path

# Add src to path like uvicorn would
_proj_root = Path(__file__).parent.parent
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

"""Test Beta_VH_Map imports under typical runtime where 'src' is in path"""

def test_import_beta_vh_map():
    import importlib
    try:
        m = importlib.import_module('src.Beta_VH_Map')
        assert hasattr(m, 'main')
    except Exception as e:
        raise
