import importlib
from pathlib import Path
import sys

# Support both `python -m pipeline_v2.cli` with PYTHONPATH=scripts and
# `python -m scripts.pipeline_v2.cli` from the repo root.
_PACKAGE_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PACKAGE_DIR.parent
_REPO_ROOT = _SCRIPTS_DIR.parent

for _path in (str(_REPO_ROOT), str(_SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

_control_plane = importlib.import_module(f"{__name__}.control_plane")
BudgetConfig = _control_plane.BudgetConfig
BudgetRule = _control_plane.BudgetRule
ControlPlane = _control_plane.ControlPlane
Job = _control_plane.Job
Lease = _control_plane.Lease

__all__ = [
    "BudgetConfig",
    "BudgetRule",
    "ControlPlane",
    "Job",
    "Lease",
]
