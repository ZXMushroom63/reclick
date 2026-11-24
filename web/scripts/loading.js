async function load_cfg(inCf) {
    const conf = inCf || (await window.pywebview.api.read_cfg());
    await update_nic_list();
    if (conf["NoShaders"]) {
        document.documentElement.classList.add("no_shaders");
        document.documentElement.style.setProperty("--hueOffset", "0deg");
    } else {
        document.documentElement.classList.remove("no_shaders");
        document.documentElement.style.setProperty("--hueOffset", conf["RetconHue"] + "deg");
    }
    Object.entries(conf).forEach((ent) => {
        const settingTarget = document.querySelector(
            `[data-setting="${ent[0]}"]`,
        );
        if (settingTarget) {
            settingTarget.set_value(ent[1]);
            settingTarget.onblur = () => {
                reload_cfg();
            };
            settingTarget.onkeydown = (e) => {
                if (e.key === "Enter") {
                    settingTarget.blur();
                }
            };
            settingTarget.oninput = (e) => {
                if (settingTarget.type === "checkbox") {
                    settingTarget.blur();
                }
            };
        }
    });
    lastLoadedConf = conf;
    redraw_games();
    return conf;
}
async function reload_cfg(inCf) {
    const conf = inCf || (await window.pywebview.api.read_cfg());
    [...document.querySelectorAll(`[data-setting]`)].forEach(
        (setting) => {
            conf[setting.getAttribute("data-setting")] =
                setting.get_value();
        },
    );
    console.log(conf);
    const newCf = await window.pywebview.api.write_cfg(conf);
    await load_cfg(newCf);
    return conf;
}