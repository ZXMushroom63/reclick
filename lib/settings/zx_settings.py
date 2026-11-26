from pathlib import Path
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from lib.utils import get_vk_icd_files
import inspect
readDir = Path(".")


MAINSETTING_DEFINITIONS: dict[str,Setting] = {}
GAMESETTING_DEFINITIONS: dict[str,Setting] = {}

@dataclass
class Setting:
    id: str
    owner: dict[str,Setting]
    kind: str
    _validate: Callable[[Any], bool]
    regen: Callable[[Any], Any] #generate a default value
    quickfix: Callable[[Any], Any]
    def validate(self, value) -> bool:
        typename = type(value).__name__
        if typename != self.kind:
            print(f"[Setting.{self.id}] typecheck failed. expected {self.kind}, got {typename}")
            return False
        return self._validate(value)
    def __post_init__(self) -> None:
        self.owner[self.id] = self

def nullcall(func):
    sig = inspect.signature(func)
    
    kwargs = {
        name: None
        for name, param in sig.parameters.items()
        if param.default is param.empty
        and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
    }
    
    return func(**kwargs)

def internal_fixup_conf(_obj, SETTING_DEFINITIONS, regenArg = None):
    obj = _obj.copy()
    out_obj = {}
    keys = SETTING_DEFINITIONS.keys()
    for key in keys:
        definition = SETTING_DEFINITIONS[key]
        
        if key in obj: #validate and fix existing settings
            if not definition.validate(obj[key]):
                if regenArg:
                    obj[key] = definition.regen(regenArg)
                else:
                    obj[key] = nullcall(definition.regen)
            out_obj[key] = definition.quickfix(obj[key])
        else: #regen missing settings
            if regenArg:
                out_obj[key] = definition.regen(regenArg)
            else:
                out_obj[key] = nullcall(definition.regen)
            out_obj[key] = definition.quickfix(out_obj[key])
    return out_obj

def fixup_conf(_obj):
    return internal_fixup_conf(_obj, MAINSETTING_DEFINITIONS)

def fixup_gameconf(__obj, gamefile):
    _obj = __obj.copy()
    if not "Settings" in _obj:
        _obj["Settings"] = {}
    _obj["Settings"] = internal_fixup_conf(_obj["Settings"], GAMESETTING_DEFINITIONS, gamefile)
    return _obj

def write_gameconf(configPath, obj):
    if obj is None:
        return
    fixed_ver = fixup_gameconf(obj, Path(obj["GamePath"]))
    with open(configPath, "w") as f:
        f.write(json.dumps(fixed_ver, indent=2))
    return fixed_ver

def read_gameconf(configPath):
    out = {}
    try:
        with open(configPath) as f:
            out.update(json.loads(f.read()))
            out = fixup_gameconf(out, Path(out["GamePath"]))
    except:
        return None
    return out

def create_default_gameconf(gamefile):
    return fixup_gameconf({}, gamefile)["Settings"]

def write_conf(obj):
    if obj is None:
        return
    fixed_ver = fixup_conf(obj)
    with open(readDir.joinpath("reclick.root.json"), "w") as f:
        f.write(json.dumps(fixed_ver, indent=2))
    return fixed_ver

def create_default_conf():
    write_conf({})

def read_cfg():
    if not readDir.joinpath("reclick.root.json").exists():
        create_default_conf()
    out = {}
    try:
        with open(readDir.joinpath("reclick.root.json")) as f:
            out.update(json.loads(f.read()))
            out = fixup_conf(out)
    except:
        print("Encountered corrupt config, regenerating...")
        out = fixup_conf({})
        write_conf(out)
    return out


#settings impls
from lib.utils import mk_new_user, mk_steam_uuid, passthrough, verify_ipv4


###################
#  MAIN SETTINGS  #
###################
Setting(
    "SteamID",
    MAINSETTING_DEFINITIONS,
    "str",
    lambda x: len(x) == 17 and x.startswith("7656"),
    mk_steam_uuid,
    passthrough
)

Setting(
    "Username",
    MAINSETTING_DEFINITIONS,
    "str",
    lambda x: len(x) > 0 and len(x) < 64,
    mk_new_user,
    lambda x: x.replace(" ", "_").strip()
)

Setting(
    "VulkanICD",
    MAINSETTING_DEFINITIONS,
    "str",
    lambda x: x in get_vk_icd_files().keys(),
    lambda _: "",
    lambda x: x
)

Setting(
    "PhotonHost",
    MAINSETTING_DEFINITIONS,
    "str",
    verify_ipv4,
    lambda _: "127.0.0.1",
    lambda x: x.strip()
)

Setting(
    "HostAddress",
    MAINSETTING_DEFINITIONS,
    "str",
    verify_ipv4,
    lambda _: "127.0.0.1",
    lambda x: x.strip()
)

Setting(
    "ReplaceSteamAPI",
    MAINSETTING_DEFINITIONS,
    "bool",
    lambda _: True,
    lambda _: True,
    lambda x: x
)

Setting(
    "RetconHue",
    MAINSETTING_DEFINITIONS,
    "int",
    lambda x: x >= 0 and x <= 360,
    lambda _: 0,
    lambda x: x
)

Setting(
    "NoShaders",
    MAINSETTING_DEFINITIONS,
    "bool",
    lambda _: True,
    lambda _: False,
    lambda x: x
)


###################
#  GAME SETTINGS  #
###################

Setting(
    "DisplayName",
    GAMESETTING_DEFINITIONS,
    "str",
    lambda x: len(x) > 0,
    lambda gamefile: gamefile.name.replace(".exe", "").strip(),
    lambda x: x.strip()
)

Setting(
    "Color",
    GAMESETTING_DEFINITIONS,
    "str",
    lambda x: len(x) <= 7 and x.startswith("#"),
    lambda gamefile: "#FFFFFF",
    lambda x: x.strip()
)

Setting(
    "EnableMods",
    GAMESETTING_DEFINITIONS,
    "bool",
    lambda x: True,
    lambda gamefile: True,
    lambda x: x
)

Setting(
    "GaleProfile",
    GAMESETTING_DEFINITIONS,
    "str",
    lambda x: True,
    lambda gamefile: "None",
    lambda x: x
)

Setting(
    "GbeOverlay",
    GAMESETTING_DEFINITIONS,
    "bool",
    lambda x: True,
    lambda gamefile: True,
    lambda x: x
)

Setting(
    "Arguments",
    GAMESETTING_DEFINITIONS,
    "str",
    lambda x: True,
    lambda gamefile: "",
    lambda x: x.strip()
)

Setting(
    "NoHwAccel",
    GAMESETTING_DEFINITIONS,
    "bool",
    lambda x: True,
    lambda gamefile: False,
    lambda x: x
)
