@echo off
REM Portable helper script to start dans-dv-upload in GUI mode (Windows)

set DIR=%~dp0
if exist "%DIR%dans-dv-upload.pyz" (
    python "%DIR%dans-dv-upload.pyz" --gui
    exit /b %ERRORLEVEL%
)

echo Could not find dans-dv-upload.pyz in %DIR%. Please ensure it is present.
exit /b 1
