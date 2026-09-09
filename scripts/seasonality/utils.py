"""
Shared utility functions for ETF Daily seasonality scripts.
"""

import shutil
from pathlib import Path


def distribute(source_files, extra_dirs):
    """
    Copy a list of source files to all existing extra_dirs.

    Args:
        source_files: Iterable of Path or str objects (files to distribute).
        extra_dirs:   Iterable of Path or str objects (target directories).
                      Directories that do not exist are silently skipped.
    """
    for src in source_files:
        src = Path(src)
        for d in extra_dirs:
            d = Path(d)
            if d.exists():
                shutil.copy2(src, d / src.name)
                print(f"  -> distributed {src.name} to {d}")
