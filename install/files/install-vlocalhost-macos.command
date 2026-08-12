#!/bin/bash
# Vlocalhost.AI installer for macOS.
# Double-click this file. If macOS refuses because it is from an
# "unidentified developer", right-click it and choose Open instead.

set -u

VERSION="1.0.4"
URL="https://github.com/antigravitysoham-eng/vlocalhost-core/archive/refs/tags/v${VERSION}.tar.gz"
ROOT="$HOME/Library/Application Support/Vlocalhost"
APP="$ROOT/vlocalhost-core-${VERSION}"
TARBALL="$(mktemp -t vlocalhost).tar.gz"

bold=$(printf '\033[1m'); dim=$(printf '\033[2m'); off=$(printf '\033[0m')

say()  { printf '   %s\n' "$*"; }
step() { printf '\n   %s%s%s\n' "$bold" "$*" "$off"; }
die()  { printf '\n   [X] %s\n\n' "$*"; printf '   Press return to close.'; read -r _; exit 1; }

clear
printf '\n   %sVlocalhost.AI%s\n' "$bold" "$off"
printf '   %sMeeting notes that never leave your machine%s\n' "$dim" "$off"
printf '   ==========================================\n\n'
say "Everything installs inside your own home folder."
say "No administrator password is needed."

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
       Install it from https://www.python.org/downloads/macos/
       then run this installer again."
say "Found $("$PY" --version 2>&1)."

# --------------------------------------------------------------- PortAudio
step "[2/6] Checking the microphone backend ..."
if command -v brew >/dev/null 2>&1; then
    if brew list portaudio >/dev/null 2>&1; then
        say "PortAudio already installed."
    else
        say "Installing PortAudio via Homebrew ..."
        brew install portaudio || say "Could not install PortAudio - the mic may not work."
    fi
else
    say "Homebrew not found. If the microphone does not work later, install"
    say "Homebrew from https://brew.sh then run:  brew install portaudio"
fi

# ---------------------------------------------------------------- Download
step "[3/6] Downloading Vlocalhost ${VERSION} ..."
mkdir -p "$ROOT" || die "Could not create $ROOT"
rm -rf "$APP"
curl -fsSL "$URL" -o "$TARBALL" || die "Download failed. Check your internet connection."
tar -xzf "$TARBALL" -C "$ROOT" || die "Could not unpack the download."
rm -f "$TARBALL"
[ -f "$APP/vlocalhost.py" ] || die "The download did not contain what we expected."

# ------------------------------------------------------------ Environment
step "[4/6] Setting up a private Python environment ..."
"$PY" -m venv "$APP/.venv" || die "Could not create the Python environment."
VPY="$APP/.venv/bin/python"
"$VPY" -m pip install --upgrade pip --quiet --disable-pip-version-check
"$VPY" -m pip install -r "$APP/requirements.txt" --quiet --disable-pip-version-check \
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
step "[6/6] Adding Vlocalhost to your Applications ..."
(cd "$APP" && "$VPY" vlocalhost.py --install-shortcut)

printf '\n   ==========================================\n'
printf '   %sDone.%s Open Vlocalhost.AI from Launchpad or\n' "$bold" "$off"
printf '   from the Applications folder in your home.\n'
printf '   ==========================================\n\n'
say "macOS will ask for microphone permission the first time - allow it."
printf '\n   Open Vlocalhost now? [y/N] '
read -r answer
case "$answer" in
    [yY]*) open "$HOME/Applications/Vlocalhost.AI.app" 2>/dev/null \
               || ("$VPY" "$APP/vlocalhost.py" &) ;;
esac
printf '\n   You can close this window.\n\n'
