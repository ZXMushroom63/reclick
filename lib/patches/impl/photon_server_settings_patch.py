from lib.patches.base_patch import BasePatch

#literally only used by REPO
class PhotonServerSettingsPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
        photonSS = list(search_dir.rglob("uk.1a3.photonserversettings.cfg"))
        for cfg in photonSS:
            new_content = ""
            with open(cfg, "r", encoding="utf-8") as f:
                new_content = f.read()
            pattern = re.compile(r"Server\s*?=\s*?\d+?\.\d+?\.\d+?\.\d+?\s*?$", flags=re.MULTILINE)
            new_content = pattern.sub("Server = " + global_conf["PhotonHost"] + "\n", new_content)
            print(f"Patch photon server redirector address: {cfg}")
            with open(cfg, "w") as x:
                x.write(new_content)
        return True