:: WIPE
netsh advfirewall firewall delete rule name="GSE_TCP_1"
netsh advfirewall firewall delete rule name="GSE_TCP_2"
netsh advfirewall firewall delete rule name="GSE_UDP_1"
netsh advfirewall firewall delete rule name="GSE_UDP_2"

:: INJECT
netsh advfirewall firewall add rule name="GSE_TCP_1" dir=in action=allow protocol=tcp localport=47584 remoteport=any remoteip=any enable=yes
netsh advfirewall firewall add rule name="GSE_TCP_2" dir=out action=allow protocol=tcp localport=47584 remoteport=any remoteip=any enable=yes
netsh advfirewall firewall add rule name="GSE_UDP_1" dir=in action=allow protocol=udp localport=47584 remoteport=any remoteip=any enable=yes
netsh advfirewall firewall add rule name="GSE_UDP_2" dir=out action=allow protocol=udp localport=47584 remoteport=any remoteip=any enable=yes

:: CHECK
netsh advfirewall firewall show rule name="GSE_TCP_1"
netsh advfirewall firewall show rule name="GSE_TCP_2"
netsh advfirewall firewall show rule name="GSE_UDP_1"
netsh advfirewall firewall show rule name="GSE_UDP_2"