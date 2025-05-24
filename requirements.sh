#!/bin/bash
echo "Installing NovaPlayer dependencies..."
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv python3-tk \
    ffmpeg build-essential git
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pillow requests psutil
chmod +x src/novaplayer.py
mkdir -p ~/Opnames
echo "Installation complete!"
echo "Usage: source venv/bin/activate && python3 src/novaplayer.py, but for now we activated the venv"
