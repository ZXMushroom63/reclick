from lib.patches.base_patch import BasePatch

class CleanupPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
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
        print(f"Cleared {JT} junk logs/traces/dump files")
        return True