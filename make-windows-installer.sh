#!/bin/sh
# Check if makensis is available
if ! command -v makensis >/dev/null 2>&1; then
  echo "Error: makensis is not installed or not in PATH." >&2
  exit 1
fi

# Run makensis on the NSIS script
makensis src/assembly/windows-installer.nsi

