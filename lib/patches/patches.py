import importlib
import pkgutil
import sys
import os
from pathlib import Path
import lib.zx_packaging as zx_packaging

PATCHES = [ ]

patchfiles = Path("lib/patches/impl").glob("*.py")
for patch in patchfiles:
    module = importlib.import_module("lib.patches.impl." + patch.stem)
    builtname = "".join(map(lambda x: x.title(), patch.stem.split("_")))
    PATCHES.append(getattr(module, builtname)())
    
def patch_path(search_dir):
    global_conf = zx_packaging.read_cfg()
    for patch in PATCHES:
        patch.patch(search_dir, global_conf)