# dans-dv-upload: Portable Dataverse File Uploader

## Overview
This package provides a portable, cross-platform tool for uploading files to Dataverse, supporting both command-line and GUI modes.

## Contents
- `dans-dv-upload.pyz` — The self-contained Python executable (shiv package)
- `dans-dv-upload-gui` — Helper script for launching the GUI (Linux/macOS)
- `dans-dv-upload-gui.bat` — Helper script for launching the GUI (Windows)
- `README.md` — This file
- `LICENSE` — License information

## Requirements
- Python 3.7+
- `tkinter` (for GUI mode)
  - Linux: `sudo apt install python3-tk`
  - macOS: Included with standard Python installer
  - Windows: Included with standard Python installer

## Installation
1. Download and extract the appropriate package for your platform:
   - **Windows:** Use the `.zip` archive
   - **Linux/macOS:** Use the `.tar.gz` archive
2. Unpack the archive to a directory of your choice.
3. (Linux/macOS) Make the GUI script executable:
   ```sh
   chmod +x dans-dv-upload-gui
   ```

## Usage
### GUI Mode
- **Linux/macOS:**
  ```sh
  ./dans-dv-upload-gui
  ```
- **Windows:**
  Double-click `dans-dv-upload-gui.bat` or run:
  ```bat
  dans-dv-upload-gui.bat
  ```

### Command-Line Mode
- All platforms:
  ```sh
  python3 dans-dv-upload.pyz <doi> <file> [options]
  ```
  Use `--help` for options.

## Notes
- The helper scripts always run the `.pyz` in the same directory.
- Ensure Python 3 and tkinter are installed on your system.
- No installation is required; just unpack and run.

## Example Directory Layout
```
dans-dv-upload/
  dans-dv-upload.pyz
  dans-dv-upload-gui
  dans-dv-upload-gui.bat
  README.md
  LICENSE
```
