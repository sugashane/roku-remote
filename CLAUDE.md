# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
python roku_remote.py

# Install deps (dev)
pip install -e ".[macos-app]"

# Build macOS .app bundle (uses PyInstaller, isolated venv)
./build_macos_app.sh

# Copy built app to Applications
cp -R "dist/Roku Remote.app" /Applications/
```

No test suite exists.

## Architecture

Single-file PyQt6 desktop app (`roku_remote.py`). Wraps the `roku` library (ECP protocol over HTTP) with a GUI remote control.

**Key classes:**

- `RokuRemote(QWidget)` — main window. Owns all UI sections and the active `Roku` connection. `self.roku` is `None` when disconnected; all command methods guard with `ensure_connected()`.
- `DiscoveryWorker(QObject)` — runs `Roku.discover()` in a `QThread` to avoid blocking the UI. Emits `finished(devices)` or `failed(str)`.
- `DeviceRecord` — frozen dataclass holding device metadata (host, port, model, serial).

**UI sections** (built in `__init__` in order): device selector → navigation d-pad → text input → apps → TV controls → activity log.

**State flow:**
1. App starts → `refresh_devices()` fires discovery in background thread.
2. User selects device → `connect_to_device()` creates `Roku(host, port)`, fetches `device_info`, calls `load_apps()`.
3. Commands call `getattr(self.roku, command_name)()` dynamically (e.g. `self.roku.up()`).
4. `self.device_controls` list tracks all widgets that should be enabled only when connected; `update_device_controls()` iterates it.

**Persistence:** `QSettings("roku-remote", "roku-remote")` saves `last_device_host` so the previously used device is auto-selected after discovery.

**Favorites:** `populate_favorites()` ranks apps against `PREFERRED_APPS` list (first 6 matches shown as quick-launch buttons above the full app list).

**macOS app bundle:** `build_macos_app.sh` creates a fresh venv, installs `.[macos-app]` (adds PyInstaller), runs `pyinstaller --windowed`. Output: `dist/Roku Remote.app`.
