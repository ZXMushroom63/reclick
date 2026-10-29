import importlib
import pkgutil
import sys
import os
from pathlib import Path

PATCHES = [ ]

patchfiles = Path("lib/patches/impl").glob("*.py")
for patch in patchfiles:
    module = importlib.import_module("lib.patches.impl." + patch.stem)
    PATCHES.append(getattr(module, patch.stem))