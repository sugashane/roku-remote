#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_VENV="$(mktemp -d "${TMPDIR:-/tmp}/roku-remote-build.XXXXXX")"
SPEC_DIR="$ROOT_DIR/build/pyinstaller-spec"

cleanup() {
  rm -rf "$TEMP_VENV"
}

trap cleanup EXIT

echo "Creating isolated build environment..."
python3 -m venv "$TEMP_VENV"

echo "Installing build dependencies..."
"$TEMP_VENV/bin/pip" install --quiet --upgrade pip
(
  cd "$ROOT_DIR"
  "$TEMP_VENV/bin/pip" install --quiet ".[macos-app]"
)

echo "Building Roku Remote.app..."
(
  cd "$ROOT_DIR"
  mkdir -p "$SPEC_DIR"
  "$TEMP_VENV/bin/pyinstaller" \
    --noconfirm \
    --clean \
    --specpath "$SPEC_DIR" \
    --windowed \
    --name "Roku Remote" \
    --osx-bundle-identifier "com.shane.rokuremote" \
    roku_remote.py
)

echo
echo "Built app bundle:"
echo "  $ROOT_DIR/dist/Roku Remote.app"
echo
echo "To make it available in Spotlight, copy it into /Applications:"
echo "  cp -R \"$ROOT_DIR/dist/Roku Remote.app\" /Applications/"
