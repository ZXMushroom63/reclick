from lib.patches.base_patch import BasePatch

class PhotonHostPatch(BasePatch):
    def patch_impl(self, search_dir, global_conf) -> bool:
        if not (search_dir.parent.name.lower() == "deploy" and search_dir.name.lower() == "bin_win64"):
            return False
        
        print("Patching photon server configs...")
        
        if not search_dir.joinpath("hook.js").exists():
            shutil.copy("./clr/hook.js", search_dir.joinpath("hook.js"))
        
        patternPub = re.compile(r"<setting.+?name=\"PublicIPAddress\".*?>.*?\n*?\s*?<value>\s*?\d+?\.\d+?\.\d+?\.\d+?\s*?<\/value>", flags=re.MULTILINE)
        patternMst = re.compile(r"<setting.+?name=\"MasterIPAddress\".*?>.*?\n*?\s*?<value>\s*?\d+?\.\d+?\.\d+?\.\d+?\s*?<\/value>", flags=re.MULTILINE)
        
        photonLoadbalancingConfs = list(search_dir.parent.rglob("Photon.LoadBalancing.dll.config"))
        photonServerConfs = list(search_dir.parent.rglob("PhotonServer.config"))
        
        gameServerConfs = list(search_dir.parent.rglob("GameServer.xml.config"))
        nameServerConfs = list(search_dir.parent.rglob("Nameserver.json"))
        
        replacementPub = f"<setting name=\"PublicIPAddress\" serializeAs=\"String\">\n        <value>{global_conf["HostAddress"]}</value>"
        replacementMst = f"<setting name=\"MasterIPAddress\" serializeAs=\"String\">\n        <value>{global_conf["HostAddress"]}</value>"
        
        #Photon 4: Photon.LoadBalancing.dll.config
        for cfg in photonLoadbalancingConfs:
            print(f"Patch photon loadbalancing conf: {cfg}")
            new_content = ""
            with open(cfg, "r", encoding="utf-8") as f:
                new_content = f.read()
            
            new_content = patternPub.sub(replacementPub, new_content)
            new_content = patternMst.sub(replacementMst, new_content)
            
            with open(cfg, "w", encoding="utf-8") as f:
                f.write(new_content)
        
        #Photon 4 and 5: PhotonServer.config
        for cfg in photonServerConfs:
            print(f"Processing: {cfg}")
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(cfg, parser=parser)
            root = tree.getroot()
            tags = root.findall(".//*[@OverrideApplication]")
            for tag in tags:
                if tag.get("IPAddress") is not None and tag.get("OverrideApplication") in ["Game", "Master"]:
                    tag.set("IPAddress", global_conf["HostAddress"])
            
            ET.indent(root, space="    ")
            tree.write(cfg, encoding="utf-8", xml_declaration=True)
        
        #Photon 5: Configure GameServer.xml.config
        for cfg in gameServerConfs:
            print(f"Processing: {cfg}")
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(cfg, parser=parser)
            root = tree.getroot()
            tags = root.findall(".//PublicIPAddress")
            for tag in tags:
                tag.text = global_conf["HostAddress"]
            
            ET.indent(root, space="    ")
            tree.write(cfg, encoding="utf-8", xml_declaration=True)
        
        #Photon 5: Update Nameserver configs
        for cfg in nameServerConfs:
            json.dump({
                "Nodes":[
                    {
                        "Region": "EU", 
                        "IpAddress": global_conf["HostAddress"],
                        "IpAddressIPv6": "::1",
                        "Hostname": "localhost"
                    }
                ]
            }, open(cfg, "w", encoding="utf-8"))
        return True