# NovaPlayer 🎵

A modern, feature-rich stream player and recorder built with Python and VLC. NovaPlayer allows you to play audio streams and record them with automatic reconnection capabilities and a sleek GUI.

![NovaPlayer](assets/NovaPlayer.png)

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Features ✨

- **Stream Playback**: Play audio streams using VLC's powerful engine
- **Recording**: Record streams to MP3 format with customizable filenames
- **Auto-Reconnection**: Automatically reconnects when stream connection is lost
- **GUI & Headless Mode**: Use with a modern dark-themed GUI or run headless for automation
- **Configurable**: JSON-based configuration for easy customization
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Dutch Localization**: Built-in support for Dutch date formatting

### Main Interface
The clean, modern interface makes it easy to play and record streams:

- Dark theme for comfortable viewing
- Real-time status updates
- One-click recording
- Automatic reconnection with retry counter

### Quick Install (Linux/Ubuntu)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joel2009gh/NovaPlayer
   cd NovaPlayer
   ```

2. **Run the installation script:**
   ```bash
   chmod +x requirements.sh
   ./requirements.sh
   ```

3. **Start using NovaPlayer:**
   ```bash
   ./start_novaplayer.sh
   ```
   

   ## Usage 💡

### GUI Mode
But first activate the virtual env: python3 venv/bin/activate
```bash
# Basic usage
python3 novaplayer.py

# With a stream URL
python3 novaplayer.py "https://icecast.omroep.nl/radio1-bb-mp3"

# Using the launcher script
./start_novaplayer.sh "https://your-stream-url.com/stream"
```

### Headless Mode
Perfect for automation and server deployments:

```bash
# Headless playback
python3 novaplayer.py "https://stream-url.com" --headless

# Headless with auto-recording
python3 novaplayer.py "https://stream-url.com" --headless --record
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `url` | Stream URL to play (optional) |
| `--headless` | Run without GUI |
| `--record` | Automatically start recording |

## Configuration ⚙️

NovaPlayer uses a `config.json` file for customization:

```json
{
    "filename_prefix": "My Recording",
    "max_retries": 10,
    "retry_delay": 5,
    "recordings_dir": "~/Opnames"
}
```

### Configuration Options

- **filename_prefix**: Prefix for recorded files (default: "example")
- **max_retries**: Maximum reconnection attempts (default: 10)
- **retry_delay**: Seconds between reconnection attempts (default: 5)
- **recordings_dir**: Directory for recordings (default: "~/Opnames")

## File Naming 📁

Recordings are automatically named using Dutch date formatting:
```
[prefix] [day] [month] [time_of_day].mp3
```
Example:
- `My Show 23 december avond.mp3`

  ## Features in Detail 🔍

### Automatic Reconnection
- Detects connection drops
- Configurable retry attempts
- Progressive retry delays
- Status updates during reconnection

### Recording Features
- High-quality MP3 encoding (192kbps)
- Automatic file naming with timestamps
- Simultaneous playback and recording
- Recording status monitoring

### GUI Features
- Modern dark theme
- Real-time status updates
- Responsive design
- Error handling with user-friendly messages

## Troubleshooting 🔧

### Common Issues

**Permission errors:**
```bash
# Make sure the script is executable
chmod +x novaplayer.py
chmod +x start_novaplayer.sh
```

**Audio issues:**
```bash
cvlc "https://your-stream-url.com"
```

**Python dependencies:**
```bash
# Reinstall dependencies
pip3 install --upgrade pillow psutil
```

## Development 👨‍💻

### Project Structure
```
NovaPlayer/
├── novaplayer.py          # Main application
├── config.json           # Configuration file
├── install.sh            # Installation script
├── start_novaplayer.sh   # Launcher script
├── assets/               # Images and resources
│   └── NovaPlayer.png
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Test on multiple platforms


---
