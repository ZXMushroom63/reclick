from lib.patches.base_patch import BasePatch


class PositronPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
        positron = list(search_dir.rglob("needs_photon_address.txt")) + list(
            search_dir.rglob("needs_photon5_address.txt")
        )
        for cfg in positron:
            print(f"Patch positron address: {cfg}")
            with open(cfg, "w") as x:
                x.write(global_conf["PhotonHost"])
        return True
