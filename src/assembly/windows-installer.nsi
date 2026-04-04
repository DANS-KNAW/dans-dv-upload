OutFile "../../target/dans-dv-upload.exe"
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\dans-dv-upload"

Page directory
Page instfiles

Section
  SetOutPath "$INSTDIR"
  File /r "dist\*"
  File /r "..\..\target\bin\*"
SectionEnd

