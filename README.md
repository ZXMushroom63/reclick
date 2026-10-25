# RECLICK
All-in-one userfriendly GUI for GSE/GBE games, automatically managing Photon for you.

- needs python 3.14 or newer
- you need these packages:
    - pywebview
    - psutil
    - requests

- FRIDA SUPPORT
    - `python -m pip install frida-tools` (used for CLR hooking)

- Features so far:
    - really cool visual style
    - autodetects games and their features
    - automatically handles usernames and userIDs
    - easy VLAN fixes for windows (instant firewall rules, broadcast routing, apilib unfirewalling)
    - linux and windows support (for games and photon server v4)
        - photon v4 on linux requires .NET from microsoft to be installed (winetricks recommended)
- Todo: 
    - Photon v5 support (maybe with Frida hooking on linux to bypass platform checks?)
    - Autopatch PhotonRedirector and PhotonServerSettings
    - Username setting
    - Better settings GUI
    - BepInEx modloader toggle
    - settings toggle
    - add options for per-game launch settings
    - add Vulkan ICD file options