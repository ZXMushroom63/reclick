# CLR Hook
This is a Frida hook that disables CLR verification in .NET apps such as Photon.

You can then modify DLLs get custom functionality.
For photon server v5, retcon4 automatically launches via `frida -f ".\PhotonSocketServer.exe" -l hook.js -- /run LoadBalancing` and expects `frida-tools` to be installed.