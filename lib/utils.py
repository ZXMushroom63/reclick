import sys
import random
from collections.abc import Iterable
import time
import psutil
import socket
import hashlib
from pathlib import Path

def datenow():
    return int(time.time() * 1000)

def flatten1(nested_list):
    for item in nested_list:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item

def mk_new_user():
    USER = "RETCONPLAYER"
    for i in range(4):
        USER += str(random.randint(0, 9))
    return USER

def flatten(nested):
    return list(flatten1(nested))

def make_tags(tags_dict):
    out = []
    for key in tags_dict:
        if tags_dict[key](None):
            out.append(key)
    out.sort()
    return out

def mk_steam_uuid():
    STEAMID = "7656"
    for i in range(13):
        STEAMID += str(random.randint(0, 9))
    return STEAMID

def get_nics():
    out = {}
    interfaces = psutil.net_if_addrs()
    for interface_name, address_list in interfaces.items():
        out[interface_name] = []
        for addr in address_list:
            if addr.family == socket.AF_INET:
                out[interface_name].append(addr.address)
    return out

def passthrough(x):
    return x

def verify_ipv4(x):
    ip = x.strip()
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        for part in parts:
            segment = int(part)
            if segment > 255 or segment < 0:
                return False
    except:
        return False
    
    return True


VK_DIRECTORIES = { #last takes priority | unique'd by checksum
    "/usr/share/vulkan/icd.d/": "usr",
    "/etc/vulkan/icd.d/": "etc",
    "~/.local/share/vulkan/icd.d/": "~/.local",
    "/run/opengl-driver/share/vulkan/icd.d/": "nix"
}

def hash_path(pth):
    with open(pth, "r") as f:
        text = f.read()
        return hashlib.md5(text.encode("utf-8")).hexdigest()
    return "0"


vk_cache = None
def get_vk_icd_files():
    global vk_cache
    if vk_cache != None:
        return vk_cache
    if not sys.platform.startswith("linux"):
        return {"": "none"}
    icdMap = {}
    for pth in VK_DIRECTORIES.keys():
        directory = Path(pth).expanduser()
        if not directory.exists():
            continue
        matches = list(directory.glob("*.json"))
        for match in matches:
            hsh = hash_path(match)
            icdMap[hsh] = str(match.absolute())
    res = list(icdMap.values())
    res.sort()
    out = {"": "none"}
    for icd in res:
        name = str(icd)
        for base in VK_DIRECTORIES.keys():
            name = name.replace(base, VK_DIRECTORIES[base] + " - ")
        name = name.replace(".x86_64", "")
        name = name.removesuffix(".json")
        name = name.removesuffix("_icd")
        out[str(icd)] = name
    vk_cache = out
    return out

last_stage = datenow()
def perfstage(name):
    return
    print(f"perf: {name} - {datenow() - last_stage}ms")