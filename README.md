# Roku Remote

PyQt6 desktop GUI for controlling Roku devices on your local network.

Auto-discovers Roku players and TVs via SSDP. Supports navigation, text input, app launching, volume/input controls, and cross-device switching.

## Requirements

- Python 3.10+
- macOS (for the .app bundle; the Python script runs anywhere with PyQt6)

## Install & Run

### Run from source

```bash
pip install -e .
roku-remote
# or: python roku_remote.py
```

### macOS app bundle

Build a standalone `Roku Remote.app` (no Python installation required to run it):

```bash
./build_macos_app.sh
```

Then copy into Applications so it appears in Spotlight:

```bash
cp -R "dist/Roku Remote.app" /Applications/
```

The build script creates an isolated venv automatically — you do not need PyInstaller installed beforehand.

## Usage

1. Launch the app. It scans your network for Roku devices automatically.
2. Select a device from the dropdown.
3. Use the on-screen buttons or keyboard shortcuts to control it.

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Arrow keys | Navigate |
| Enter / Return | Select |
| Escape | Back |
| H | Home |

Shortcuts are suppressed when a text input field has focus so you can type normally.

### Text input

Type into the **Text Input & Search** box and press **Type Text** to send characters to the Roku (useful for login screens). **Roku Search** opens the Roku global search with the entered text.

### Apps

Quick-launch buttons show your top installed streaming apps. The full list below supports filtering by name; double-click or select and press **Launch** to open any app.
