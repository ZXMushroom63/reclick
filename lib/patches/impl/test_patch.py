from lib.patches.base_patch import BasePatch

class test_patch(BasePatch):
    def __init__(self):
        self.patch_name = "test_patch"
    def patch_impl(self, search_dir, global_conf) -> bool:
        print(search_dir)
        print(global_conf)