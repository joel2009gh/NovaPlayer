# NovaPlayer

A Python-based audio stream player with simultaneous recording capabilities, featuring both GUI and headless modes for live streaming and archival purposes.

## Features

- Play audio streams from URLs
- Record streams while playing
- GUI and headless (command-line) modes
- Automatic filename generation with Dutch date formatting
- Support for various stream formats (MP3, AAC, M3U8, etc.)

### Installation & System Requirements
First, update your system:
sudo apt update
Once you have done that, use git clone https://github.com/joel2009gh/NovaPlayer
Then, cd into the directory:
cd NovaPlayer
Next, make the requirements.sh file executable:
chmod +x requirements.sh
Then run it:
./requirements.sh


If you want an desktop entry:

```bash
sudo mkdir -p /usr/local/share/icons

sudo cp assets/NovaPlayer.jpg /usr/local/share/icons/novaplayer.jpg

mkdir -p ~/.local/share/applications
```

```bash
cat > ~/.local/share/applications/novaplayer.desktop << EOF
[Desktop Entry]
Name=NovaPlayer
Comment=Audio Stream Player and Recorder
Exec=/usr/local/bin/novaplayer
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Player;
EOF
```
