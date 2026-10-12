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

readDir = pathlib.Path(".")
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
    if match.joinpath("reclick.json").exists():
        continue
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
    appid = 480
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
            "AppID": appid
        }, indent=2))