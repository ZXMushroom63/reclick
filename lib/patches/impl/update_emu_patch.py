import shutil
from lib.patches.base_patch import BasePatch


class UpdateEmuPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
        if not (global_conf["ReplaceSteamAPI"].lower() in ["enable", "yes", "y"]):
            return False
        GSE_FORK_DLLS = [
            "steam_api.dll",
            "steam_api64.dll",
            "steamclient.dll",
            "steamclient64.dll",
        ]

        CT = 0
        for DLL in GSE_FORK_DLLS:
            nodes = list(search_dir.rglob(DLL))
            for node in nodes:
                strNode = str(node)

                if "retconlib" in strNode:
                    continue

                shutil.copy("./retconlib/" + DLL, strNode)
                CT += 1
        return True
