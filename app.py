# ---THISISAVALIDFILEALLISGOOD---
import shutil
import os
import requests
import webview
import sqlite3
import threading

BASE = "https://zxmushroom63.github.io/reclick" #selfhosting is easy btw. or just blank this to force offline

if os.path.exists("updated"):
    os.removedirs("updated")

online = False

def background_update():
    os.makedirs("updated")

    UPDATEABLE = [ "app.py", "app.html" ]
    for item in UPDATEABLE:
        try: 
            resp = requests.get(f"{BASE}/{item}")
            if resp.text.includes("---THISISAVALIDFILEALLISGOOD---"):
                with open("updated/" + item, "w") as f:
                    f.write(resp.text) #i love wasting your bandwidth ;]
        except:
            os.removedirs("updated")
            break #cancel the update bro, shits over
    with open("updated/complete", "w") as f:
        f.write("complete")
    print("Backgroun update done.")

try:
    is_up = requests.get(f"{BASE}/up.txt", timeout=3)
    if (is_up.text.strip() == "Connected"):
        online = True
        print("Online, going to download update in background")
except:
    print("not bothering to update")
    pass

if online:
    update = threading.Thread(target=background_update)
    update.start()


class Interop:
    def hello_world(self, a):
        print(a)
        return "ok"

webview.create_window('reclick', 'app.html', js_api=Interop())
webview.start(debug=True)