@echo off
(
    :: load into memory
    echo Updating to latest retcon4 patch from github...
    curl -L "https://github.com/ZXMushroom63/retcon4/archive/refs/heads/main.zip" -o "reclick.zip"
    tar -xf "reclick.zip"
    del "reclick.zip"
    rd /s /q "lib"
    rd /s /q "web"
    robocopy "retcon4-main" . /E /IS /IT /R:3 /W:5
    rd /s /q "retcon4-main"
    mkdir stuff
    echo Updated successfully!
    TIMEOUT 3
)