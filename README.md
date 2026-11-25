# RECLICK
All-in-one userfriendly GUI for GSE/GBE games, automatically managing Photon for you.

- needs python 3.14 or newer
- you need these packages:
    - pywebview
    - psutil

- FRIDA SUPPORT
    - `python -m pip install frida-tools` (used for CLR hooking)

- Features:
    - autodetects games and their features
    - automatically handles usernames and userIDs
    - easy VLAN fixes for windows (instant firewall rules, broadcast routing)
    - linux and windows support
    - one-click self-hosting for photon v4 and v5
        - photon v5 requires the python frida-tools package to be installed
        - photon v5 does not work on linux for now
        - photon v4 on linux requires .NET from microsoft to be installed (winetricks recommended)
    - autopatches PhotonServerSettings
    - custom vulkan icd settings on linux
- Todo: 
    - Autopatch PhotonRedirector