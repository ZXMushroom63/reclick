# Photon5IL2CPP Runtime nameserver patcher mod
This is a BepInEx 6.0.0 IL2CPP mod that allows you to replace the nameserver target IP.
- Put FridaLoader.dll in the BepInEx plugins folder
- Place gadget.config, gadget.dll, and photonhook.js next to the game executable
- On first launch with the mod, `needs_photoncpp_address.txt` is created in the game folder.
- You can edit it to target a different photon nameserver.
- Note! Most IL2CPP photon games use Photon Fusion, which cannot yet be self-hosted.