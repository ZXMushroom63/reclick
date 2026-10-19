# ---THISISAVALIDFILEALLISGOOD---
import json
import pathlib
import time
import os
from collections.abc import Iterable
new_games = set()

ignorelist = ["UnityCrashHandler64", "UnityCrashHandler"] #we pick the largest .exe in the game folder

def flatten1(nested_list):
    for item in nested_list:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item
def flatten(nested):
    return list(flatten1(nested))
def make_tags(tags_dict):
    out = []
    for key in tags_dict:
        if tags_dict[key](None):
            out.append(key)
    out.sort()
    return out

readDir = pathlib.Path(".")
def update_games_internal():
    files = flatten(map(lambda x: readDir.rglob(x), ["steam_api.dll", "steam_api64.dll"]))

    matches = set()

    for file in files:
        parts = file.parts
        cwd = pathlib.Path(parts[0])
        found_match = False
        for part in parts[1:]:
            if len(list(cwd.glob("*.exe"))) > 0:
                found_match = True
                break
            cwd = cwd.joinpath(part)
        if found_match:
            matches.add(cwd)

    for match in matches:
        targets = list(match.glob("*.exe"))
        filtered = []
        targets.sort(key=lambda x: os.path.getsize(x), reverse=True)
        for targ in targets:
            if not targ.stem in ignorelist:
                filtered.append(targ)
        if len(filtered) > 0:
            new_games.add(filtered[0])
            
    for game in new_games:
        cwd = game.parent
        appid = 0
        appids = list(cwd.rglob("steam_appid.txt"))
        if len(appids) > 0:
            with open(appids[0], "r") as f:
                try:
                    appid = int(f.read().strip())
                except:
                    pass
        with open(cwd.joinpath("reclick.json"), "w") as f:
            f.write(json.dumps({
                "GamePath": str(game),
                "AppID": appid,
                "Tags": make_tags({
                    "Positron": lambda _: cwd.joinpath("needs_photon_address.txt").exists(), #custom photon server patch
                    "PhotonRedirector": lambda _: len(list(cwd.joinpath("BepInEx").joinpath("plugins").rglob("PhotonRedirector.dll"))) > 0,
                    "PhotonServerSettings": lambda _: len(list(cwd.joinpath("BepInEx").joinpath("plugins").rglob("PhotonServerSettings.dll"))) > 0,
                    "PUN": lambda _: len(list(cwd.rglob("PhotonNetwork.dll"))) > 0,
                    "PUN2": lambda _: len(list(cwd.rglob("PhotonUnityNetworking.dll"))) > 0,
                    "BepInEx": lambda _: cwd.joinpath("BepInEx").exists(),
                    "SteamAPI": lambda _: appid != 0,
                    "Unity": lambda _: cwd.joinpath("UnityCrashHandler64.exe").exists() or cwd.joinpath("UnityCrashHandler.exe").exists(),
                    "IL2CPP": lambda _: len(list(cwd.rglob("il2cpp_data"))) > 0,
                })
            }, indent=2))

# add a UI hint that more games have been added if autodetect finishes after this is called
def get_games():
    files = list(readDir.rglob("reclick.json"))
    out = {}
    for f in files:
        handle = open(f, "r")
        out[str(f)] = handle.read()
        handle.close()
    return out