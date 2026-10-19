cd /home/zxmushroom63/Documents/LegallyAcquiredFiles/RECLICK
if [ -d updated ]; then
    cp updated/* .
    echo "Installed update."
    sleep 0.5
    rm -r updated
fi
python reclick.py $1
