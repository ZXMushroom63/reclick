import json
import os
from pathlib import Path
import sys
#from lib.utils import perfstage

cached_modprofiles = None
def get_modprofiles():
    global cached_modprofiles
    if cached_modprofiles != None:
        return cached_modprofiles
    penguin = not sys.platform.startswith("win")
    GAME_LOCATIONS = [
        Path("~/.local/share/com.kesomannen.gale").expanduser()
    ] if penguin else [
        Path(os.path.expandvars("%APPDATA%\\com.kesomannen.gale")),
        Path(os.path.expandvars("%LOCALAPPDATA%\\com.kesomannen.gale"))
    ]
    catalogPath = None
    dirPath = None
    for loc in GAME_LOCATIONS:
        if not loc.joinpath("games.json").exists():
            continue
        dirPath = loc
        catalogPath = loc.joinpath("games.json")
    print(f"Using Gale from: {dirPath}")
    if catalogPath == None:
        cached_modprofiles = {}
        return {}
    # gather lists of locally installed mod profiles and reutrern it here
    try:
        ct = json.load(open(catalogPath))["games"]
        out = {}
        for game in ct:
            if not "steam" in game["platforms"]:
                continue
            if game["platforms"]["steam"] == None:
                continue
            if not dirPath.joinpath(game["slug"]).joinpath("profiles").exists():
                continue
            out[str(game["platforms"]["steam"]["id"])] = {
                "profiles": ["None"] + list(map(lambda x: x.absolute().name, list(dirPath.joinpath(game["slug"]).joinpath("profiles").glob("*")))),
                "slug": game["slug"]
            }
        cached_modprofiles = out
        return out
    except Exception as e:
        print(e)
        return {}
    return {}