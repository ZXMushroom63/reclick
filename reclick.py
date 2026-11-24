import shutil
import sys
import time
from pathlib import Path
import subprocess

sys.path.append(Path(__file__).resolve().parent.joinpath("lib"))  # fix imports
root = Path(__file__).resolve().parent

try:
    import requests
    import webview
    import psutil
except Exception as e:
    print(e)
    cmd = "python"
    if shutil.which(cmd) == None:
        cmd = "python3"
    subprocess.run(
        [
            cmd,
            "-m",
            "pip",
            "install",
            "--trusted-host",
            "pypi.org",
            "--trusted-host",
            "files.pythonhosted.org",
            "pywebview",
            "requests",
            "psutil",
        ]
    )
    sys.exit(1)

import lib.zx_packaging as zx_packaging
import lib.zx_launching as zx_launching
import lib.settings.zx_settings as zx_settings
import lib.utils as utils

class Interop:
    def get_library(self):
        return zx_packaging.get_games()

    def internal_update_library(self):
        zx_packaging.update_games_internal()

    def launch_async(self, configPath, config_obj, modded, flags, prefix):
        zx_launching.launch_game(configPath, config_obj, modded, flags, prefix, root)

    def close_async(self, config_obj):
        zx_launching.close_game(config_obj)

    def read_cfg(self):
        return zx_settings.read_cfg()

    def write_cfg(self, obj):
        return zx_settings.write_conf(obj)

    def generate_steam_id(self):
        return utils.mk_steam_uuid()

    def get_nics(self):
        return utils.get_nics()

    def lanpatch(self, broadcastAddr):
        penguin = not sys.platform.startswith("win")
        if len(broadcastAddr) == 0 or penguin:
            return
        print(f"Running broadcast patch on: {broadcastAddr}")
        import ctypes
        import os

        target_dir = str(root) if "root" in locals() and root else os.getcwd()
        bat_relative_path = ".\\retconlib\\vlanpatch.bat"

        parameters = f'/c cd /d "{target_dir}" && "{bat_relative_path}" {broadcastAddr}'

        print(f"DEBUG: Target Dir: {target_dir}")
        print(f"DEBUG: Parameters: {parameters}")

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", "cmd.exe", parameters, target_dir, 1
        )

    def has_frida(self):
        try:
            import frida
            return True
        except:
            return False


def on_closed():
    k = zx_launching.config_pid_map.keys()
    for key in k:
        zx_launching.config_pid_map[key] = False
    time.sleep(1.0)
    print("Goodbye")


window = webview.create_window("reclick", "app.html", js_api=Interop(), frameless=False)
window.events.closed += on_closed

webview.start(debug=False if len(sys.argv) > 0 else True)
