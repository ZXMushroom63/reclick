# ---THISISAVALIDFILEALLISGOOD---
import json
import pathlib
import time
import os
import subprocess
import sys
import shutil
import zx_packaging
import psutil
import re

import xml.etree.ElementTree as ET

def patch_path(search_dir):
    global_conf = zx_packaging.read_cfg()
    GSE_FORK_DLLS = [
        "steam_api.dll",
        "steam_api64.dll",
        "steamclient.dll",
        "steamclient64.dll",
    ]
    JT = 0
    junklogs = list(search_dir.rglob("STEAM_LOG*.log"))
    for junklog in junklogs:
        try:
            os.remove(junklog)
        except:
            pass
        JT += 1

    junkcrashes = list(search_dir.rglob("EMU_CRASHES.txt"))
    for junkcrash in junkcrashes:
        try:
            os.remove(junkcrash)
        except:
            pass
        JT += 1
        
    usercfgs = list(search_dir.rglob("configs.user.ini"))

    ST = 0
    for cfg in usercfgs:
        out = []
        with open(cfg) as x:
            dt = x.readlines()

        ND = False
        SD = False
        for ln in dt:
            qLn = ln.strip()

            if len(qLn) == 0:
                continue

            if qLn.startswith("account_name="):
                if not ND:
                    out.append(f"account_name={global_conf["Username"]}")
                    out.append("")
                    ND = True
            elif qLn.startswith("account_steamid="):
                if not SD:
                    out.append(f"account_steamid={global_conf["SteamID"]}")
                    out.append("")
                    SD = True
            elif qLn.startswith("["):
                out.append("")
                out.append(qLn)
            else:
                out.append(qLn)

        with open(cfg, "w") as x:
            x.write("\n".join(out))

        ST += 1
    
    CT = 0
    if global_conf["ReplaceSteamAPI"].lower() in ["enable", "yes", "y"]:
        for DLL in GSE_FORK_DLLS:
            nodes = list(search_dir.rglob(DLL))
            for node in nodes:
                strNode = str(node)

                if "retconlib" in strNode:
                    continue

                shutil.copy("./retconlib/" + DLL, strNode)
                CT += 1
    print(f"Updated {CT} DLLs, cleared {JT} logs, updated {ST} configs")
    
    positron = list(search_dir.rglob("needs_photon_address.txt"))
    for cfg in positron:
        print(f"Patch positron address: {cfg}")
        with open(cfg, "w") as x:
            x.write(global_conf["PhotonHost"])
    
    if search_dir.parent.name.lower() == "deploy" and search_dir.name.lower() == "bin_win64": # and search_dir.joinpath("bin_Win32").exists()
        print("Patching photon server configs...")
        patternPub = re.compile(r"<setting.+?name=\"PublicIPAddress\".*?>.*?\n*?\s*?<value>\s*?\d+?\.\d+?\.\d+?\.\d+?\s*?<\/value>", flags=re.MULTILINE)
        patternMst = re.compile(r"<setting.+?name=\"MasterIPAddress\".*?>.*?\n*?\s*?<value>\s*?\d+?\.\d+?\.\d+?\.\d+?\s*?<\/value>", flags=re.MULTILINE)
        patternSrv = re.compile(r'(<(?:UDP|TCP)Listener\b[^>]*?\bIPAddress=")\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}("[^>]*?\bOverrideApplication\s*=\s*"(?:Game|Master)"[^>]*>)', flags=re.DOTALL)
        photonLoadbalancingConfs = list(search_dir.parent.rglob("Photon.LoadBalancing.dll.config"))
        photonServerConfs = list(search_dir.parent.rglob("PhotonServer.config"))
        replacementPub = f"<setting name=\"PublicIPAddress\" serializeAs=\"String\">\n        <value>{global_conf["HostAddress"]}</value>"
        replacementMst = f"<setting name=\"MasterIPAddress\" serializeAs=\"String\">\n        <value>{global_conf["HostAddress"]}</value>"
        for cfg in photonLoadbalancingConfs:
            print(f"Patch photon loadbalancing conf: {cfg}")
            new_content = ""
            with open(cfg, "r", encoding="utf-8") as f:
                new_content = f.read()
            new_content = patternPub.sub(replacementPub, new_content)
            new_content = patternMst.sub(replacementMst, new_content)
            with open(cfg, "w", encoding="utf-8") as f:
                f.write(new_content)
        for cfg in photonServerConfs:
            print(f"Processing: {cfg}")
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(cfg, parser=parser)
            root = tree.getroot()
            tags = root.findall(".//*[@OverrideApplication]")
            for tag in tags:
                if tag.get("IPAddress") is not None and tag.get("OverrideApplication") in ["Game", "Master"]:
                    tag.set("IPAddress", global_conf["HostAddress"])
            
            ET.indent(root, space="    ")
            tree.write(cfg, encoding="utf-8", xml_declaration=True)

config_pid_map = {}
def launch_game(config, modded, flags):
    global config_pid_map
    penguin = not sys.platform.startswith("win")
    env = os.environ.copy()
    command = [str(pathlib.Path(config["GamePath"]).absolute())]
    #dedupe(config["GamePath"])
    fileName = pathlib.Path(config["GamePath"]).name
    if penguin:
        command.insert(0, "wine")
    env["WINEDEBUG"] = "-all"
    if modded:
        env["WINEDLLOVERRIDES"] = "winhttp=n,b;version=n,b;dinput8=n,b"
        env["BEPINEX_DISABLE"] = "0"
    else:
        env["WINEDLLOVERRIDES"] = "dinput8=n,b"
        env["BEPINEX_DISABLE"] = "1"
    if shutil.which("nvidia-offload"):
        command.insert(0, "nvidia-offload")
    command = command + flags
    old_portstart = subprocess.run(["sysctl", "-n", "net.ipv4.ip_unprivileged_port_start"], capture_output=True, text=True).stdout.strip()
    
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
        containerPath = pathlib.Path(config["GamePath"]).parent
        
        patch_path(containerPath)
        
        process = subprocess.Popen(command, env=env, cwd=containerPath, creationflags=subprocess.CREATE_NEW_CONSOLE)
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