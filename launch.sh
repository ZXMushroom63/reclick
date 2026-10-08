if [ -d updated ]; then
    cp updated/* .
    echo "Installed update."
    sleep 0.5
fi
rm -r updated
python app.py