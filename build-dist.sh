#!/usr/bin/env bash
# Build and package dans-dv-upload for distribution (zip and tar.gz)
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$MODULE_DIR/dist"
PKG_NAME="dans-dv-upload"
PKG_VER="$(date +%Y%m%d)"
STAGE_DIR="$DIST_DIR/$PKG_NAME"

# Clean and prepare dist directory
rm -rf "$DIST_DIR"
mkdir -p "$STAGE_DIR"

# 1. Build the shiv package (assumes wheel is already built)
# You may need to adjust the wheel path if your build process is different
if ! command -v shiv >/dev/null 2>&1; then
  echo "shiv is not installed. Please install with: pip install shiv" >&2
  exit 1
fi

# Find the wheel (assumes only one wheel in dist/)
WHEEL_PATH=$(find "$MODULE_DIR/../../dist" "$MODULE_DIR/dist" -name 'dans_dv_upload-*.whl' 2>/dev/null | head -n1)
if [ -z "$WHEEL_PATH" ]; then
  echo "Could not find dans_dv_upload-*.whl. Please build the wheel first." >&2
  exit 1
fi

# Build the .pyz
shiv --output-file "$STAGE_DIR/dans-dv-upload.pyz" --python python3 -e dans_dv_upload.upload_file_to_dataset:main "$WHEEL_PATH"

# 2. Copy helper scripts, README, LICENSE
cp "$MODULE_DIR/dans-dv-upload-gui" "$STAGE_DIR/"
cp "$MODULE_DIR/dans-dv-upload-gui.bat" "$STAGE_DIR/"
cp "$MODULE_DIR/README.md" "$STAGE_DIR/"
cp "$MODULE_DIR/LICENSE" "$STAGE_DIR/"

# 3. Package as .zip and .tar.gz
cd "$DIST_DIR"
zip -r "${PKG_NAME}.zip" "$PKG_NAME"
tar czf "${PKG_NAME}.tar.gz" "$PKG_NAME"

# 4. Print result
cd "$MODULE_DIR"
echo "Distribution packages created in $DIST_DIR:"
echo "  - $DIST_DIR/${PKG_NAME}.zip"
echo "  - $DIST_DIR/${PKG_NAME}.tar.gz"

