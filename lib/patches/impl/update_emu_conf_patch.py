from lib.patches.base_patch import BasePatch

class UpdateEmuConfPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
        usercfgs = []
        usercfgs.extend(list(search_dir.rglob("configs.user.ini")))
        usercfgs.extend(list(search_dir.rglob("configs.main.ini")))

        ST = 0
        for cfg in usercfgs:
            out = []
            with open(cfg) as x:
                dt = x.readlines()

            ND = False
            SD = False
            for ln in dt:
                qLn = ln.strip()

                if len(qLn) == 0:
                    continue

                if qLn.startswith("account_name="):
                    if not ND:
                        out.append(f"account_name={global_conf["Username"]}")
                        out.append("")
                        ND = True
                elif qLn.startswith("account_steamid="):
                    if not SD:
                        out.append(f"account_steamid={global_conf["SteamID"]}")
                        out.append("")
                        SD = True
                elif qLn.startswith("record_playtime="):
                    out.append(f"record_playtime=1")
                    out.append("")
                elif qLn.startswith("local_save_path="):
                    out.append(f"local_save_path=retLocalSaves")
                    out.append("")
                elif qLn.startswith("["):
                    out.append("")
                    out.append(qLn)
                else:
                    out.append(qLn)

            with open(cfg, "w") as x:
                x.write("\n".join(out))

            ST += 1
        return True