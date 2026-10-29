from lib.utils import datenow

class BasePatch:
    def __init__(self):
        self.patch_name = "base_patch"
        pass
    def patch(self, search_dir, global_conf) -> bool:
        start = datenow()
        code = self.patch_impl(search_dir, global_conf)
        result = "applied" if code else "skipped"
        print(f"Patch {self.patch_name} {result} in {datenow()-start}ms")
    def patch_impl(self, search_dir, global_conf) -> bool:
        pass