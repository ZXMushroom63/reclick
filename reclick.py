# ---THISISAVALIDFILEALLISGOOD---
import shutil
import sys
import os
import requests
import webview
import pathlib
import glob
import threading

sys.path.append(os.path.dirname(os.path.abspath("."))) #fix imports
import packaging

BASE = "https://zxmushroom63.github.io/reclick" #selfhosting is easy btw. or just blank this to force offline

if os.path.exists("updated"):
    os.removedirs("updated")

ENABLE_AUTOUPDATE = False

def background_update():
    is_up = False
    try:
        is_up = requests.get(f"{BASE}/up.txt", timeout=3)
        if (is_up.text.strip() == "Connected"):
            is_up = True
            print("Online, going to download update in background")
    except:
        print("not boaate")
    if not is_up:
        return
    
    os.makedirs("updated")

    UPDATEABLE = [ "reclick.py", "app.html", "packaging.py" ]
    for item in UPDATEABLE:
        try: 
            resp = requests.get(f"{BASE}/{item}")
            if "---THISISAVALIDFILEALLISGOOD---" in resp.text:
                with open("updated/" + item, "w") as f:
                    f.write(resp.text) #i love wasting your bandwidth ;]
        except Exception as e:
            os.removedirs("updated")
            print(f"update failed: {e}")
            return #cancel the update bro, shits over
    with open("updated/complete", "w") as f:
        f.write("complete")
    print("Backgroun update done.")

if ENABLE_AUTOUPDATE:
    update = threading.Thread(target=background_update)
    update.start()

class Interop:
    def get_library(self, a):
        print(a)
        return "ok"


class DatabaseCalls:
    def nil(self):
        pass


window = webview.create_window('reclick', 'app.html', js_api=Interop(), frameless=False)
webview.start(debug=False)