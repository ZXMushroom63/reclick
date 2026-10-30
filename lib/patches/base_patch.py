from lib.utils import datenow

class BasePatch:
    def __init__(self):
        self.patch_name = type(self).__name__
        print(f"Initialised patch: {self.patch_name}")
        pass
    def patch(self, search_dir, global_conf) -> bool:
        start = datenow()
        code = False
        try:
            code = self.patch_impl(search_dir, global_conf)
        except Exception as e:
            print()
            print(f"Exception in patch {self.patch_name}!")
            print(e)
        result = "applied" if code else "skipped"
        print(f"Patch {self.patch_name} {result} in {datenow()-start}ms")
    def patch_impl(self, search_dir, global_conf) -> bool:
        pass