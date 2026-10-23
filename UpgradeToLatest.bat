@echo off
(
    :: load into memory
    echo Updating to latest reclick patch from github...
    curl -L "https://github.com/ZXMushroom63/reclick/archive/refs/heads/main.zip" -o "reclick.zip"
    tar -xf "reclick.zip"
    del "reclick.zip"
    robocopy "reclick-main" . /E /IS /IT /R:3 /W:5
    rd /s /q "reclick-main"
    mkdir PLAYLIST
    echo Updated successfully!
    TIMEOUT 3
)