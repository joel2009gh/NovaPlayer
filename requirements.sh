#!/bin/bash

# NovaPlayer Installation Script
# This script installs all dependencies and sets up NovaPlayer

set -e  # Exit on any error

echo "============================================"
echo "    NovaPlayer Installation Script"
echo "============================================"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Do not run this script as root (without sudo)"
   echo "Run it as a regular user, it will ask for sudo when needed."
   exit 1
fi

# Check if we're in the right directory
if [[ ! -f "novaplayer.py" && ! -f "src/novaplayer.py" ]]; then
    print_warning "novaplayer.py not found in current directory or src/ folder"
    print_warning "Make sure you're in the NovaPlayer directory"
fi

print_status "Starting NovaPlayer installation..."
echo

# Update package list
print_status "Updating package list..."
sudo apt update

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    ffmpeg \
    vlc \
    build-essential \
    git \
    curl \
    wget

# Check if virtual environment already exists
if [[ -d "venv" ]]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python packages..."
pip install pillow requests psutil

# Create recordings directory
print_status "Creating recordings directory..."
mkdir -p ~/Opnames

# Make Python script executable
if [[ -f "novaplayer.py" ]]; then
    chmod +x novaplayer.py
    SCRIPT_PATH="novaplayer.py"
elif [[ -f "src/novaplayer.py" ]]; then
    chmod +x src/novaplayer.py
    SCRIPT_PATH="src/novaplayer.py"
else
    print_warning "novaplayer.py not found, skipping chmod"
    SCRIPT_PATH="novaplayer.py"
fi

# Create desktop entry (optional)
print_status "Creating desktop shortcut..."
DESKTOP_FILE="$HOME/.local/share/applications/novaplayer.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NovaPlayer
Comment=Stream URL Player and Recorder
Exec=$PWD/venv/bin/python $PWD/$SCRIPT_PATH
Icon=multimedia-player
Terminal=false
Categories=AudioVideo;Player;
EOF

# Create convenience launch script
print_status "Creating launch script..."
cat > "start_novaplayer.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 novaplayer.py "$@"
EOF

chmod +x start_novaplayer.sh

# Create launcher for recordings folder
cat > "open_recordings.sh" << 'EOF'
#!/bin/bash
xdg-open ~/Opnames 2>/dev/null || nautilus ~/Opnames 2>/dev/null || echo "Recordings folder: ~/Opnames"
EOF

chmod +x open_recordings.sh

echo
echo "============================================"
print_status "Installation completed successfully!"
echo "============================================"
echo
print_status "Virtual environment is now activated."
print_status "Recordings will be saved to: ~/Opnames"
echo
echo "Usage options:"
echo
echo "1. Direct execution (venv already activated):"
echo "   python3 $SCRIPT_PATH"
echo
echo "2. Using the launcher script:"
echo "   ./start_novaplayer.sh"
echo
echo "3. With a stream URL:"
echo "   ./start_novaplayer.sh https://icecast.omroep.nl/radio1-bb-mp3"
echo
echo "4. Headless mode with auto-recording:"
echo "   ./start_novaplayer.sh https://icecast.omroep.nl/radio1-bb-mp3 --headless --record"
echo
echo "5. Open recordings folder:"
echo "   ./open_recordings.sh"
echo
echo "To activate the virtual environment manually in the future:"
echo "   source venv/bin/activate"
echo
print_status "You can now test NovaPlayer with a Dutch radio stream!"

# Test if everything works
echo
read -p "Do you want to test NovaPlayer now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Testing NovaPlayer with NPO Radio 1..."
    python3 $SCRIPT_PATH https://icecast.omroep.nl/radio1-bb-mp3
fi
