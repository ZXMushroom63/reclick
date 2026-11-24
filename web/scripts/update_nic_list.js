const ignorelist = ["vmware", "virtual", "vm", "vir"];
const nameMapping = {
    ham: "Hamachi",
    wlp: "WiFi",
    wlan: "WiFi",
    eth: "Ethernet",
    en: "Ethernet",
    lo: "Local",
};
async function update_nic_list(inCf) {
    const conf = inCf || (await window.pywebview.api.read_cfg());
    const targetAddress = conf["HostAddress"];
    const nics = await window.pywebview.api.get_nics();
    const dropdown = document.querySelector(
        "[data-setting=HostAddress]",
    );
    dropdown.innerHTML = "";
    Object.entries(nics).forEach((ent) => {
        let rawName = ent[0];
        let chkName = ent[0].toLowerCase();
        let displayName = ent[0];
        const addresses = ent[1];
        for (let i = 0; i < ignorelist.length; i++) {
            if (chkName.includes(ignorelist[i])) {
                return;
            }
        }
        Object.entries(nameMapping).forEach((mapper) => {
            if (chkName.startsWith(mapper[0])) {
                displayName = mapper[1];
            }
        });
        addresses.forEach((addr) => {
            const opt = document.createElement("option");
            opt.value = addr;
            opt.innerText = `${displayName}: ${addr}`;
            opt.selected = targetAddress === addr;
            dropdown.appendChild(opt);
        });
    });
}