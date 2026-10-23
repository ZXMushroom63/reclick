@echo off
setlocal enabledelayedexpansion

set "SUBDIR=updated"

if exist "%SUBDIR%" (
    robocopy "%SUBDIR%" "." /E /MT:8 /R:1 /W:1
    echo "Installed update!"
    TIMEOUT 1
    RMDIR /S /Q "%SUBDIR%"
)
start "" pythonw.exe reclick.py
exit