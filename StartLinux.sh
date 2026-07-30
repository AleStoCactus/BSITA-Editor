#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# 0. Terminal Spawner Check
# If not running in a terminal (tty), spawn a terminal emulator and rerun self.
# -----------------------------------------------------------------------------
if [ ! -t 0 ] && [ -z "$SPAWNED_IN_TERM" ]; then
    export SPAWNED_IN_TERM=1
    SCRIPT_PATH="$(readlink -f "$0")"

    # List of common terminal emulators to try
    TERMINALS=(
        "konsole -e"
        "gnome-terminal --"
        "xfce4-terminal -e"
        "kitty"
        "alacritty -e"
        "foot"
        "xterm -e"
    )

    for term in "${TERMINALS[@]}"; do
        term_bin=$(echo "$term" | awk '{print $1}')
        if command -v "$term_bin" &> /dev/null; then
            exec $term "$SCRIPT_PATH" "$@"
        fi
    done

    echo "Error: Could not find a supported terminal emulator."
    exit 1
fi

# Exit immediately if a command exits with a non-zero status
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== BSITA EDITOR Launcher ==="

# -----------------------------------------------------------------------------
# 1. Distro Detection & Package Management
# -----------------------------------------------------------------------------
install_packages() {
    local packages=("$@")

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
        DISTRO_LIKE=${ID_LIKE:-""}
    else
        echo "Error: Cannot detect Linux distribution (/etc/os-release missing)."
        exit 1
    fi

    echo "--> Missing packages detected: ${packages[*]}"

    # Arch Linux / EndeavourOS / Manjaro
    if [[ "$DISTRO_ID" =~ ^(arch|endeavouros|manjaro)$ ]] || [[ "$DISTRO_LIKE" =~ "arch" ]]; then
        echo "--> Arch-based distro detected ($NAME). Installing via pacman..."
        sudo pacman -S --needed --noconfirm "${packages[@]}"

    # Debian / Ubuntu / Pop!_OS / Mint
    elif [[ "$DISTRO_ID" =~ ^(ubuntu|debian|pop|linuxmint)$ ]] || [[ "$DISTRO_LIKE" =~ "debian" ]]; then
        echo "--> Debian/Ubuntu-based distro detected ($NAME). Installing via apt..."
        sudo apt update
        sudo apt install -y "${packages[@]}"

    # Fedora / RHEL
    elif [[ "$DISTRO_ID" =~ ^(fedora|rhel|centos)$ ]] || [[ "$DISTRO_LIKE" =~ "fedora" ]]; then
        echo "--> Fedora-based distro detected ($NAME). Installing via dnf..."
        sudo dnf install -y --allow-erasing "${packages[@]}"

    else
        echo "Error: Unsupported distribution ($NAME). Please install ${packages[*]} manually."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# 2. Dependency Checks (Python & FFmpeg)
# -----------------------------------------------------------------------------
MISSING_PKGS=()

if ! command -v python3 &> /dev/null; then
    MISSING_PKGS+=("python")
fi

if ! command -v ffmpeg &> /dev/null; then
    MISSING_PKGS+=("ffmpeg")
fi

# Check for python3-venv / python-virtualenv on Debian/Ubuntu systems
if command -v apt &> /dev/null && ! dpkg -l | grep -q python3-venv; then
    MISSING_PKGS+=("python3-venv")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    install_packages "${MISSING_PKGS[@]}"
fi

# -----------------------------------------------------------------------------
# 3. Virtual Environment Setup
# -----------------------------------------------------------------------------
if [ ! -d ".venv" ]; then
    echo "--> Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "--> Virtual environment (.venv) already exists."
fi

# Activate virtual environment
echo "--> Activating virtual environment..."
# shellcheck source=/dev/null
source .venv/bin/activate

# -----------------------------------------------------------------------------
# 4. Pip Dependencies
# -----------------------------------------------------------------------------
echo "--> Checking/upgrading Python dependencies..."
pip install --upgrade pip --quiet
pip install --upgrade pillow eel moviepy gdown --quiet

# -----------------------------------------------------------------------------
# 5. Launch
# -----------------------------------------------------------------------------
echo "--> Starting BSITA EDITOR..."
echo "======================================"
python main.py

# Keep window open if python exits/crashes so you can read logs
echo ""
echo "Program finished. Press Enter to close..."
read -r