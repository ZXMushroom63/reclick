@echo off
.\retconlib\holepunch_port.bat
route -p delete 255.255.255.255
route -p add 255.255.255.255 mask 255.255.255.255 %0 metric 10