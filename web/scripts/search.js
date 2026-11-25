// Source - https://stackoverflow.com/a/35279162
// Posted by gustf, modified by community. See post 'Timeline' for change history
// Retrieved 2026-11-25, License - CC BY-SA 3.0
function levenshtein(s, t) {
    if (s === t) {
        return 0;
    }
    var n = s.length, m = t.length;
    if (n === 0 || m === 0) {
        return n + m;
    }
    var x = 0, y, a, b, c, d, g, h;
    var p = new Uint16Array(n);
    var u = new Uint32Array(n);
    for (y = 0; y < n;) {
        u[y] = s.charCodeAt(y);
        p[y] = ++y;
    }

    for (; (x + 3) < m; x += 4) {
        var e1 = t.charCodeAt(x);
        var e2 = t.charCodeAt(x + 1);
        var e3 = t.charCodeAt(x + 2);
        var e4 = t.charCodeAt(x + 3);
        c = x;
        b = x + 1;
        d = x + 2;
        g = x + 3;
        h = x + 4;
        for (y = 0; y < n; y++) {
            a = p[y];
            if (a < c || b < c) {
                c = (a > b ? b + 1 : a + 1);
            }
            else {
                if (e1 !== u[y]) {
                    c++;
                }
            }

            if (c < b || d < b) {
                b = (c > d ? d + 1 : c + 1);
            }
            else {
                if (e2 !== u[y]) {
                    b++;
                }
            }

            if (b < d || g < d) {
                d = (b > g ? g + 1 : b + 1);
            }
            else {
                if (e3 !== u[y]) {
                    d++;
                }
            }

            if (d < g || h < g) {
                g = (d > h ? h + 1 : d + 1);
            }
            else {
                if (e4 !== u[y]) {
                    g++;
                }
            }
            p[y] = h = g;
            g = d;
            d = b;
            b = c;
            c = a;
        }
    }

    for (; x < m;) {
        var e = t.charCodeAt(x);
        c = x;
        d = ++x;
        for (y = 0; y < n; y++) {
            a = p[y];
            if (a < c || d < c) {
                d = (a > d ? d + 1 : a + 1);
            }
            else {
                if (e !== u[y]) {
                    d = c + 1;
                }
                else {
                    d = c;
                }
            }
            p[y] = d;
            c = a;
        }
        h = d;
    }

    return h;
}


const searchbox = document.querySelector("#gamesearch");
function sort_games() {
    let search = searchbox.value.toLowerCase().trim();
    let working_games = Object.assign({}, games);
    let kvlist = [];
    Object.entries(working_games).forEach(ent => {
        kvlist.push({
            k: ent[0],
            v: ent[1],
            i: ent[1]["Settings"]["DisplayName"] || ent[1]["Name"]
        })
    });
    if (search) {
        //levenshtein sort, substring, prefix
        kvlist.sort((a, b)=>{
            return levenshtein(search, a.i.toLowerCase()) - levenshtein(search, b.i.toLowerCase());
        });
        kvlist.sort((a, b)=>{
            return b.i.toLowerCase().includes(search) - a.i.toLowerCase().includes(search);
        });
        kvlist.sort((a, b)=>{
            return b.i.toLowerCase().startsWith(search) - a.i.toLowerCase().startsWith(search);
        });
        games = {};
        kvlist.forEach(kv => {
            games[kv.k] = kv.v;
        });
    } else {
        //alphabetically sort
        const kvmap = kvlist.map(kv => {
            const wstr = Object(kv.i);
            wstr.kv_entry = kv;
            return wstr;
        });
        kvmap.sort();
        games = {};
        kvmap.forEach(wstr => {
            games[wstr.kv_entry.k] = wstr.kv_entry.v;
        });
    }
}
searchbox.addEventListener("input", ()=>{
    sort_games();
    redraw_games();
});
let lastLaunchKeyb = Date.now();
searchbox.addEventListener("keydown", (e)=>{
    if (e.key === "Enter" && searchbox.value.trim() !== "") {
        const target = Object.keys(games)[0];
        const now = Date.now();
        if (target && buttonMaps.has(target) && (now - lastLaunchKeyb) > 150) {
            buttonMaps.get(target)[0].click();
            lastLaunchKeyb = now;
        }
    }
});
window.addEventListener("keydown", (e)=>{
    if ((e.key.length !== 1) || e.ctrlKey || e.altKey || e.metaKey) {
        return;
    }
    if (![window, document.documentElement, document.body].includes(e.target) && !["SELECT", "BUTTON"].includes(e.target.tagName)) {
        return;
    }
    e.preventDefault();
    e.stopPropagation();
    searchbox.focus();
    searchbox.value = e.key;
    searchbox.dispatchEvent(new InputEvent("input"));
}, true);

window.addEventListener("keydown", (e)=>{
    if (![window, document.documentElement, document.body].includes(e.target) && !["SELECT", "BUTTON"].includes(e.target.tagName)) {
        return;
    }
    if (e.key === "Enter" && e.shiftKey) {
        return buttonMaps.get(selectedGame)[0].click();
    }
    if (!["ArrowUp", "ArrowDown", "ArrowRight", "PageUp"].includes(e.key)) {
        return;
    }
    e.preventDefault();
    e.stopPropagation();
    const keys = Object.keys(games);
    if (e.key === "ArrowUp") {
        selectedGame = keys[Math.max(0, keys.indexOf(selectedGame) - 1)];
    } else if (e.key === "ArrowDown") {
        selectedGame = keys[Math.min(keys.length-1,keys.indexOf(selectedGame) + 1)];
    } else {
        selectedGame = keys[0];
    }
    const newIndex = keys.indexOf(selectedGame);
    redraw_games();
    const cont = document.querySelector("#left");
    cont.scrollTop = (document.querySelector(".game.selected").offsetTop + 33 + 16) - (cont.clientHeight / 2);
    // base 16px + serch 32px - each(1px border + 8px padding + 24px content - 16px? margin)
}, true);