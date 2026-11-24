from pathlib import Path
import json
import os
from lib.utils import flatten, make_tags

new_games = set()

ignorelist = ["UnityCrashHandler64", "UnityCrashHandler"] #we pick the largest .exe in the game folder
readDir = Path(".")

def update_games_internal():
    files = flatten(map(lambda x: readDir.rglob(x), ["steam_api.dll", "steam_api64.dll"]))

    matches = set()

    for file in files:
        if "retconlib" in str(file):
            continue
        parts = file.parts
        cwd = Path(parts[0])
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
            
    photonFiles = filter(lambda unit: not "bin_Win32" in str(unit), flatten(map(lambda x: readDir.rglob(x), ["PhotonSocketServer.exe"])))
    new_games.update(photonFiles)
            
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
                "Name": game.name.replace(".exe", ""),
                "DisplayName": game.name.replace(".exe", ""),
                "GamePath": str(game.relative_to(cwd)),
                "AppID": appid,
                "Arguments": "",
                "Color": "none",
                "Tags": make_tags({
                    "Positron": lambda _: cwd.joinpath("needs_photon_address.txt").exists(), #custom photon server patch
                    "PhotonServerSettings": lambda _: len(list(cwd.joinpath("BepInEx").joinpath("config").rglob("uk.1a3.photonserversettings.cfg"))) > 0,
                    "PUN": lambda _: len(list(cwd.rglob("PhotonNetwork.dll"))) > 0,
                    "PUN2": lambda _: len(list(cwd.rglob("PhotonUnityNetworking.dll"))) > 0,
                    "EOS": lambda _: len(list(cwd.rglob("EOSSDK-Win64-Shipping.dll"))) > 0,
                    "BepInEx": lambda _: cwd.joinpath("BepInEx").exists(),
                    "SteamAPI": lambda _: appid != 0,
                    "Unity": lambda _: cwd.joinpath("UnityCrashHandler64.exe").exists() or cwd.joinpath("UnityCrashHandler.exe").exists()  or cwd.joinpath("UnityPlayer.dll").exists(),
                    "IL2CPP": lambda _: len(list(cwd.rglob("il2cpp_data"))) > 0,
                    "PhotonServer4": lambda _: cwd.joinpath("PhotonLicensing.dll").exists(),
                    "PhotonServer5": lambda _: (not cwd.joinpath("PhotonLicensing.dll").exists()) and cwd.joinpath("PhotonHostRuntime.dll").exists(),
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
        
        try:
            obj = json.loads(out[str(f)])
            if not f.parent.joinpath(Path(obj["GamePath"])).exists():
                f.unlink(True)
                del out[str(f)]
        except:
            f.unlink(True)
            del out[str(f)]
    return out