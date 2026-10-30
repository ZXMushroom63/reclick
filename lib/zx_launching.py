import json
from pathlib import Path
import time
import os
import subprocess
import sys
import shutil
import lib.zx_packaging as zx_packaging
import psutil
import re
from lib.patches.patches import patch_path

config_pid_map = {}
def launch_game(configPath, config, modded, flags, prefix, root):
    global config_pid_map
    global_conf = zx_packaging.read_cfg()
    penguin = not sys.platform.startswith("win")
    env = os.environ.copy()
    gamePath = Path(configPath).parent.joinpath(Path(config["GamePath"]))
    command = [str(gamePath.absolute())]
    #dedupe(config["GamePath"])
    fileName = gamePath.name
    if penguin:
        command.insert(0, "wine")
        env["VK_DRIVER_FILES"] = "/run/opengl-driver/share/vulkan/icd.d/nvidia_icd.json"
        env["WINEDEBUG"] = "-all"
    env["EOSR_DATA_DIR"] = str(root.joinpath(".eosr").absolute())
    env["EOSR_ENABLE_LAN"] = "1"
    env["EOSR_TRACE"] = "lifecycle"
    env["EOSR_DISPLAY_NAME"] = global_conf["Username"]
    if modded:
        env["WINEDLLOVERRIDES"] = "winhttp=n,b;version=n,b;dinput8=n,b"
        env["BEPINEX_DISABLE"] = "0"
    else:
        env["WINEDLLOVERRIDES"] = "dinput8=n,b"
        env["BEPINEX_DISABLE"] = "1"
    if shutil.which("nvidia-offload"):
        command.insert(0, "nvidia-offload")
    command = prefix + command + flags
    old_portstart = 1024
    # subprocess.run(["sysctl", "-n", "net.ipv4.ip_unprivileged_port_start"], capture_output=True, text=True).stdout.strip()
    
    if "PhotonServer4" in config["Tags"] or "PhotonServer5" in config["Tags"]:
        if penguin:
            subprocess.run(["pkexec", "sysctl", "-w", "net.ipv4.ip_unprivileged_port_start=80"], env=env)
        else:
            try:
                subprocess.run(["taskkill", "/F", "/IM", fileName], check=True, capture_output=True, text=True)
            except:
                pass
        
    print(command)
    try:
        containerPath = gamePath.parent
        
        patch_path(containerPath)
        
        kwargs = {
            "env": env,
            "cwd": containerPath
        }
        if not penguin:
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        process = subprocess.Popen(command, **kwargs)
        config_pid_map[config["GamePath"]] = True
        
        try:
            while True:
                ret = process.poll()
                if ret is not None:
                    print(f"Process exited with code {ret}")
                    config_pid_map[config["GamePath"]] = False
                    break

                if config_pid_map[config["GamePath"]] == False:
                    print(f"Terming process...")
                    process.terminate()

                    try:
                        print(f"Killing process...")
                        sys.stdout.flush()
                        process.wait(timeout=0.5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
                time.sleep(0.1)
        finally:
            config_pid_map[config["GamePath"]] = False
    except Exception as e:
        print(e)
    config_pid_map[config["GamePath"]] = False
    # if "PhotonServer4" in config["Tags"] or "PhotonServer5" in config["Tags"] and penguin:
    #     subprocess.run(["pkexec", "sysctl", "-w", f"net.ipv4.ip_unprivileged_port_start={old_portstart}"], env=env)
        
def close_game(config):
    config_pid_map[config["GamePath"]] = False