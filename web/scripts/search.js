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
document.addEventListener("keydown", (e)=>{
    if ((e.key.length !== 1) || e.ctrlKey || e.altKey || e.metaKey) {
        return;
    }
    if (![window, document.documentElement, document.body].includes(e.target)) {
        return;
    }
    e.preventDefault();
    searchbox.focus();
    searchbox.value = e.key;
    searchbox.dispatchEvent(new InputEvent("input"));
});