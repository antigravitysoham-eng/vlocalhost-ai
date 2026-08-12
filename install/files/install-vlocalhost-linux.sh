#!/bin/bash
# Vlocalhost.AI installer for Linux.
#
#   bash install-vlocalhost-linux.sh
#
# Installs into your home directory. The only step that may ask for your
# password is the system audio library, and it is skipped if already present.

set -u

VERSION="1.0.5"
SUPPORT="https://antigravitysoham-eng.github.io/vlocalhost-ai/support/"
URL="https://github.com/antigravitysoham-eng/vlocalhost-core/archive/refs/tags/v${VERSION}.tar.gz"
ROOT="$HOME/.local/share/vlocalhost"
APP="$ROOT/vlocalhost-core-${VERSION}"
LOG="$ROOT/install-log.txt"
TARBALL="$(mktemp --suffix=.tar.gz 2>/dev/null || mktemp)"

bold=$(printf '\033[1m'); dim=$(printf '\033[2m'); off=$(printf '\033[0m')

say()  { printf '   %s\n' "$*"; }
step() { printf '\n   %s%s%s\n' "$bold" "$*" "$off"; }
die()  { printf '\n   [X] %s\n\n' "$*";
         printf '   Details:  %s\n' "$LOG"
         printf '   Get help: %s\n\n' "$SUPPORT"; exit 1; }

printf '\n   %sVlocalhost.AI%s\n' "$bold" "$off"
printf '   %sMeeting notes that never leave your machine%s\n' "$dim" "$off"
printf '   ==========================================\n\n'

# ----------------------------------------------------------------- Python
step "[1/6] Looking for Python 3.9+ ..."
PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' 2>/dev/null; then
            PY="$candidate"; break
        fi
    fi
done
[ -n "$PY" ] || die "Python 3.9 or newer was not found.
       Debian/Ubuntu:  sudo apt install python3 python3-venv
       Fedora/RHEL:    sudo dnf install python3"
say "Found $("$PY" --version 2>&1)."

# ------------------------------------------------- system audio + tray dep
step "[2/6] Checking the microphone backend ..."
if ldconfig -p 2>/dev/null | grep -q libportaudio; then
    say "PortAudio already present."
elif command -v apt-get >/dev/null 2>&1; then
    say "Installing libportaudio2 (you may be asked for your password) ..."
    sudo apt-get update -qq && sudo apt-get install -y libportaudio2 \
        || say "Could not install it - the microphone may not work."
elif command -v dnf >/dev/null 2>&1; then
    say "Installing portaudio (you may be asked for your password) ..."
    sudo dnf install -y portaudio || say "Could not install it - the mic may not work."
else
    say "Unknown package manager. Install PortAudio yourself if the mic fails."
fi
if ! python3 -c "import gi" >/dev/null 2>&1; then
    say "Optional: for a system-tray icon, install gir1.2-appindicator3-0.1."
    say "Without it the app falls back to terminal mode automatically."
fi

# ---------------------------------------------------------------- Download
step "[3/6] Downloading Vlocalhost ${VERSION} ..."
mkdir -p "$ROOT" || die "Could not create $ROOT"
printf 'Vlocalhost installer %s\n' "$(date)" > "$LOG"
rm -rf "$APP"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" -o "$TARBALL" || die "Download failed. Check your connection."
elif command -v wget >/dev/null 2>&1; then
    wget -q "$URL" -O "$TARBALL" || die "Download failed. Check your connection."
else
    die "Neither curl nor wget is installed. Install one and try again."
fi
tar -xzf "$TARBALL" -C "$ROOT" || die "Could not unpack the download."
rm -f "$TARBALL"
[ -f "$APP/vlocalhost.py" ] || die "The download did not contain what we expected."

# ------------------------------------------------------------ Environment
step "[4/6] Setting up a private Python environment ..."
"$PY" -m venv "$APP/.venv" || die "Could not create the Python environment.
       Debian/Ubuntu may need:  sudo apt install python3-venv"
VPY="$APP/.venv/bin/python"
"$VPY" -m pip install --upgrade pip --disable-pip-version-check >>"$LOG" 2>&1
"$VPY" -m pip install -r "$APP/requirements.txt" --disable-pip-version-check >>"$LOG" 2>&1 \
    || die "Could not install the dependencies."

# ---------------------------------------------------------------- Ollama
step "[5/6] Checking Ollama (for written summaries) ..."
if command -v ollama >/dev/null 2>&1; then
    say "Fetching the summary model - this can take a few minutes ..."
    ollama pull llama3.2 || say "Model download failed; you can retry later."
else
    say "Ollama is not installed. Recording and transcription will work"
    say "without it, but written summaries need it."
    say "Get it from https://ollama.com/download then run: ollama pull llama3.2"
fi

# --------------------------------------------------------------- Shortcut
step "[6/6] Adding Vlocalhost to your applications menu ..."
(cd "$APP" && "$VPY" vlocalhost.py --install-shortcut)

printf '\n   ==========================================\n'
printf '   %sDone.%s Find Vlocalhost.AI in your applications\n' "$bold" "$off"
printf '   menu, or on your desktop, and click it.\n'
printf '   ==========================================\n\n'
say "If the desktop icon needs it, right-click and choose 'Allow launching'."
printf '\n   Open Vlocalhost now? [y/N] '
read -r answer
case "$answer" in
    [yY]*) ("$VPY" "$APP/vlocalhost.py" >/dev/null 2>&1 &) ; say "Starting ..." ;;
esac
printf '\n'
