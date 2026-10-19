# ---THISISAVALIDFILEALLISGOOD---
import json
import pathlib
import time
import os
import subprocess
import sys
import shutil

active_games = {}
def launch_game(config, modded):
    env = os.environ.copy()
    command = [config["GamePath"]]
    if not sys.platform.startswith("win"):
        command.insert(0, "wine")
    if modded:
        env["WINEDLLOVERRIDES"] = "winhttp=n,b;version=n,b;dinput8=n,b"
        env["BEPINEX_DISABLE"] = "0"
    else:
        env["WINEDLLOVERRIDES"] = "dinput8=n,b"
        env["BEPINEX_DISABLE"] = "1"
    if shutil.which("nvidia-offload"):
        command.insert(0, "nvidia-offload")
    print(command)
    subprocess.run(command, env=env)