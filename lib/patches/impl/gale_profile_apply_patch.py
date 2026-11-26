from pathlib import Path
import os
import shutil
from lib.patches.base_patch import BasePatch
from lib.zx_modding import get_modprofiles

class GaleProfileApplyPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf, game_conf) -> bool:
        # remove all hardlinks (needed for all stages)
        # TODO: add diff-check optimisation, to skip repatching the same thing for no reason
        for dirpath, _, filenames in os.walk(search_dir, followlinks=False):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if not filepath.is_symlink() and filepath.lstat().st_nlink > 1:
                    filepath.unlink()
        
        for res in search_dir.rglob("retcon_hardlink"):
            try:
                shutil.rmtree(res.parent)
            except:
                pass
        
        profile_id = game_conf["Settings"]["GaleProfile"]
        
        if profile_id == "None":
            return True #our job here is done
        
        profilesdb = get_modprofiles()
        if not (str(game_conf["AppID"]) in profilesdb):
            print(f"Profile id {profile_id} not found on {game_conf["AppID"]}")
            return True
        
        profile_wrapper = profilesdb[str(game_conf["AppID"])]
        
        container_path = Path(profile_wrapper["container"]).joinpath(profile_id)
        if not container_path.exists():
            print(f"Profile id {profile_id} not found on {game_conf["AppID"]}")
            return True
        
        modfiles = container_path.rglob("*")
        for modfile in modfiles:
            relativePosition = modfile.relative_to(container_path)
            #print(relativePosition)
            endPosition = search_dir.joinpath(modfile.relative_to(container_path))
            if modfile.is_dir():
                try:
                    os.makedirs(endPosition, exist_ok=False)
                    open(endPosition.joinpath("retcon_hardlink"), 'w').close()
                except Exception as e:
                    pass
            else:
                try:
                    os.makedirs(endPosition.parent, exist_ok=False)
                    open(endPosition.parent.joinpath("retcon_hardlink"), 'w').close()
                except Exception as e:
                    pass
            if endPosition.exists():
                #print(f"Skipping {relativePosition}")
                continue
            try:
                os.link(modfile.absolute(), endPosition.absolute())
                #print(f"Linked: {relativePosition}")
            except:
                pass
        
        # KEEP any manually places files and structures
        # additive merge files for the profile using os.link(), skipping real files
        # this way, it is easy for users to mod mods or add overrides
        return True