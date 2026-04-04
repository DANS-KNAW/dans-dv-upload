!include "MUI2.nsh"

OutFile "../../target/dans-dv-upload.exe"
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\dans-dv-upload"

!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "../../LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section
  SetOutPath "$INSTDIR"
  File /r "dist\*"
  File /r "..\..\target\bin\*"
  CreateShortcut "$DESKTOP\dans-dv-upload-gui.lnk" "$INSTDIR\dans-dv-upload-gui.vbs"
SectionEnd

