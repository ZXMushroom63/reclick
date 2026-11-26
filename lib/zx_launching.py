from pathlib import Path
import time
import os
import subprocess
import sys
import shutil
import lib.settings.zx_settings as zx_settings
from lib.patches.patches import patch_path

config_pid_map = {}

def launch_game(configPath, root):
    global config_pid_map
    global_conf = zx_settings.read_cfg()
    config = zx_settings.read_gameconf(configPath)
    flags = config["Settings"]["Arguments"].split(" ")
    penguin = not sys.platform.startswith("win")
    env = os.environ.copy()
    gamePath = Path(configPath).parent.joinpath(Path(config["GamePath"]))
    command = [str(gamePath.absolute())]
    fileName = gamePath.name
    if penguin:
        command.insert(0, "wine")
        if len(global_conf["VulkanICD"]) > 0 and Path(global_conf["VulkanICD"]).exists():
            env["VK_DRIVER_FILES"] = global_conf["VulkanICD"]
        env["WINEDEBUG"] = "-all"

    try:
        os.mkdir(root.joinpath(".eosr").absolute())
    except:
        pass
    env["LOVELY_MOD_DIR"] = str(gamePath.parent.joinpath("mods").absolute())
    env["EOSR_DATA_DIR"] = str(root.joinpath(".eosr").absolute())
    env["EOSR_ENABLE_LAN"] = "1"
    env["EOSR_TRACE"] = "lifecycle"
    env["EOSR_DISPLAY_NAME"] = global_conf["Username"]
    
    if config["Settings"]["EnableMods"]:
        env["WINEDLLOVERRIDES"] = "winhttp=n,b;version=n,b;dinput8=n,b"
        env.pop("DOORSTOP_DISABLE", None)
    else:
        env["WINEDLLOVERRIDES"] = "dinput8=n,b"
        env["DOORSTOP_DISABLE"] = "1"
    
    if shutil.which("nvidia-offload") and not config["Settings"]["NoHwAccel"]:
        command.insert(0, "nvidia-offload")

    command = command + flags
    
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
        
        patch_path(containerPath, config)
        
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
                        sys.stdout.flush()
                        process.wait(timeout=0.5)
                    except subprocess.TimeoutExpired:
                        print(f"Killing process...")
                        process.kill()
                    break
                time.sleep(0.1)
        finally:
            config_pid_map[config["GamePath"]] = False
    except Exception as e:
        print(e)
    config_pid_map[config["GamePath"]] = False
        
def close_game(config):
    config_pid_map[config["GamePath"]] = False