Dim fso, scriptDir, pyzPath, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pyzPath = scriptDir & "\dans-dv-upload.pyz"
If fso.FileExists(pyzPath) Then
    cmd = "python """ & pyzPath & """ --gui"
    Set WshShell = CreateObject("WScript.Shell")
    WshShell.Run cmd, 0, False
Else
    MsgBox "Could not find dans-dv-upload.pyz in " & scriptDir & ". Please ensure it is present.", vbCritical
End If
