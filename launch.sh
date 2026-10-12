if [ -d updated ]; then
    cp updated/* .
    echo "Installed update."
    sleep 0.5
    rm -r updated
fi
python app.py