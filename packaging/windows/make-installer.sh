#!/bin/bash
#
# Build the Windows self-extracting installer for dans-dv-upload.
#
# This script is called from the module root directory.
#
# Prerequisites:
# - 7z (p7zip) must be installed.
# - packaging/windows/7zS.sfx must be present.
# - target/dist/dans-dv-upload must contain the distribution files.

set -e

SFX_FILE="packaging/windows/7z.sfx"
CONFIG_FILE="packaging/windows/config.txt"
DIST_DIR="target/dist/dans-dv-upload"
STAGING_DIR="target/windows-staging"
PAYLOAD_7Z="target/payload.7z"
INSTALLER_EXE="target/dans-dv-upload-windows-installer.exe"

echo "Checking for $SFX_FILE..."
if [ ! -f "$SFX_FILE" ]; then
    echo "$SFX_FILE missing. Windows installer build failed."
    exit 1
fi

echo "Building Windows installer..."
mkdir -p "$STAGING_DIR"
cp -r "$DIST_DIR"/* "$STAGING_DIR"/

# Create the .7z archive from the staging directory
# Use -y to overwrite existing archive if present
7z a -y "$PAYLOAD_7Z" ./"$STAGING_DIR"/*

# Concatenate SFX module, config file, and 7z archive to create the SFX installer
cat "$SFX_FILE" "$CONFIG_FILE" "$PAYLOAD_7Z" > "$INSTALLER_EXE"

echo "Windows installer created: $INSTALLER_EXE"
