from pathlib import Path
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
import inspect
readDir = Path(".")


SETTING_DEFINITIONS: dict[str,Setting] = {}
@dataclass
class Setting:
    id: str
    owner: dict[str,Setting]
    kind: str
    _validate: Callable[[Any], bool]
    regen: Callable[[None], Any] #generate a default value
    quickfix: Callable[[Any], Any]
    def validate(self, value) -> bool:
        typename = type(value).__name__
        if typename != self.kind:
            print(f"[Setting.{self.id}] typecheck failed. expected {self.kind}, got {typename}")
            return False
        return self._validate(value)
    def __post_init__(self) -> None:
        SETTING_DEFINITIONS[self.id] = self

def nullcall(func):
    sig = inspect.signature(func)
    
    kwargs = {
        name: None
        for name, param in sig.parameters.items()
        if param.default is param.empty
        and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
    }
    
    return func(**kwargs)

def fixup_conf(_obj):
    obj = _obj.copy()
    out_obj = {}
    keys = SETTING_DEFINITIONS.keys()
    for key in keys:
        definition = SETTING_DEFINITIONS[key]
        
        if key in obj: #validate and fix existing settings
            if not definition.validate(obj[key]):
                obj[key] = nullcall(definition.regen)
            out_obj[key] = definition.quickfix(obj[key])
        else: #regen missing settings
            out_obj[key] = nullcall(definition.regen)
            out_obj[key] = definition.quickfix(out_obj[key])
    return out_obj

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

# GLOBAL SETTINGS
Setting(
    "SteamID",
    SETTING_DEFINITIONS,
    "str",
    lambda x: len(x) == 17 and x.startswith("7656"),
    mk_steam_uuid,
    passthrough
)

Setting(
    "Username",
    SETTING_DEFINITIONS,
    "str",
    lambda x: len(x) > 0 and len(x) < 64,
    mk_new_user,
    lambda x: x.replace(" ", "_").strip()
)

Setting(
    "PhotonHost",
    SETTING_DEFINITIONS,
    "str",
    verify_ipv4,
    lambda _: "127.0.0.1",
    lambda x: x.strip()
)

Setting(
    "HostAddress",
    SETTING_DEFINITIONS,
    "str",
    verify_ipv4,
    lambda _: "127.0.0.1",
    lambda x: x.strip()
)

Setting(
    "ReplaceSteamAPI",
    SETTING_DEFINITIONS,
    "bool",
    lambda _: True,
    lambda _: True,
    lambda x: x
)

Setting(
    "RetconHue",
    SETTING_DEFINITIONS,
    "int",
    lambda x: x >= 0 and x <= 360,
    lambda _: 0,
    lambda x: x
)

Setting(
    "NoShaders",
    SETTING_DEFINITIONS,
    "bool",
    lambda _: True,
    lambda _: False,
    lambda x: x
)