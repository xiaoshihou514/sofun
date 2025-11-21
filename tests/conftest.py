from __future__ import annotations

import sys
from pathlib import Path


# Ensure project root is importable even when running pytest via the console script
ROOT = Path(__file__).resolve().parent.parent
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())
