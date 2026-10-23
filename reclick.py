# ---THISISAVALIDFILEALLISGOOD---
import shutil
import sys
import os
import pathlib
import time
import glob
import socket
import threading
from pathlib import Path
import subprocess
sys.path.append(Path(__file__).resolve().parent) #fix imports
root = Path(__file__).resolve().parent

try:
    import requests
    import webview
    import psutil
except Exception as e:
    print(e)
    subprocess.run(["python", "-m", "pip", "install", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org", "pywebview", "requests", "psutil" ])
    exit(1)

import zx_packaging
import zx_launching

BASE = "https://zxmushroom63.github.io/reclick" #selfhosting is easy btw. or just blank this to force offline

if os.path.exists("updated"):
    os.removedirs("updated")

ENABLE_AUTOUPDATE = False

def background_update():
    is_up = False
    try:
        is_up = requests.get(f"{BASE}/up.txt", timeout=3)
        if (is_up.text.strip() == "Connected"):
            is_up = True
            print("Online, going to download update in background")
    except:
        print("not boaate")
    if not is_up:
        return
    
    os.makedirs("updated")

    UPDATEABLE = [ "reclick.py", "app.html", "zx_packaging.py" "zx_launching.py" ]
    for item in UPDATEABLE:
        try: 
            resp = requests.get(f"{BASE}/{item}")
            if "---THISISAVALIDFILEALLISGOOD---" in resp.text:
                with open("updated/" + item, "w") as f:
                    f.write(resp.text) #i love wasting your bandwidth ;]
        except Exception as e:
            os.removedirs("updated")
            print(f"update failed: {e}")
            return #cancel the update bro, shits over
    with open("updated/complete", "w") as f:
        f.write("complete")
    print("Background update done.")

if ENABLE_AUTOUPDATE:
    update = threading.Thread(target=background_update)
    update.start()

class Interop:
    def get_library(self):
        return zx_packaging.get_games()
    def internal_update_library(self):
        zx_packaging.update_games_internal()
    def launch_async(self, configPath, config_obj, modded, flags):
        zx_launching.launch_game(configPath, config_obj, modded, flags)
    def close_async(self, config_obj):
        zx_launching.close_game(config_obj)
    def read_cfg(self):
        return zx_packaging.read_cfg()
    def write_cfg(self, obj):
        zx_packaging.write_conf(obj)
    def generate_steam_id(self):
        return zx_packaging.mk_steam_uuid()
    def get_nics(self):
        out = {}
        interfaces = psutil.net_if_addrs()
        for interface_name, address_list in interfaces.items():
            out[interface_name] = []
            for addr in address_list:
                if addr.family == socket.AF_INET:
                    out[interface_name].append(addr.address)
        return out
    def lanpatch(self, broadcastAddr):
        penguin = not sys.platform.startswith("win")
        if len(broadcastAddr) == 0 or penguin:
            return
        print(f"Running broadcast patch on: {broadcastAddr}")
        import ctypes
        parameters = f'/c ".\\retconlib\\vlanpatch.bat" {broadcastAddr}'

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "cmd.exe",
            parameters,
            root,
            1
        )
        
def on_closed():
    k = zx_launching.config_pid_map.keys()
    for key in k:
        zx_launching.config_pid_map[key] = False
    time.sleep(1.0)
    print("Goodbye")    

window = webview.create_window('reclick', 'app.html', js_api=Interop(), frameless=False)
window.events.closed += on_closed

webview.start(debug=False if len(sys.argv) > 0 else True)
